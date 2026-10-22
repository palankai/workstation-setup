import pytest

from workstation_manager.cli import main
from workstation_manager.core import Workspace

from .test_core import workspace  # noqa: F401


def ws(workspace: Workspace, *args: str) -> None:  # noqa: F811
    main(["--root", str(workspace.root), *args])


def test_select_and_deselect(workspace: Workspace, capsys):  # noqa: F811
    ws(workspace, "select", "fd", "jq", "vim", "--profile", "dev")
    out = capsys.readouterr().out
    assert "Selected in dev: fd" in out
    assert "Already selected: jq" in out
    assert "Always installed (fundamental): vim" in out
    assert "fd" in workspace.profile("dev").refs

    workspace.update_selection("dev", ["zsh", "claude-code", "fd"])
    ws(workspace, "unselect", "fd", "jq", "--profile", "dev")
    out = capsys.readouterr().out
    assert "Deselected in dev: fd" in out
    assert "Already not selected: jq" in out
    assert "Still installed as a fundamental or dependency: jq" in out
    assert "fd" not in workspace.profile("dev").refs


def test_flag_commands(workspace: Workspace, capsys):  # noqa: F811
    ws(workspace, "deprecate", "jq", "fd")
    ws(workspace, "archive", "jq")
    catalog = workspace.catalog()
    assert catalog.get("fd").deprecated and catalog.get("jq").archived
    capsys.readouterr()
    ws(workspace, "undeprecate", "jq")
    ws(workspace, "unarchive", "jq", "fd")
    out = capsys.readouterr().out
    assert "Cleared deprecated: jq" in out
    assert "Already not archived: fd" in out
    assert not workspace.catalog().get("jq").archived


def test_unknown_id_is_an_error(workspace: Workspace):  # noqa: F811
    with pytest.raises(SystemExit, match="Unknown application id 'nope'"):
        ws(workspace, "archive", "nope")
