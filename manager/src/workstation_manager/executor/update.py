import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from ..core import Application, Step, StepKind, Workspace
from ..core.query import parse_query, select
from ..core.runs import RunLog, RunStatus, StepResult
from ..core.state import State, file_sha256, now
from . import process

OnceStatus = Literal["pending", "done", "changed"]

# Uninstalls run between update and upgrade, so nothing is upgraded just to be removed
BREW_UPDATE = (("brew update", ["brew", "update"]),)
BREW_UPGRADE = (("brew upgrade", ["brew", "upgrade"]),)
BREW_AFTER = (("brew autoremove", ["brew", "autoremove"]), ("brew cleanup", ["brew", "cleanup"]))
STEP_SH = Path(__file__).with_name("step.sh")
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
    # Marked for uninstall in the profile, dependents first; only their uninstall steps
    uninstalls: list[PlannedApp] = field(default_factory=list)


def make_plan(
    workspace: Workspace,
    state: State,
    profile: str,
    terms: list[str],
    force: bool = False,
    no_deps: bool = False,
    only: StepKind | None = None,
) -> Plan:
    """Applications the profile installs, narrowed by terms; dependencies are included
    unless no_deps, and applications outside the profile only with force.
    Matching applications marked for uninstall are uninstalled instead.
    With `only`, just that kind of step: no brew, no uninstalls, applications without one left out."""
    catalog = workspace.catalog()
    profile_state = workspace.state(profile, catalog)
    install = profile_state.install_order
    installed = set(install)
    marked = profile_state.uninstall
    if conflicts := [id for id in marked if id in installed]:
        raise PlanError(
            f"Marked for uninstall but still installed by profile '{profile}': "
            f"{', '.join(conflicts)} (ws keep, or deselect what needs them)"
        )
    if not terms:
        ids, removals = install, marked
    else:
        query = parse_query(terms)
        matched = select(catalog, query, keep={*installed, *marked}, uninstall=marked)
        removals = [id for id in matched if id in marked]
        matched = [id for id in matched if id not in marked]
        if not force:
            outside = [id for id in query.ids if id not in installed and id not in marked]
            if outside:
                raise PlanError(
                    f"Not installed by profile '{profile}': {', '.join(outside)} (use --force)"
                )
            matched = [id for id in matched if id in installed]
        ordered = catalog.resolve(matched)
        ids = [id for id in ordered if id in set(matched)] if no_deps else ordered
    removals = [id for id in reversed(catalog.resolve(removals)) if id in set(removals)]
    if only:
        apps = [plan_application(catalog.get(id), state) for id in ids]
        apps = [PlannedApp(a.application, tuple(p for p in a.steps if p.step.kind == only)) for a in apps]
        return Plan(profile, [a for a in apps if a.steps], full=False)
    return Plan(
        profile,
        [plan_application(catalog.get(id), state) for id in ids],
        full=not terms,
        uninstalls=[plan_uninstall(catalog.get(id)) for id in removals],
    )


def plan_uninstall(application: Application) -> PlannedApp:
    steps = (PlannedStep(s) for s in application.steps if s.kind == "uninstall")
    return PlannedApp(application, tuple(steps))


def plan_application(application: Application, state: State) -> PlannedApp:
    steps = []
    for step in application.steps:
        if step.kind == "uninstall":
            continue
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


NO_UNINSTALL_STEPS = "no uninstall steps"
ONCE_NOTES = {
    "pending": "once",
    "done": "once, done",
    "changed": "once, changed since it ran; not rerun (`once reset` to rerun)",
}


def format_plan(plan: Plan) -> str:
    lines = [f"Profile {plan.profile} · {len(plan.apps)} applications"]
    if plan.uninstalls:
        lines[0] += f" · {len(plan.uninstalls)} to uninstall"
    if plan.full:
        lines.append("brew update, uninstalls, brew upgrade before; brew autoremove, cleanup after")
    for planned in plan.uninstalls:
        app = planned.application
        lines.append(f"==> Uninstall {app.name} ({app.id})")
        for p in planned.steps:
            lines.append(f"    {p.step.file:<16} uninstall")
        if not planned.steps:
            lines.append(f"    {NO_UNINSTALL_STEPS}; stays on the list")
    for planned in plan.apps:
        app = planned.application
        lines.append(f"==> {app.name} ({app.id})")
        for p in planned.steps:
            note = ONCE_NOTES[p.once] if p.once else p.step.kind
            lines.append(f"    {p.step.file:<16} {note}")
    return "\n".join(lines)


class Executor:
    def __init__(
        self,
        repo: Path,
        state: State,
        log: RunLog,
        brew: bool = True,
        fail_fast: bool = False,
        env: dict[str, str] | None = None,
    ):
        """`env` is added to every application step's environment."""
        self.env = env or {}
        self.repo = repo
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
        if self.brew and plan.full:
            ok &= self._brew(BREW_UPDATE)
        for planned in plan.uninstalls:
            if not self._uninstall(planned):
                ok = False
                if self.fail_fast:
                    return "failed"
        if self.brew and plan.full:
            ok &= self._brew(BREW_UPGRADE)

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
            ok &= self._brew(BREW_AFTER)
        return "ok" if ok and not failed else "failed"

    def _brew(self, steps: tuple[tuple[str, list[str]], ...]) -> bool:
        ok = True
        for name, argv in steps:
            self._header(name)
            ok &= self._run(None, name, "brew", argv, Path.home(), {})
        return ok

    def _uninstall(self, planned: PlannedApp) -> bool:
        """Failures stay with the application: nothing else is skipped because of them.
        A successful uninstall forgets the once steps, so a reinstall runs them again."""
        app = planned.application
        title = f"Uninstall {app.name} ({app.id})"
        if not planned.steps:
            self._header(title, f"skipped, {NO_UNINSTALL_STEPS}")
            timestamp = now()
            self.log.add(
                StepResult(app.id, "*", "uninstall", "skipped", timestamp, timestamp, reason=NO_UNINSTALL_STEPS)
            )
            return True
        self._header(title)
        for planned_step in planned.steps:
            if not self._run_step(app, planned_step.step):
                return False
        self.state.reset_once(app.id)
        self.log.add_uninstalled(app.id)
        return True

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
        return all(self._run_step(app, p.step) for p in steps)

    def _run_step(self, app: Application, step: Step) -> bool:
        env = {
            **self.env,
            "APP_ID": app.id,
            "APP_DIR": str(app.path),
            "WORKSTATION_PROFILE": self.log.data["profile"],
            "WORKSTATION_ROOT": str(self.repo),
        }
        file = app.path / step.file
        self._step(step.file)
        if step.kind == "brewfile":
            argv = ["bash", "-c", BUNDLE, "bundle", str(file)]
            extra = {**env, "HOMEBREW_NO_AUTO_UPDATE": "1"}
        elif file.suffix == ".py":
            # The repository on the path, as the generated scripts did, for its `lib` package
            python_path = os.pathsep.join(filter(None, [str(self.repo), os.environ.get("PYTHONPATH")]))
            argv, extra = [sys.executable, str(file)], {**env, "PYTHONPATH": python_path}
        else:
            argv, extra = ["bash", str(STEP_SH), str(self.repo), str(file)], env
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
            except KeyboardInterrupt:
                self.log.add(
                    StepResult(app, name, kind, "failed", started, now(), None, path.name, "interrupted")
                )
                raise
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
