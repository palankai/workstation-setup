import os
from pathlib import Path

import pytest

from workstation_manager.core import Workspace
from workstation_manager.core.state import State, file_sha256
from workstation_manager.migrate import migrate

from .test_core import workspace, write_app  # noqa: F401

INSTALLER = "curl -fsSL https://example.com/install | sh\n"


@pytest.fixture
def old_setup(workspace: Workspace, tmp_path: Path) -> Path:  # noqa: F811
    """claude-code as the old setup left it: component folder, run once marker, linked hooks."""
    component = workspace.root / "components" / "ai" / "claude-code"
    (component / "config" / "hooks").mkdir(parents=True)
    (component / "10-runonce.sh").write_text(INSTALLER)
    app = workspace.catalog().get("claude-code").path
    readme = app / "README.md"
    readme.write_text(readme.read_text().replace("---\n\n", "legacy: components/ai/claude-code\n---\n\n"))
    (app / "10-once.sh").write_text(INSTALLER)
    (app / "config" / "hooks").mkdir(parents=True)
    markers = workspace.root / "targets" / "dev" / ".once"
    markers.mkdir(parents=True)
    marker = markers / "installed-install_ai_claude_code_10_runonce_sh-once"
    marker.touch()
    os.utime(marker, (1_700_000_000, 1_700_000_000))
    home = tmp_path / "home"
    (home / ".claude").mkdir(parents=True)
    (home / ".claude" / "hooks").symlink_to(component / "config" / "hooks")
    return home


def run(workspace: Workspace, home: Path, dry_run: bool = False) -> list[str]:  # noqa: F811
    return migrate(workspace, State(home / "state"), "dev", home, dry_run)


def test_records_once_steps_the_old_setup_ran(workspace: Workspace, old_setup: Path):  # noqa: F811
    assert "+ once claude-code/10-once.sh: recorded as run at 2023-11-14T22:13:20+00:00" in run(
        workspace, old_setup
    )
    record = State(old_setup / "state").once_record("claude-code", "10-once.sh")
    app = workspace.catalog().get("claude-code").path
    assert record.sha256 == file_sha256(app / "10-once.sh")


def test_a_changed_once_step_keeps_the_old_hash(workspace: Workspace, old_setup: Path):  # noqa: F811
    old = workspace.root / "components" / "ai" / "claude-code" / "10-runonce.sh"
    old.write_text("old installer\n")
    run(workspace, old_setup)
    record = State(old_setup / "state").once_record("claude-code", "10-once.sh")
    assert record.sha256 == file_sha256(old)


def test_relinks_into_the_application_and_removes_ln_nesting(
    workspace: Workspace, old_setup: Path  # noqa: F811
):
    old_hooks = workspace.root / "components" / "ai" / "claude-code" / "config" / "hooks"
    new_hooks = workspace.catalog().get("claude-code").path / "config" / "hooks"
    (old_hooks / "hooks").symlink_to(new_hooks)
    lines = run(workspace, old_setup)
    assert f"- {old_hooks / 'hooks'}: stray link from ln -sf, removed" in lines
    assert os.readlink(old_setup / ".claude" / "hooks") == str(new_hooks)
    assert not os.path.lexists(old_hooks / "hooks")


def test_replaces_a_folder_that_should_be_a_link(workspace: Workspace, old_setup: Path):  # noqa: F811
    new_hooks = workspace.catalog().get("claude-code").path / "config" / "hooks"
    hooks = old_setup / ".claude" / "hooks"
    hooks.unlink()
    hooks.mkdir()
    (hooks / "stop.py").write_text("print()\n")
    (hooks / "hooks").symlink_to(new_hooks)
    run(workspace, old_setup)
    assert os.readlink(hooks) == str(new_hooks)
    assert (old_setup / ".claude" / "hooks.pre-migrate" / "stop.py").is_file()


def test_running_again_changes_nothing(workspace: Workspace, old_setup: Path):  # noqa: F811
    run(workspace, old_setup)
    state = (old_setup / "state" / "state.yaml").read_text()
    assert run(workspace, old_setup) == ["  once claude-code/10-once.sh: already recorded"]
    assert (old_setup / "state" / "state.yaml").read_text() == state


def test_dry_run_changes_nothing(workspace: Workspace, old_setup: Path):  # noqa: F811
    old_hooks = workspace.root / "components" / "ai" / "claude-code" / "config" / "hooks"
    assert len(run(workspace, old_setup, dry_run=True)) == 2
    assert not (old_setup / "state").exists()
    assert os.readlink(old_setup / ".claude" / "hooks") == str(old_hooks)


def test_nothing_to_do_without_the_old_setup(workspace: Workspace, tmp_path: Path):  # noqa: F811
    (tmp_path / "home").mkdir()
    assert run(workspace, tmp_path / "home") == []
