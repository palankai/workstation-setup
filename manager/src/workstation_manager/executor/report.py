from datetime import datetime
from pathlib import Path

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
