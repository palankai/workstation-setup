import json
from pathlib import Path

import pytest

from workstation_manager.core import CatalogError, Workspace
from workstation_manager.core.query import parse_query, select
from workstation_manager.core.runs import RUNS, RunLog, clean_output, list_runs
from workstation_manager.core.state import State
from workstation_manager.executor.update import Executor, Plan, PlanError, make_plan

from .test_core import workspace, write_app  # noqa: F401


@pytest.fixture
def state(tmp_path: Path) -> State:
    return State(tmp_path / "state" / "nested")


def script(app: Path, name: str, body: str) -> None:
    (app / name).write_text(body)


def ids(plan) -> list[str]:
    return [p.application.id for p in plan.apps]


def run(workspace: Workspace, state: State, terms: list[str], **options) -> tuple[str, dict]:  # noqa: F811
    plan = make_plan(workspace, state, "dev", terms)
    log = RunLog(state.directory / RUNS, "dev", terms)
    status = Executor(workspace.root, state, log, brew=False, **options).execute(plan)
    return status, log.data


def test_query_parses_filters_and_ids():
    query = parse_query(["git", "#rust", "tag:cli", "kind:cli", "is:trial"])
    assert (query.ids, query.tags, query.kinds, query.flags) == (
        ["git"],
        ["rust", "cli"],
        ["cli"],
        ["trial"],
    )
    with pytest.raises(CatalogError, match="Unknown flag"):
        parse_query(["is:nope"])


def test_select_matches_kind_prefix_and_hides_archived(workspace: Workspace):  # noqa: F811
    write_app(workspace.root, "old", "old", kind="Desktop App", extra="archived: true\n")
    write_app(workspace.root, "slack", "slack", kind="Desktop App")
    catalog = workspace.catalog()
    assert select(catalog, parse_query(["kind:desktop"])) == ["slack"]
    assert select(catalog, parse_query(["kind:desktop"]), keep={"old"}) == ["old", "slack"]
    assert select(catalog, parse_query(["is:archived"])) == ["old"]


def test_plan_defaults_to_whole_profile(workspace: Workspace, state: State):  # noqa: F811
    plan = make_plan(workspace, state, "dev", [])
    assert plan.full
    assert ids(plan) == workspace.state("dev").install_order


def test_plan_includes_dependencies_unless_no_deps(workspace: Workspace, state: State):  # noqa: F811
    workspace.update_selection("dev", ["claude-code"])
    assert ids(make_plan(workspace, state, "dev", ["claude-code"])) == ["jq", "claude-code"]
    plan = make_plan(workspace, state, "dev", ["claude-code"], no_deps=True)
    assert ids(plan) == ["claude-code"]
    assert not plan.full


def test_plan_needs_force_outside_profile(workspace: Workspace, state: State):  # noqa: F811
    with pytest.raises(PlanError, match="fd"):
        make_plan(workspace, state, "dev", ["fd"])
    assert ids(make_plan(workspace, state, "dev", ["fd"], force=True)) == ["fd"]


def test_once_runs_once_and_flags_changes(workspace: Workspace, state: State):  # noqa: F811
    app = workspace.catalog().get("bat").path
    script(app, "10-once.sh", "echo once >> \"$APP_DIR/ran\"\n")
    assert run(workspace, state, ["bat"])[0] == "ok"
    assert run(workspace, state, ["bat"])[0] == "ok"
    assert (app / "ran").read_text() == "once\n"
    assert make_plan(workspace, state, "dev", ["bat"]).apps[0].steps[0].once == "done"

    script(app, "10-once.sh", "echo changed\n")
    assert make_plan(workspace, state, "dev", ["bat"]).apps[0].steps[0].once == "changed"
    assert state.reset_once("bat") == ["10-once.sh"]
    assert make_plan(workspace, state, "dev", ["bat"]).apps[0].steps[0].once == "pending"


def test_state_folder_is_created(workspace: Workspace, state: State):  # noqa: F811
    assert not state.directory.exists()
    state.record_once("bat", "10-once.sh", "abc")
    assert State(state.directory).once_record("bat", "10-once.sh").sha256 == "abc"


def test_failure_skips_dependents_but_not_others(workspace: Workspace, state: State):  # noqa: F811
    workspace.update_selection("dev", ["claude-code", "bat"])
    catalog = workspace.catalog()
    script(catalog.get("jq").path, "10-run.sh", "echo broken; exit 3\n")
    script(catalog.get("claude-code").path, "10-run.sh", "echo should not run\n")
    script(catalog.get("bat").path, "10-run.sh", "echo bat $APP_ID in $(basename $PWD)\n")

    status, data = run(workspace, state, [])
    assert status == "failed" and data["status"] == "failed"
    results = {s["app"]: s for s in data["steps"]}
    assert (results["jq"]["status"], results["jq"]["exit_code"]) == ("failed", 3)
    assert results["claude-code"]["status"] == "skipped"
    assert "jq" in results["claude-code"]["reason"]
    assert results["bat"]["status"] == "ok"
    output = state.directory / RUNS / data["id"] / results["bat"]["output"]
    assert output.read_text() == "bat bat in bat\n"


def test_fail_fast_stops(workspace: Workspace, state: State):  # noqa: F811
    catalog = workspace.catalog()
    script(catalog.get("bat").path, "10-run.sh", "exit 1\n")
    script(catalog.get("jq").path, "10-run.sh", "echo jq\n")
    _, data = run(workspace, state, ["bat", "jq"], fail_fast=True)
    assert [s["app"] for s in data["steps"]] == ["bat"]


def test_brew_steps_are_captured(state: State, tmp_path: Path, monkeypatch):
    bin = tmp_path / "bin"
    bin.mkdir()
    (bin / "brew").write_text('#!/bin/sh\necho "brew $1"\n')
    (bin / "brew").chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin}:/usr/bin:/bin")
    log = RunLog(state.directory / RUNS, "dev", ["--brew-only"])
    assert Executor(tmp_path, state, log).execute(Plan("dev", [], full=True)) == "ok"
    steps = log.data["steps"]
    assert [s["step"] for s in steps] == ["brew update", "brew upgrade", "brew cleanup"]
    assert (log.directory / steps[1]["output"]).read_text() == "brew upgrade\n"


def test_shell_steps_get_setup_functions_and_set_e(workspace: Workspace, state: State):  # noqa: F811
    (workspace.root / "_setup_functions.sh").write_text('function greet { echo "hello $1"; }\n')
    app = workspace.catalog().get("bat").path
    script(app, "10-run.sh", 'greet "$APP_ID"\nfalse\necho "not reached"\n')
    _, data = run(workspace, state, ["bat"])
    step = data["steps"][0]
    assert step["status"] == "failed"
    assert (state.directory / RUNS / data["id"] / step["output"]).read_text() == "hello bat\n"


def test_brewfile_steps_are_skipped_without_brew(workspace: Workspace, state: State):  # noqa: F811
    script(workspace.catalog().get("bat").path, "00-Brewfile", 'brew "bat"\n')
    _, data = run(workspace, state, ["bat"])
    assert data["steps"] == []


def test_python_steps_can_import_the_package(workspace: Workspace, state: State):  # noqa: F811
    app = workspace.catalog().get("bat").path
    script(
        app,
        "10-run.py",
        "import os\nfrom workstation_manager import helpers\n"
        "print(helpers.app_id(), os.getcwd() == str(helpers.app_dir()))\n",
    )
    _, data = run(workspace, state, ["bat"])
    output = state.directory / RUNS / data["id"] / data["steps"][0]["output"]
    assert output.read_text() == "bat True\n"


def test_runs_are_listed_latest_first(state: State):
    first = RunLog(state.directory / RUNS, "dev", [])
    second = RunLog(state.directory / RUNS, "dev", ["bat"])
    second.data["started"] = "9999"
    second.finish("ok")
    assert [r["id"] for r in list_runs(state.directory)] == [second.id, first.id]
    assert json.loads((first.directory / "run.json").read_text())["status"] == "running"


def test_clean_output_strips_colours_and_progress():
    raw = b"\x1b[32mok\x1b[0m\r\n10%\r50%\r100%\ndone\r\n"
    assert clean_output(raw) == "ok\n100%\ndone\n"
