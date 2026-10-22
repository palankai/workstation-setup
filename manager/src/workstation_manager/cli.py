import argparse
import os
import re
import sys
import threading
import urllib.request
import webbrowser
from pathlib import Path

from .core import CatalogError, ProfileError, Workspace, WorkspaceError
from .core.runs import RUNS, RunLog, list_runs, load_run
from .core.state import State, StateError, default_state_dir
from .executor.report import format_run, summary_line
from .executor.update import Executor, PlanError, format_plan, make_plan

UI_DIST = Path(__file__).resolve().parents[2] / "ui" / "dist"
HOST = "127.0.0.1"
PORT = 8765
# The repository this package lives in, used when the cwd isn't inside one
PACKAGE_ROOT = Path(__file__).resolve().parents[3]
MACHINE_CONFIG = Path.home() / ".workstation-setup-config"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="workstation-manager")
    parser.add_argument(
        "--root",
        type=Path,
        help="workstation-setup repository (default: discovered from cwd, then this package's)",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    serve = commands.add_parser("serve", help="run the selector web UI")
    serve.add_argument("--host", default=HOST)
    serve.add_argument("--port", type=int, default=PORT)
    serve.add_argument("--no-open", action="store_true", help="don't open the browser")
    serve.add_argument(
        "--report",
        nargs="?",
        const="latest",
        metavar="RUN",
        help="open on a run report (default: the latest run)",
    )
    serve.add_argument("--ui", type=Path, default=UI_DIST, help="built UI folder")

    selection = argparse.ArgumentParser(add_help=False)
    selection.add_argument(
        "query",
        nargs="*",
        help="application ids, #tag, kind:<kind>, is:<flag>; default: the whole profile",
    )
    selection.add_argument("--profile", help="default: $WORKSTATION or ~/.workstation-setup-config")
    selection.add_argument(
        "--force", action="store_true", help="allow applications the profile doesn't install"
    )
    selection.add_argument("--no-deps", action="store_true", help="skip dependencies")

    commands.add_parser(
        "plan", parents=[selection], help="show what update would run, without running it"
    )
    update = commands.add_parser(
        "update",
        parents=[selection],
        help="install and update applications",
        description="Without a query: brew update and upgrade, every application's steps, "
        "then brew cleanup. With a query: only the matching applications' steps.",
    )
    update.add_argument(
        "--no-brew", action="store_true", help="skip brew entirely, including Brewfile steps"
    )
    update.add_argument("--fail-fast", action="store_true", help="stop at the first failure")
    update.add_argument(
        "--open", action="store_true", help="open the run report in the web UI afterwards"
    )

    once = commands.add_parser("once", help="once step records on this machine")
    once_commands = once.add_subparsers(dest="once_command", required=True)
    once_commands.add_parser("list", help="show recorded once steps")
    reset = once_commands.add_parser("reset", help="forget once steps so they run again")
    reset.add_argument("id")
    reset.add_argument("step", nargs="?", help="default: every once step of the application")

    runs = commands.add_parser("runs", help="list recent update runs")
    runs.add_argument("-n", "--limit", type=int, default=20)

    report = commands.add_parser("report", help="show a run's results and failed output")
    report.add_argument("run", nargs="?", help="run id (default: the latest)")
    report.add_argument("--app", help="only this application's steps")
    report.add_argument("--output", action="store_true", help="full output of every step shown")

    command = sys.argv[1:] if argv is None else argv
    args = parser.parse_args(command)
    try:
        workspace = discover(args.root)
        state_dir = default_state_dir()
        if args.command == "serve":
            path = f"/?run={args.report}" if args.report else "/"
            run_server(workspace, args.host, args.port, args.ui, None if args.no_open else path)
        elif args.command in ("plan", "update"):
            sys.exit(run_update(workspace, state_dir, args, command))
        elif args.command == "once":
            run_once(workspace, State(state_dir), args)
        elif args.command == "runs":
            for run in list_runs(state_dir)[: args.limit]:
                print(summary_line(run))
        elif args.command == "report":
            run_report(state_dir, args)
    except (WorkspaceError, CatalogError, ProfileError, StateError, PlanError) as e:
        sys.exit(f"error: {e}")
    except KeyboardInterrupt:
        sys.exit(130)


def discover(root: Path | None) -> Workspace:
    try:
        return Workspace.discover(root)
    except WorkspaceError:
        if root is None:
            return Workspace.discover(PACKAGE_ROOT)
        raise


def resolve_profile(name: str | None) -> str:
    if name or (name := os.environ.get("WORKSTATION")):
        return name
    if MACHINE_CONFIG.is_file():
        match = re.search(r"^export WORKSTATION=(\S+)", MACHINE_CONFIG.read_text(), re.M)
        if match:
            return match.group(1).strip("\"'")
    raise ProfileError(f"No profile: pass --profile, set $WORKSTATION or {MACHINE_CONFIG}")


def run_update(
    workspace: Workspace, state_dir: Path, args: argparse.Namespace, command: list[str]
) -> int:
    state = State(state_dir)
    profile = resolve_profile(args.profile)
    plan = make_plan(workspace, state, profile, args.query, args.force, args.no_deps)
    if args.command == "plan":
        print(format_plan(plan))
        return 0
    log = RunLog(state_dir / RUNS, profile, command)
    status = Executor(state, log, brew=not args.no_brew, fail_fast=args.fail_fast).execute(plan)
    print()
    print(format_run(log.data, state_dir, problems_only=True))
    if args.open:
        show_report(workspace, log.id)
    return 0 if status == "ok" else 1


def show_report(workspace: Workspace, run_id: str) -> None:
    """Opens the report in a running UI, or serves one until Ctrl-C."""
    url = f"http://{HOST}:{PORT}"
    path = f"/?run={run_id}"
    try:
        urllib.request.urlopen(f"{url}/api/settings", timeout=1).close()
    except OSError:
        print(f"\nServing the report on {url}; Ctrl-C to stop")
        run_server(workspace, HOST, PORT, UI_DIST, path)
    else:
        webbrowser.open(url + path)


def run_once(workspace: Workspace, state: State, args: argparse.Namespace) -> None:
    if args.once_command == "list":
        for app, steps in sorted(state.once.items()):
            for step, record in sorted(steps.items()):
                print(f"{app:<30} {step:<16} {record.at}  {record.sha256[:12]}")
    else:
        workspace.catalog().get(args.id)
        removed = state.reset_once(args.id, args.step)
        print(f"Reset: {', '.join(removed)}" if removed else "Nothing recorded")


def run_report(state_dir: Path, args: argparse.Namespace) -> None:
    if args.run:
        run = load_run(state_dir, args.run)
    else:
        run = next(iter(list_runs(state_dir)), None)
    if run is None:
        sys.exit("error: no such run")
    print(format_run(run, state_dir, args.app, args.output))


def run_server(
    workspace: Workspace, host: str, port: int, ui: Path, open_path: str | None
) -> None:
    try:
        import uvicorn

        from .server.app import create_app
    except ImportError:
        sys.exit("error: the web UI needs the server extra: uv run --extra server workstation-manager serve")

    if not (ui / "index.html").is_file():
        print(f"warning: no built UI in {ui}, serving the API only", file=sys.stderr)
        print("         build it with: pnpm --dir ui build", file=sys.stderr)
    url = f"http://{host}:{port}"
    print(f"Workspace: {workspace.root}\nServing:   {url}")
    if open_path is not None:
        threading.Timer(1.0, webbrowser.open, [url + open_path]).start()
    uvicorn.run(create_app(workspace, ui), host=host, port=port, log_level="warning")
