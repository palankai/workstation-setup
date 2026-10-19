import argparse
import sys
import threading
import webbrowser
from pathlib import Path

from .core import Workspace, WorkspaceError

UI_DIST = Path(__file__).resolve().parents[2] / "ui" / "dist"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="workstation-manager")
    parser.add_argument(
        "--root",
        type=Path,
        help="workstation-setup repository (default: discovered from cwd)",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    serve = commands.add_parser("serve", help="run the selector web UI")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--open", action="store_true", help="open the browser")
    serve.add_argument("--ui", type=Path, default=UI_DIST, help="built UI folder")

    args = parser.parse_args(argv)
    try:
        workspace = Workspace.discover(args.root)
    except WorkspaceError as e:
        sys.exit(f"error: {e}")

    if args.command == "serve":
        run_server(workspace, args.host, args.port, args.ui, args.open)


def run_server(
    workspace: Workspace, host: str, port: int, ui: Path, open_browser: bool
) -> None:
    import uvicorn

    from .server.app import create_app

    if not (ui / "index.html").is_file():
        print(f"warning: no built UI in {ui}, serving the API only", file=sys.stderr)
        print("         build it with: pnpm --dir ui build", file=sys.stderr)
    url = f"http://{host}:{port}"
    print(f"Workspace: {workspace.root}\nServing:   {url}")
    if open_browser:
        threading.Timer(1.0, webbrowser.open, [url]).start()
    uvicorn.run(create_app(workspace, ui), host=host, port=port, log_level="warning")
