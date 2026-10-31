import argparse
import os
import re
import sys
import threading
import urllib.request
import webbrowser
from collections.abc import Collection
from pathlib import Path

from .core import CatalogError, ProfileError, UninstallError, Workspace, WorkspaceError, set_flag
from .core.runs import RUNS, RunLog, list_runs, load_run, prune_runs, uninstalled
from .core.state import State, StateError, default_state_dir
from .core.query import search
from .executor.report import format_run, format_search, summary_line, write_html_report
from .executor.update import Executor, Plan, PlanError, format_plan, make_plan
from .generator import DRY_RUN, OVERWRITE
from .scaffold import scaffold_uninstall
from .migrate import migrate

UI_DIST = Path(__file__).resolve().parents[2] / "ui" / "dist"
# The static run report's template, built from the UI's RunReport (ui/report.html)
REPORT_TEMPLATE = UI_DIST / "report.html"
# ws cleanup: runs older than this many days go, except the latest few
CLEANUP_DAYS = 30
CLEANUP_KEEP = 5
HOST = "127.0.0.1"
PORT = 8765
# The repository this package lives in, used when the cwd isn't inside one
PACKAGE_ROOT = Path(__file__).resolve().parents[3]
MACHINE_CONFIG = Path.home() / ".workstation-setup-config"
# Command → (flag, value), the CLI side of the UI's toggle buttons
FLAG_COMMANDS = {
    "deprecate": ("deprecated", True),
    "undeprecate": ("deprecated", False),
    "archive": ("archived", True),
    "unarchive": ("archived", False),
}


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
        help="application ids, #tag, kind:<kind>, is:<flag>; default: the whole profile, "
        "with every uninstall it marks",
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
        description="Without a query: brew update, uninstalls, brew upgrade, every application's "
        "steps, then brew autoremove and cleanup. With a query: only the matching applications' "
        "steps, or uninstall steps for those marked for uninstall.",
    )
    update.add_argument(
        "--no-brew", action="store_true", help="skip brew entirely, including Brewfile steps"
    )
    update.add_argument(
        "--brew-only",
        action="store_true",
        help="only brew update, upgrade and cleanup; no application steps",
    )
    update.add_argument("--fail-fast", action="store_true", help="stop at the first failure")
    update.add_argument(
        "--open", action="store_true", help="open the run report in the web UI afterwards"
    )
    update.add_argument(
        "--cleanup",
        action="store_true",
        help=f"afterwards, delete runs older than {CLEANUP_DAYS} days except the latest "
        f"{CLEANUP_KEEP} (like ws cleanup)",
    )

    generate = commands.add_parser(
        "generate",
        parents=[selection],
        help="write the files installed applications generate (their *generate.py steps)",
        description="Runs only the *generate.py steps, which update also runs. A generated file "
        "carries a header with a hash; one edited since, hand-written or a symlink is refused.",
    )
    generate.add_argument("-n", "--dry-run", action="store_true", help="only show what it would write")
    generate.add_argument(
        "--overwrite",
        action="store_true",
        help="replace edited and hand-written files too, keeping each as <name>.bak",
    )

    search = commands.add_parser(
        "search",
        help="list applications, one line each",
        description="Every word must appear in the id, name, description or tags; "
        "#tag, kind:<kind> and is:<flag> filter. ✓ marks what the profile installs, "
        "✗ what it uninstalls (is:uninstall).",
    )
    search.add_argument("query", nargs="*")
    search.add_argument("--profile", help="default: $WORKSTATION or ~/.workstation-setup-config")

    profile_option = argparse.ArgumentParser(add_help=False)
    profile_option.add_argument("ids", nargs="+", metavar="id")
    profile_option.add_argument(
        "--profile", help="default: $WORKSTATION or ~/.workstation-setup-config"
    )
    commands.add_parser(
        "select", parents=[profile_option], help="add applications to the profile"
    )
    commands.add_parser(
        "deselect",
        aliases=["unselect"],
        parents=[profile_option],
        help="remove applications from the profile",
    )
    uninstall = commands.add_parser(
        "uninstall",
        help="mark applications for uninstall: deselects them, and every update uninstalls them",
        description="Marked applications stay on the profile's uninstall list until cleared, "
        "so every machine on the profile uninstalls them. select or keep takes them off.",
    )
    uninstall.add_argument("ids", nargs="*", metavar="id")
    uninstall.add_argument("--profile", help="default: $WORKSTATION or ~/.workstation-setup-config")
    uninstall.add_argument(
        "--clear",
        action="store_true",
        help="take off the list every application whose last uninstall succeeded",
    )
    commands.add_parser(
        "keep",
        parents=[profile_option],
        help="take applications off the uninstall list, without selecting them",
    )
    application_ids = argparse.ArgumentParser(add_help=False)
    application_ids.add_argument("ids", nargs="+", metavar="id")
    for name, (flag, value) in FLAG_COMMANDS.items():
        commands.add_parser(
            name,
            parents=[application_ids],
            help=f"{'set' if value else 'clear'} '{flag}' in the applications' frontmatter",
        )

    once = commands.add_parser("once", help="once step records on this machine")
    once_commands = once.add_subparsers(dest="once_command", required=True)
    once_commands.add_parser("list", help="show recorded once steps")
    reset = once_commands.add_parser("reset", help="forget once steps so they run again")
    reset.add_argument("id")
    reset.add_argument("step", nargs="?", help="default: every once step of the application")

    migrate_command = commands.add_parser(
        "migrate",
        help="move this machine from the old setup: once steps, links into components/",
        description="Records once steps the old setup already ran (targets/<profile>/.once), "
        "points links into old component folders at the applications, and undoes `ln -sf` "
        "nesting. Safe to run again, and on machines without the old setup.",
    )
    migrate_command.add_argument("--profile", help="default: $WORKSTATION or ~/.workstation-setup-config")
    migrate_command.add_argument("-n", "--dry-run", action="store_true", help="only show what it would do")

    scaffold = commands.add_parser(
        "scaffold-uninstall",
        help="write uninstall steps for applications installed by Brewfiles alone",
        description="Writes 90-uninstall.sh into applications whose only steps are Brewfiles of brew, "
        "cask and tap lines: it uninstalls their formulae and casks (not taps). Regenerates files it "
        "wrote before; leaves hand-written uninstall steps and packages shared with other "
        "applications alone.",
    )
    scaffold.add_argument("ids", nargs="*", metavar="ID", help="default: every application")
    scaffold.add_argument("-n", "--dry-run", action="store_true", help="only show what it would do")

    runs = commands.add_parser("runs", help="list recent update runs")
    runs.add_argument("-n", "--limit", type=int, default=20)

    report = commands.add_parser("report", help="show a run's results and failed output")
    report.add_argument("run", nargs="?", help="run id (default: the latest)")
    report.add_argument("--app", help="only this application's steps")
    report.add_argument("--output", action="store_true", help="full output of every step shown")
    report.add_argument(
        "--html",
        action="store_true",
        help="(re)write the run's static HTML report and print its location instead",
    )

    cleanup = commands.add_parser(
        "cleanup",
        help="delete old runs",
        description="Deletes runs older than --older-than days, but never the latest --keep runs: "
        "with the defaults, a run goes once it's over 30 days old and five newer ones exist. "
        "--keep 0 deletes by age alone, --older-than 0 keeps just the latest --keep.",
    )
    cleanup.add_argument(
        "--keep",
        type=int,
        default=CLEANUP_KEEP,
        metavar="N",
        help=f"always keep the latest N runs (default: {CLEANUP_KEEP})",
    )
    cleanup.add_argument(
        "--older-than",
        type=int,
        default=CLEANUP_DAYS,
        metavar="DAYS",
        help=f"delete runs started more than DAYS days ago (default: {CLEANUP_DAYS})",
    )
    cleanup.add_argument("-n", "--dry-run", action="store_true", help="only show what it would delete")

    command = sys.argv[1:] if argv is None else argv
    args = parser.parse_args(command)
    try:
        workspace = discover(args.root)
        state_dir = default_state_dir()
        if args.command == "serve":
            path = f"/?run={args.report}" if args.report else "/"
            run_server(workspace, args.host, args.port, args.ui, None if args.no_open else path)
        elif args.command in ("plan", "update", "generate"):
            sys.exit(run_update(workspace, state_dir, args, command))
        elif args.command == "search":
            run_search(workspace, args)
        elif args.command in ("select", "deselect", "unselect"):
            run_select(workspace, args, select=args.command == "select")
        elif args.command == "uninstall":
            run_uninstall(workspace, state_dir, args)
        elif args.command == "keep":
            run_keep(workspace, args)
        elif args.command in FLAG_COMMANDS:
            run_flag(workspace, args)
        elif args.command == "once":
            run_once(workspace, State(state_dir), args)
        elif args.command == "migrate":
            profile = resolve_profile(args.profile)
            lines = migrate(workspace, State(state_dir), profile, Path.home(), args.dry_run)
            print("\n".join(lines) if lines else "Nothing to migrate")
        elif args.command == "scaffold-uninstall":
            lines = scaffold_uninstall(workspace.catalog(), args.ids, args.dry_run)
            print("\n".join(lines) if lines else "Nothing to scaffold")
        elif args.command == "runs":
            for run in list_runs(state_dir)[: args.limit]:
                print(summary_line(run))
        elif args.command == "report":
            run_report(workspace, state_dir, args)
        elif args.command == "cleanup":
            run_cleanup(state_dir, args.keep, args.older_than, args.dry_run)
    except (WorkspaceError, CatalogError, ProfileError, StateError, PlanError, UninstallError) as e:
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
    generate = args.command == "generate"
    if getattr(args, "brew_only", False):
        if args.query or args.no_brew:
            raise PlanError("--brew-only can't be combined with a query or --no-brew")
        plan = Plan(profile, [], full=True)
    else:
        only = "generate" if generate else None
        plan = make_plan(workspace, state, profile, args.query, args.force, args.no_deps, only)
    if args.command == "plan":
        print(format_plan(plan))
        return 0
    log = RunLog(state_dir / RUNS, profile, command)
    if generate:
        env = {DRY_RUN: "1"} if args.dry_run else {}
        env |= {OVERWRITE: "1"} if args.overwrite else {}
        executor = Executor(workspace.root, state, log, brew=False, env=env)
    else:
        executor = Executor(
            workspace.root, state, log, brew=not args.no_brew, fail_fast=args.fail_fast
        )
    try:
        status = executor.execute(plan)
    except KeyboardInterrupt:
        print("\nInterrupted")
        print(format_run(log.data, state_dir, problems_only=True))
        print_html_report(workspace, state_dir, log.data)
        return 130
    print()
    print(format_run(log.data, state_dir, problems_only=True))
    print_html_report(workspace, state_dir, log.data)
    if getattr(args, "cleanup", False):
        run_cleanup(state_dir, CLEANUP_KEEP, CLEANUP_DAYS, protect=[log.id])
    if getattr(args, "open", False):
        show_report(workspace, log.id)
    elif done := log.data["uninstalled"]:
        offer_clear(workspace, profile, done)
    return 0 if status == "ok" else 1


def print_html_report(workspace: Workspace, state_dir: Path, run: dict) -> None:
    if not REPORT_TEMPLATE.is_file():
        print(f"No HTML report: no built UI in {UI_DIST} (pnpm --dir ui build)", file=sys.stderr)
        return
    names = {application.id: application.name for application in workspace.catalog()}
    path = write_html_report(run, state_dir, REPORT_TEMPLATE, names)
    print(f"Report: {path.as_uri()}")


def run_cleanup(
    state_dir: Path, keep: int, days: int, dry_run: bool = False, protect: Collection[str] = ()
) -> None:
    if keep < 0 or days < 0:
        sys.exit("error: --keep and --older-than can't be negative")
    removed = prune_runs(state_dir, keep, days, protect, dry_run)
    if not removed:
        print("No runs to clean up")
        return
    runs = f"{len(removed)} run{'s' if len(removed) != 1 else ''}"
    print(f"{'Would delete' if dry_run else 'Deleted'} {runs}: {', '.join(removed)}")


def offer_clear(workspace: Workspace, profile: str, ids: list[str]) -> None:
    if not sys.stdin.isatty():
        print("Take them off the uninstall list with: ws uninstall --clear")
        return
    try:
        answer = input(f"Take {', '.join(ids)} off the uninstall list? [y/N] ")
    except EOFError:
        answer = ""
    if answer.strip().lower() in ("y", "yes"):
        workspace.keep(profile, ids)
        print(f"Cleared from the uninstall list: {', '.join(ids)}")


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


def run_search(workspace: Workspace, args: argparse.Namespace) -> None:
    catalog = workspace.catalog()
    try:
        state = workspace.state(resolve_profile(args.profile), catalog)
        installed, marked = set(state.install_order), set(state.uninstall)
    except ProfileError:
        if args.profile:
            raise
        installed, marked = set(), set()
    found = search(catalog, args.query, keep=installed | marked, uninstall=marked)
    lines = format_search(found, installed, sys.stdout.isatty(), marked)
    print("\n".join(lines) if lines else "No applications match.")


def run_select(workspace: Workspace, args: argparse.Namespace, select: bool) -> None:
    profile = resolve_profile(args.profile)
    catalog = workspace.catalog()
    ids = list(dict.fromkeys(catalog.get(id).id for id in args.ids))
    before = workspace.state(profile, catalog)
    current = before.selected
    if select:
        fundamentals = [id for id in ids if catalog.get(id).fundamental]
        unchanged = [id for id in ids if id in current]
        changed = [id for id in ids if id not in current and id not in fundamentals]
        selection = [*current, *changed]
    else:
        fundamentals = []
        unchanged = [id for id in ids if id not in current]
        changed = [id for id in ids if id in current]
        selection = [id for id in current if id not in changed]
    if changed:
        workspace.update_selection(profile, selection)
        print(f"{'Selected' if select else 'Deselected'} in {profile}: {', '.join(changed)}")
    if unchanged:
        print(f"Already {'selected' if select else 'not selected'}: {', '.join(unchanged)}")
    if fundamentals:
        print(f"Always installed (fundamental): {', '.join(fundamentals)}")
    if select and changed:
        marked = workspace.state(profile).uninstall
        if kept := [id for id in before.uninstall if id not in marked]:
            print(f"No longer marked for uninstall: {', '.join(kept)}")
    if not select:
        installed = set(workspace.state(profile).install_order)
        if still := [id for id in ids if id in installed]:
            print(f"Still installed as a fundamental or dependency: {', '.join(still)}")


def run_uninstall(workspace: Workspace, state_dir: Path, args: argparse.Namespace) -> None:
    profile = resolve_profile(args.profile)
    if args.clear:
        if args.ids:
            raise UninstallError("--clear takes no ids; ws keep ID takes single applications off")
        marked = workspace.state(profile).uninstall
        if done := uninstalled(state_dir, profile, marked):
            workspace.keep(profile, done)
            print(f"Cleared from the uninstall list: {', '.join(done)}")
        if pending := [id for id in marked if id not in done]:
            print(f"Still marked, not uninstalled yet: {', '.join(pending)}")
        if not marked:
            print("Nothing marked for uninstall")
        return
    if not args.ids:
        raise UninstallError("Give application ids, or --clear")
    catalog = workspace.catalog()
    ids = list(dict.fromkeys(catalog.get(id).id for id in args.ids))
    before = workspace.state(profile, catalog)
    workspace.mark_uninstall(profile, ids)
    if changed := [id for id in ids if id not in before.uninstall]:
        print(f"Marked for uninstall in {profile}: {', '.join(changed)}")
    if unchanged := [id for id in ids if id in before.uninstall]:
        print(f"Already marked: {', '.join(unchanged)}")
    if deselected := [id for id in ids if id in before.selected]:
        print(f"Deselected: {', '.join(deselected)}")


def run_keep(workspace: Workspace, args: argparse.Namespace) -> None:
    profile = resolve_profile(args.profile)
    catalog = workspace.catalog()
    ids = list(dict.fromkeys(catalog.get(id).id for id in args.ids))
    marked = workspace.state(profile, catalog).uninstall
    if changed := [id for id in ids if id in marked]:
        workspace.keep(profile, changed)
        print(f"No longer marked for uninstall in {profile}: {', '.join(changed)}")
    if unchanged := [id for id in ids if id not in marked]:
        print(f"Not marked for uninstall: {', '.join(unchanged)}")


def run_flag(workspace: Workspace, args: argparse.Namespace) -> None:
    flag, value = FLAG_COMMANDS[args.command]
    catalog = workspace.catalog()
    applications = [catalog.get(id) for id in dict.fromkeys(args.ids)]
    changed = [a.id for a in applications if getattr(a, flag) != value]
    for application in applications:
        if application.id in changed:
            set_flag(application.path / "README.md", flag, value)
    if changed:
        print(f"{'Set' if value else 'Cleared'} {flag}: {', '.join(changed)}")
    if unchanged := [a.id for a in applications if a.id not in changed]:
        print(f"Already {'' if value else 'not '}{flag}: {', '.join(unchanged)}")


def run_once(workspace: Workspace, state: State, args: argparse.Namespace) -> None:
    if args.once_command == "list":
        for app, steps in sorted(state.once.items()):
            for step, record in sorted(steps.items()):
                print(f"{app:<30} {step:<16} {record.at}  {record.sha256[:12]}")
    else:
        workspace.catalog().get(args.id)
        removed = state.reset_once(args.id, args.step)
        print(f"Reset: {', '.join(removed)}" if removed else "Nothing recorded")


def run_report(workspace: Workspace, state_dir: Path, args: argparse.Namespace) -> None:
    if args.run:
        run = load_run(state_dir, args.run)
    else:
        run = next(iter(list_runs(state_dir)), None)
    if run is None:
        sys.exit("error: no such run")
    if args.html:
        print_html_report(workspace, state_dir, run)
    else:
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
    try:
        machine_profile = resolve_profile(None)
    except ProfileError:
        machine_profile = None
    uvicorn.run(create_app(workspace, ui, machine_profile=machine_profile), host=host, port=port, log_level="warning")
