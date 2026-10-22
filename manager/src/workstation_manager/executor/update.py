import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ..core import Application, Step, Workspace
from ..core.query import parse_query, select
from ..core.runs import RunLog, RunStatus, StepResult
from ..core.state import State, file_sha256, now
from . import process

OnceStatus = Literal["pending", "done", "changed"]

BREW_BEFORE = (("brew update", ["brew", "update"]), ("brew upgrade", ["brew", "upgrade"]))
BREW_AFTER = (("brew cleanup", ["brew", "cleanup"]),)
BUNDLE = 'brew bundle check --file="$1" >/dev/null 2>&1 || brew bundle install --file="$1"'


class PlanError(Exception):
    pass


@dataclass(frozen=True)
class PlannedStep:
    step: Step
    # Only for once steps; "changed" means the script changed since it ran, and it's not rerun
    once: OnceStatus | None = None


@dataclass(frozen=True)
class PlannedApp:
    application: Application
    steps: tuple[PlannedStep, ...]


@dataclass(frozen=True)
class Plan:
    profile: str
    apps: list[PlannedApp]
    # The whole profile: brew update/upgrade/cleanup run around the applications
    full: bool


def make_plan(
    workspace: Workspace,
    state: State,
    profile: str,
    terms: list[str],
    force: bool = False,
    no_deps: bool = False,
) -> Plan:
    """Applications the profile installs, narrowed by terms; dependencies are included
    unless no_deps, and applications outside the profile only with force."""
    catalog = workspace.catalog()
    install = workspace.state(profile, catalog).install_order
    if not terms:
        ids = install
    else:
        query = parse_query(terms)
        installed = set(install)
        matched = select(catalog, query, keep=installed)
        if not force:
            outside = [id for id in query.ids if id not in installed]
            if outside:
                raise PlanError(
                    f"Not installed by profile '{profile}': {', '.join(outside)} (use --force)"
                )
            matched = [id for id in matched if id in installed]
        ordered = catalog.resolve(matched)
        ids = [id for id in ordered if id in set(matched)] if no_deps else ordered
    return Plan(
        profile,
        [plan_application(catalog.get(id), state) for id in ids],
        full=not terms,
    )


def plan_application(application: Application, state: State) -> PlannedApp:
    steps = []
    for step in application.steps:
        once = None
        if step.kind == "once":
            record = state.once_record(application.id, step.file)
            if record is None:
                once = "pending"
            elif record.sha256 == file_sha256(application.path / step.file):
                once = "done"
            else:
                once = "changed"
        steps.append(PlannedStep(step, once))
    return PlannedApp(application, tuple(steps))


ONCE_NOTES = {
    "pending": "once",
    "done": "once, done",
    "changed": "once, changed since it ran; not rerun (`once reset` to rerun)",
}


def format_plan(plan: Plan) -> str:
    lines = [f"Profile {plan.profile} · {len(plan.apps)} applications"]
    if plan.full:
        lines.append("brew update, brew upgrade before; brew cleanup after")
    for planned in plan.apps:
        app = planned.application
        lines.append(f"==> {app.name} ({app.id})")
        for p in planned.steps:
            note = ONCE_NOTES[p.once] if p.once else p.step.kind
            lines.append(f"    {p.step.file:<16} {note}")
    return "\n".join(lines)


class Executor:
    def __init__(self, state: State, log: RunLog, brew: bool = True, fail_fast: bool = False):
        self.state = state
        self.log = log
        self.brew = brew
        self.fail_fast = fail_fast
        self.color = sys.stdout.isatty()

    def execute(self, plan: Plan) -> RunStatus:
        try:
            status = self._execute(plan)
        except KeyboardInterrupt:
            self.log.finish("interrupted")
            raise
        self.log.finish(status)
        return status

    def _execute(self, plan: Plan) -> RunStatus:
        # Failed applications, and those skipped because a dependency failed
        failed: set[str] = set()
        ok = True
        cwd = Path.home()
        if self.brew and plan.full:
            for name, argv in BREW_BEFORE:
                self._header(name)
                ok &= self._run(None, name, "brew", argv, cwd, {})

        for planned in plan.apps:
            app = planned.application
            blocked = [d for d in app.dependencies if d in failed]
            if blocked:
                failed.add(app.id)
                reason = f"dependency failed: {', '.join(blocked)}"
                self._header(f"{app.name} ({app.id})", f"skipped, {reason}")
                timestamp = now()
                self.log.add(
                    StepResult(app.id, "*", "app", "skipped", timestamp, timestamp, reason=reason)
                )
                continue
            if not self._run_application(planned):
                failed.add(app.id)
                if self.fail_fast:
                    break

        if self.brew and plan.full and not (self.fail_fast and failed):
            for name, argv in BREW_AFTER:
                self._header(name)
                ok &= self._run(None, name, "brew", argv, cwd, {})
        return "ok" if ok and not failed else "failed"

    def _run_application(self, planned: PlannedApp) -> bool:
        app = planned.application
        steps = [
            p
            for p in planned.steps
            if (self.brew or p.step.kind != "brewfile") and p.once not in ("done", "changed")
        ]
        if not steps:
            return True
        self._header(f"{app.name} ({app.id})")
        env = {"APP_ID": app.id, "APP_DIR": str(app.path), "WORKSTATION_PROFILE": self.log.data["profile"]}
        for planned_step in steps:
            step = planned_step.step
            file = app.path / step.file
            self._step(step.file)
            if step.kind == "brewfile":
                argv = ["bash", "-c", BUNDLE, "bundle", str(file)]
                extra = {**env, "HOMEBREW_NO_AUTO_UPDATE": "1"}
            elif file.suffix == ".py":
                argv, extra = [sys.executable, str(file)], env
            else:
                argv, extra = ["bash", str(file)], env
            sha256 = file_sha256(file)
            if not self._run(app.id, step.file, step.kind, argv, app.path, extra):
                return False
            if step.kind == "once":
                self.state.record_once(app.id, step.file, sha256)
        return True

    def _run(
        self,
        app: str | None,
        name: str,
        kind: str,
        argv: list[str],
        cwd: Path,
        extra: dict[str, str],
    ) -> bool:
        started = now()
        path = self.log.output_path(app, name)
        with path.open("wb") as output:
            try:
                code = process.run(argv, cwd, {**os.environ, **extra}, output)
            except OSError as e:
                output.write(f"{e}\n".encode())
                code = 127
        ok = code == 0
        self.log.add(
            StepResult(app, name, kind, "ok" if ok else "failed", started, now(), code, path.name)
        )
        if not ok:
            print(self._paint(f"   ✗ {name} failed with exit code {code}", "31"), flush=True)
        return ok

    def _header(self, title: str, note: str = "") -> None:
        note = f" {self._paint(note, '33')}" if note else ""
        print(self._paint(f"==> {title}", "1;34") + note, flush=True)

    def _step(self, name: str) -> None:
        print(self._paint(f" -> {name}", "2"), flush=True)

    def _paint(self, text: str, code: str) -> str:
        return f"\x1b[{code}m{text}\x1b[0m" if self.color else text
