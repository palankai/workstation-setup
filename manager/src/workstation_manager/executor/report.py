import shutil
from datetime import datetime
from pathlib import Path

from ..core import Application

from ..core.runs import RUNS, clean_output

ICONS = {"ok": "✓", "failed": "✗", "skipped": "-"}


def duration(start: str, end: str | None) -> str:
    if not end:
        return "unfinished"
    seconds = int((datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds())
    return f"{seconds // 60}m {seconds % 60}s" if seconds >= 60 else f"{seconds}s"


def step_label(step: dict) -> str:
    if step["app"] is None:
        return step["step"]
    if step["kind"] == "app":
        return step["app"]
    return f"{step['app']} {step['step']}"


def summary_line(run: dict) -> str:
    counts = {status: 0 for status in ICONS}
    for step in run["steps"]:
        counts[step["status"]] += 1
    return (
        f"{run['id']}  {run['status']:<11} {run['profile']:<10} "
        f"✓{counts['ok']} ✗{counts['failed']} -{counts['skipped']}  "
        f"{' '.join(run['command']) or '(all)'}"
    )


def format_run(
    run: dict,
    state_dir: Path,
    app: str | None = None,
    output: bool = False,
    problems_only: bool = False,
    tail: int = 30,
) -> str:
    """Steps (or only failed and skipped ones), then the output of failed steps
    (or of every shown step with output=True)."""
    steps = [s for s in run["steps"] if app in (None, s["app"])]
    counts = {status: sum(s["status"] == status for s in steps) for status in ICONS}
    lines = [
        f"Run {run['id']} · profile {run['profile']} · {run['status']} · "
        f"{run['started']} ({duration(run['started'], run['finished'])})",
        f"Command: {' '.join(run['command']) or '(all)'}",
        f"Steps: {counts['ok']} ok, {counts['failed']} failed, {counts['skipped']} skipped",
        "",
    ]
    if problems_only:
        steps = [s for s in steps if s["status"] != "ok"]
    for step in steps:
        line = f"  {ICONS[step['status']]} {step_label(step)}"
        if step["status"] == "failed" and step["exit_code"] is not None:
            line += f" (exit {step['exit_code']})"
        if step["reason"]:
            line += f": {step['reason']}"
        lines.append(line)

    for step in steps:
        if not step["output"] or not (output or step["status"] == "failed"):
            continue
        file = state_dir / RUNS / run["id"] / step["output"]
        text = clean_output(file.read_bytes()).rstrip("\n") if file.is_file() else ""
        shown = text.splitlines() if output else text.splitlines()[-tail:]
        lines += ["", f"--- {step_label(step)} ---", *shown]

    lines += ["", f"Logs: {state_dir / RUNS / run['id']}"]
    return "\n".join(lines)


def short_description(application: Application) -> str:
    """Descriptions start with the name for search; drop it on a line that shows the id."""
    prefix = f"{application.name}, "
    rest = application.description.removeprefix(prefix)
    return rest[:1].upper() + rest[1:] if rest != application.description else rest


def format_search(apps: list[Application], installed: set[str], color: bool) -> list[str]:
    """One line per application; the description is cut to fit the terminal."""
    width = shutil.get_terminal_size().columns
    id_width = max((len(a.id) for a in apps), default=0)
    kind_width = max((len(a.kind) for a in apps), default=0)

    def paint(text: str, code: str) -> str:
        return f"\x1b[{code}m{text}\x1b[0m" if color else text

    lines = []
    for a in apps:
        mark = "✓" if a.id in installed else " "
        labels = [flag for flag in ("deprecated", "archived", "trial") if getattr(a, flag)]
        tags = [f"#{tag}" for tag in a.tags]
        suffix = " ".join(labels + tags)
        room = width - len(f"{mark} {a.id:<{id_width}}  {a.kind:<{kind_width}}  ")
        room -= len(suffix) + 2 if suffix else 0
        description = short_description(a)
        if len(description) > room:
            description = description[: room - 1] + "…" if room > 1 else ""
        line = (
            f"{paint(mark, '32')} {paint(f'{a.id:<{id_width}}', '1')}  "
            f"{paint(f'{a.kind:<{kind_width}}', '2')}  {description}"
        )
        if suffix:
            line += "  " + " ".join([paint(l, "33") for l in labels] + [paint(t, "36") for t in tags])
        lines.append(line)
    return lines
