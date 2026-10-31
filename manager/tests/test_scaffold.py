from pathlib import Path

from workstation_manager.core import Workspace
from workstation_manager.scaffold import MARKER, UNINSTALL_FILE, scaffold_uninstall

from .test_core import workspace  # noqa: F401


def app_dir(workspace: Workspace, id: str) -> Path:  # noqa: F811
    return workspace.catalog().get(id).path


def test_brew_only_application_gets_idempotent_uninstall(workspace: Workspace):  # noqa: F811
    bat = app_dir(workspace, "bat")
    (bat / "00-Brewfile").write_text('tap "x/tap"\nbrew "x/tap/bat"  # comment\ncask "bat-app", greedy: true\n')

    assert scaffold_uninstall(workspace.catalog(), [], dry_run=False) == ["bat: create 90-uninstall.sh"]

    script = (bat / UNINSTALL_FILE).read_text().splitlines()
    assert script[0].startswith(MARKER)
    assert script[1:] == [
        "if brew list --cask bat-app >/dev/null 2>&1; then brew uninstall --cask bat-app; fi",
        "if brew list --formula x/tap/bat >/dev/null 2>&1; then brew uninstall --formula x/tap/bat; fi",
    ]
    assert scaffold_uninstall(workspace.catalog(), [], dry_run=False) == []


def test_dry_run_writes_nothing(workspace: Workspace):  # noqa: F811
    jq = app_dir(workspace, "jq")
    (jq / "Brewfile").write_text('brew "jq"\n')
    assert scaffold_uninstall(workspace.catalog(), ["jq"], dry_run=True) == ["jq: create 90-uninstall.sh (dry run)"]
    assert not (jq / UNINSTALL_FILE).exists()


def test_regenerates_own_file_but_keeps_hand_written(workspace: Workspace):  # noqa: F811
    jq, fd = app_dir(workspace, "jq"), app_dir(workspace, "fd")
    (jq / "Brewfile").write_text('brew "jq"\n')
    (jq / UNINSTALL_FILE).write_text(f"{MARKER} old\n")
    (fd / "Brewfile").write_text('brew "fd"\n')
    (fd / "50-uninstall.sh").write_text("brew uninstall fd\n")

    assert scaffold_uninstall(workspace.catalog(), [], dry_run=False) == ["jq: update 90-uninstall.sh"]
    assert (fd / "50-uninstall.sh").read_text() == "brew uninstall fd\n"
    assert not (fd / UNINSTALL_FILE).exists()


def test_skips_scripts_unsupported_lines_and_shared_packages(workspace: Workspace):  # noqa: F811
    bat, jq, fd, git = (app_dir(workspace, id) for id in ("bat", "jq", "fd", "git"))
    (bat / "Brewfile").write_text('brew "bat"\n')
    (bat / "10-run.sh").write_text("true\n")
    (jq / "Brewfile").write_text('mas "Xcode", id: 497799835\n')
    (fd / "Brewfile").write_text('brew "fd"\nbrew "node"\n')
    (git / "Brewfile").write_text('brew "node"\n')

    lines = scaffold_uninstall(workspace.catalog(), [], dry_run=False)

    assert sorted(lines) == [
        "fd: create 90-uninstall.sh",
        "git: skipped, nothing to uninstall",
        'jq: skipped, unsupported Brewfile line in Brewfile: mas "Xcode", id: 497799835',
    ]
    assert not (bat / UNINSTALL_FILE).exists()
    script = (fd / UNINSTALL_FILE).read_text()
    assert "# brew node left out: also installed by git" in script
    assert "uninstall --formula fd" in script and "uninstall --formula node" not in script
