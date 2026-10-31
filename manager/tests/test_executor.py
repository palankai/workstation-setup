import json
from pathlib import Path

import pytest

from workstation_manager.core import CatalogError, Workspace
from workstation_manager.core.query import parse_query, search, select
from workstation_manager.executor.report import format_search
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


def test_is_uninstall_matches_marked_applications(workspace: Workspace):  # noqa: F811
    catalog = workspace.catalog()
    assert select(catalog, parse_query(["is:uninstall"]), uninstall={"fd"}) == ["fd"]
    assert [a.id for a in search(catalog, ["is:uninstall"], uninstall={"fd"})] == ["fd"]


def test_select_matches_kind_prefix_and_hides_archived(workspace: Workspace):  # noqa: F811
    write_app(workspace.root, "old", "old", kind="Desktop App", extra="archived: true\n")
    write_app(workspace.root, "slack", "slack", kind="Desktop App")
    catalog = workspace.catalog()
    assert select(catalog, parse_query(["kind:desktop"])) == ["slack"]
    assert select(catalog, parse_query(["kind:desktop"]), keep={"old"}) == ["old", "slack"]
    assert select(catalog, parse_query(["is:archived"])) == ["old"]


def test_search_needs_every_word_and_hides_archived(workspace: Workspace):  # noqa: F811
    write_app(workspace.root, "slack", "slack", kind="Desktop App", extra="description: Team chat\n")
    write_app(workspace.root, "skype", "skype", kind="Desktop App", extra="description: Chat\narchived: true\n")
    catalog = workspace.catalog()
    assert [a.id for a in search(catalog, ["chat"])] == ["slack"]
    assert [a.id for a in search(catalog, ["chat", "team", "kind:desktop"])] == ["slack"]
    assert [a.id for a in search(catalog, ["chat"], keep={"skype"})] == ["skype", "slack"]
    assert [a.id for a in search(catalog, ["is:archived"])] == ["skype"]


def test_search_lines_mark_installed_and_show_tags(workspace: Workspace):  # noqa: F811
    write_app(workspace.root, "slack", "slack", extra='description: "Slack, team chat"\ntags: [chat]\n')
    lines = format_search([workspace.catalog().get("slack")], {"slack"}, color=False)
    assert lines == ["✓ slack  CLI Tool  Team chat  #chat"]


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
    assert [s["step"] for s in steps] == [
        "brew update", "brew upgrade", "brew autoremove", "brew cleanup"
    ]
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


def test_uninstalls_run_dependents_first_and_skip_install_steps(workspace: Workspace, state: State):  # noqa: F811
    write_app(workspace.root, "slack", "slack", "[fd]")
    catalog = workspace.catalog()
    for id in ("fd", "slack"):
        script(catalog.get(id).path, "10-run.sh", "echo install\n")
        script(catalog.get(id).path, "90-uninstall.sh", "echo removed $APP_ID\n")
    script(catalog.get("bat").path, "90-uninstall.sh", "echo never\n")
    workspace.mark_uninstall("dev", ["fd", "slack"])

    plan = make_plan(workspace, state, "dev", [])
    assert [p.application.id for p in plan.uninstalls] == ["slack", "fd"]
    assert all(s.step.kind != "uninstall" for p in plan.apps for s in p.steps)

    state.record_once("fd", "10-once.sh", "abc")
    status, data = run(workspace, state, [])
    assert status == "ok"
    assert [(s["app"], s["step"]) for s in data["steps"][:2]] == [
        ("slack", "90-uninstall.sh"), ("fd", "90-uninstall.sh")
    ]
    assert data["uninstalled"] == ["slack", "fd"]
    assert state.once_record("fd", "10-once.sh") is None


def test_failed_uninstall_affects_nothing_else(workspace: Workspace, state: State):  # noqa: F811
    catalog = workspace.catalog()
    script(catalog.get("bat").path, "90-uninstall.sh", "exit 2\n")
    script(catalog.get("jq").path, "10-run.sh", "echo jq\n")
    workspace.mark_uninstall("dev", ["bat", "fd"])
    status, data = run(workspace, state, [])
    assert status == "failed" and data["uninstalled"] == []
    results = {s["app"]: s for s in data["steps"]}
    assert results["bat"]["status"] == "failed"
    assert (results["fd"]["status"], results["fd"]["reason"]) == ("skipped", "no uninstall steps")
    assert results["jq"]["status"] == "ok"


def test_query_uninstalls_matching_marked_applications(workspace: Workspace, state: State):  # noqa: F811
    script(workspace.catalog().get("jq").path, "90-uninstall.sh", "echo bye\n")
    workspace.mark_uninstall("dev", ["fd"])
    plan = make_plan(workspace, state, "dev", ["fd", "bat"])
    assert [p.application.id for p in plan.uninstalls] == ["fd"]
    assert ids(plan) == ["bat"]
    assert make_plan(workspace, state, "dev", ["is:uninstall"]).apps == []


def test_plan_rejects_uninstalling_what_is_installed(workspace: Workspace, state: State):  # noqa: F811
    path = workspace.profiles_dir / "dev.yaml"
    path.write_text(path.read_text() + "uninstall:\n  - $ref: bat\n")
    with pytest.raises(PlanError, match="still installed"):
        make_plan(workspace, state, "dev", [])


def fake_run(runs_dir: Path, id: str, days_ago: float) -> None:
    from datetime import UTC, datetime, timedelta

    started = (datetime.now(UTC) - timedelta(days=days_ago)).isoformat(timespec="seconds")
    (runs_dir / id).mkdir(parents=True)
    run = {"id": id, "profile": "dev", "command": [], "started": started, "finished": started,
           "status": "ok", "steps": []}
    (runs_dir / id / "run.json").write_text(json.dumps(run))


def test_prune_runs_keeps_latest_and_recent(tmp_path: Path):
    from workstation_manager.core.runs import prune_runs

    runs_dir = tmp_path / RUNS
    # Latest first: two recent runs, then old ones
    for id, days in [("a", 1), ("b", 3), ("c", 40), ("d", 50), ("e", 90)]:
        fake_run(runs_dir, id, days)

    assert prune_runs(tmp_path, keep=5, days=30) == []
    assert prune_runs(tmp_path, keep=3, days=30, dry_run=True) == ["d", "e"]
    assert (runs_dir / "d").is_dir()
    # Old runs among the latest N stay; recent ones stay whatever N is
    assert prune_runs(tmp_path, keep=1, days=2, protect=["c"]) == ["b", "d", "e"]
    assert sorted(p.name for p in runs_dir.iterdir()) == ["a", "c"]
    assert prune_runs(tmp_path, keep=0, days=0) == ["a", "c"]


def test_html_report_embeds_run_outputs_and_names(
    workspace: Workspace, state: State, tmp_path: Path  # noqa: F811
):
    from workstation_manager.executor.report import write_html_report

    app = workspace.catalog().get("jq").path
    script(app, "10-run.sh", "echo '</script><b>hi</b>'\n")
    _, data = run(workspace, state, ["jq"])
    template = tmp_path / "template.html"
    template.write_text('<script id="run-data" type="application/json">__RUN_DATA__</script>')

    path = write_html_report(data, state.directory, template, {"jq": "jq the JSON tool"})
    assert path == state.directory / RUNS / data["id"] / "report.html"
    html = path.read_text()
    assert "</script><b>" not in html
    embedded = json.loads(html.removeprefix(template.read_text().split("__")[0]).removesuffix("</script>"))
    assert embedded["run"]["id"] == data["id"]
    assert embedded["apps"] == {"jq": "jq the JSON tool"}
    assert any("</script><b>hi</b>" in text for text in embedded["outputs"].values())
