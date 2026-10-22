import hashlib
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from ruamel.yaml import YAML, YAMLError

STATE_FILE = "state.yaml"


class StateError(Exception):
    pass


def default_state_dir() -> Path:
    base = os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state"
    return Path(base) / "workstation-setup"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


@dataclass(frozen=True)
class OnceRecord:
    at: str
    sha256: str


class State:
    """Per-machine state, kept outside the repository so a fresh install starts clean."""

    def __init__(self, directory: Path):
        self.directory = directory
        self.path = directory / STATE_FILE
        self.once: dict[str, dict[str, OnceRecord]] = {}
        if self.path.is_file():
            self._load()

    def _load(self) -> None:
        try:
            data = YAML(typ="safe").load(self.path.read_text()) or {}
        except YAMLError as e:
            raise StateError(f"{self.path}: invalid YAML: {e}") from None
        for app, steps in (data.get("once") or {}).items():
            self.once[app] = {
                step: OnceRecord(str(record["at"]), str(record["sha256"]))
                for step, record in steps.items()
            }

    def once_record(self, app: str, step: str) -> OnceRecord | None:
        return self.once.get(app, {}).get(step)

    def record_once(self, app: str, step: str, sha256: str, at: str | None = None) -> None:
        self.once.setdefault(app, {})[step] = OnceRecord(at or now(), sha256)
        self.save()

    def reset_once(self, app: str, step: str | None = None) -> list[str]:
        steps = self.once.get(app, {})
        removed = [s for s in steps if step in (None, s)]
        for s in removed:
            del steps[s]
        if not steps:
            self.once.pop(app, None)
        self.save()
        return removed

    def save(self) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        data = {
            "once": {
                app: {
                    step: {"at": r.at, "sha256": r.sha256}
                    for step, r in sorted(steps.items())
                }
                for app, steps in sorted(self.once.items())
            }
        }
        temporary = self.path.with_suffix(".tmp")
        yaml = YAML()
        yaml.default_flow_style = False
        with temporary.open("w") as f:
            yaml.dump(data, f)
        os.replace(temporary, self.path)
