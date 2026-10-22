"""Run logs: runs/<id>/run.json plus one output file per executed step."""

import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

from .state import now

RUNS = "runs"
RUN_FILE = "run.json"

StepStatus = Literal["ok", "failed", "skipped"]
RunStatus = Literal["running", "ok", "failed", "interrupted"]

ANSI = re.compile(r"\x1b(\[[0-9;?]*[ -/]*[@-~]|\][^\x07\x1b]*(\x07|\x1b\\)|[@-Z\\-_])")


@dataclass
class StepResult:
    # None for run-wide steps such as `brew update`
    app: str | None
    step: str
    kind: str
    status: StepStatus
    started: str
    finished: str
    exit_code: int | None = None
    # Output file name inside the run folder
    output: str | None = None
    reason: str | None = None


class RunLog:
    """Rewrites run.json after every step, so an interrupted run can still be read back."""

    def __init__(self, runs_dir: Path, profile: str, command: list[str]):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        id, suffix = stamp, 1
        while (runs_dir / id).exists():
            suffix += 1
            id = f"{stamp}-{suffix}"
        self.id = id
        self.directory = runs_dir / id
        self.directory.mkdir(parents=True)
        self.data = {
            "id": id,
            "profile": profile,
            "command": command,
            "started": now(),
            "finished": None,
            "status": "running",
            "steps": [],
            # Applications whose uninstall steps all succeeded
            "uninstalled": [],
        }
        self._write()

    def output_path(self, app: str | None, step: str) -> Path:
        name = f"{len(self.data['steps']) + 1:03d}-{app or 'run'}-{step}"
        return self.directory / (re.sub(r"[^A-Za-z0-9._-]+", "_", name) + ".log")

    def add(self, result: StepResult) -> None:
        self.data["steps"].append(asdict(result))
        self._write()

    def add_uninstalled(self, app: str) -> None:
        self.data["uninstalled"].append(app)
        self._write()

    def finish(self, status: RunStatus) -> None:
        self.data["finished"] = now()
        self.data["status"] = status
        self._write()

    def _write(self) -> None:
        temporary = self.directory / f"{RUN_FILE}.tmp"
        temporary.write_text(json.dumps(self.data, indent=2))
        os.replace(temporary, self.directory / RUN_FILE)


def list_runs(state_dir: Path) -> list[dict]:
    """Every run, latest first."""
    runs_dir = state_dir / RUNS
    if not runs_dir.is_dir():
        return []
    runs = []
    for run_file in runs_dir.glob(f"*/{RUN_FILE}"):
        try:
            runs.append(json.loads(run_file.read_text()))
        except (OSError, json.JSONDecodeError):
            continue
    return sorted(runs, key=lambda run: (run["started"], run["id"]), reverse=True)


def uninstalled(state_dir: Path, profile: str, ids: list[str]) -> list[str]:
    """Those of ids whose latest uninstall attempt in the profile's runs succeeded."""
    result = []
    for id in ids:
        for run in list_runs(state_dir):
            if run["profile"] != profile:
                continue
            if id in run.get("uninstalled", ()):
                result.append(id)
                break
            if any(s["app"] == id and s["kind"] == "uninstall" for s in run["steps"]):
                break
    return result


def load_run(state_dir: Path, id: str) -> dict | None:
    run_file = state_dir / RUNS / id / RUN_FILE
    if "/" in id or id.startswith(".") or not run_file.is_file():
        return None
    return json.loads(run_file.read_text())


def output_file(state_dir: Path, id: str, name: str) -> Path | None:
    run_dir = (state_dir / RUNS / id).resolve()
    file = (run_dir / name).resolve()
    if file.parent != run_dir or not file.is_file() or not file.name.endswith(".log"):
        return None
    return file


def clean_output(raw: bytes) -> str:
    """Terminal output as plain text: no colours, progress bars collapsed to their last state."""
    text = ANSI.sub("", raw.decode(errors="replace"))
    lines = text.replace("\r\n", "\n").split("\n")
    return "\n".join(line.rstrip("\r").rsplit("\r", 1)[-1] for line in lines)
