from pathlib import Path

import pytest

from workstation_manager.core import CatalogError, ProfileError, Workspace

PROFILE = """\
applications:
  # fundamentals
  - $ref: zsh
  - $ref: git

  - $ref: bat
  - $ref: jq
  - application: VSCode
    steps: ["brew install code"]
"""


def write_app(
    root: Path, folder: str, id: str, dependencies: str = "[]", extra: str = ""
) -> Path:
    path = root / "applications" / folder
    path.mkdir(parents=True)
    (path / "README.md").write_text(
        f"---\nid: {id}\nname: {id.title()}\n"
        f"dependencies: {dependencies}\n{extra}---\n\n# {id}\n"
    )
    return path


@pytest.fixture
def workspace(tmp_path: Path) -> Workspace:
    for id in ["zsh", "git", "bat", "jq", "fd"]:
        write_app(tmp_path, id, id)
    write_app(tmp_path, "ai/claude", "claude-code", "[jq]")
    write_app(tmp_path, "folders", "home-folders", extra="fundamental: true\norder: 10\n")
    write_app(tmp_path, "vim", "vim", "[home-folders]", "fundamental: true\norder: 60\n")
    (tmp_path / "profiles").mkdir()
    (tmp_path / "profiles" / "dev.yaml").write_text(PROFILE)
    return Workspace(tmp_path)


def test_catalog_finds_nested_folders_by_id(workspace: Workspace):
    catalog = workspace.catalog()
    assert catalog.get("claude-code").path.name == "claude"
    assert len(catalog) == 8
    assert catalog.fundamentals == ["home-folders", "vim"]


def test_catalog_rejects_duplicate_ids(workspace: Workspace):
    write_app(workspace.root, "other", "jq")
    with pytest.raises(CatalogError, match="Duplicate id 'jq'"):
        workspace.catalog()


def test_catalog_rejects_unknown_dependency(workspace: Workspace):
    write_app(workspace.root, "broken", "broken", "[nope]")
    with pytest.raises(CatalogError, match="unknown id 'nope'"):
        workspace.catalog()


def test_resolve_orders_dependencies_first_then_by_id(workspace: Workspace):
    assert workspace.catalog().resolve(["claude-code", "bat"]) == ["bat", "jq", "claude-code"]


def test_resolve_uses_order_but_dependencies_win(workspace: Workspace):
    write_app(workspace.root, "early", "early", "[late]", "order: 1\n")
    write_app(workspace.root, "late", "late", extra="order: 500\n")
    write_app(workspace.root, "middle", "middle", extra="order: 50\n")
    order = workspace.catalog().resolve(["middle", "early", "bat"])
    assert order == ["middle", "bat", "late", "early"]


def test_invalid_order_is_rejected(workspace: Workspace):
    write_app(workspace.root, "bad", "bad", extra="order: soon\n")
    with pytest.raises(CatalogError, match="'order' must be an integer"):
        workspace.catalog()


def test_fundamental_needs_the_field_not_a_tag(workspace: Workspace):
    write_app(workspace.root, "tagged", "tagged", extra="tags: [fundamental]\n")
    assert "tagged" not in workspace.catalog().fundamentals


def test_steps_are_top_level_instruction_files_in_name_order(workspace: Workspace):
    path = write_app(workspace.root, "steps", "steps")
    for name in ["20-run.sh", "10-once.sh", "00-Brewfile", "once.py", "zshrc"]:
        (path / name).write_text("")
    (path / "config").mkdir()
    (path / "config" / "run.sh").write_text("")
    steps = workspace.catalog().get("steps").steps
    assert [(s.file, s.kind) for s in steps] == [
        ("00-Brewfile", "brewfile"),
        ("10-once.sh", "once"),
        ("20-run.sh", "run"),
        ("once.py", "once"),
    ]


def test_resolve_detects_cycles(workspace: Workspace):
    write_app(workspace.root, "a", "a", "[b]")
    write_app(workspace.root, "b", "b", "[a]")
    with pytest.raises(CatalogError, match="cycle"):
        workspace.catalog().resolve(["a"])


def test_profile_round_trip_is_lossless(workspace: Workspace):
    assert workspace.profile("dev").dump() == PROFILE


def test_profile_separates_refs_and_inline(workspace: Workspace):
    profile = workspace.profile("dev")
    assert profile.refs == ["zsh", "git", "bat", "jq"]
    assert [e.label for e in profile.inline] == ["VSCode"]


def test_state_reports_implied_dependencies(workspace: Workspace):
    workspace.update_selection("dev", ["zsh", "claude-code"])
    state = workspace.state("dev")
    assert state.selected == ["zsh", "claude-code"]
    assert state.implied == ["jq"]


def test_update_selection_keeps_comments_inline_and_order(workspace: Workspace):
    workspace.update_selection("dev", ["zsh", "git", "jq", "fd", "claude-code"])
    assert (workspace.profiles_dir / "dev.yaml").read_text() == """\
applications:
  # fundamentals
  - $ref: zsh
  - $ref: git

  - $ref: claude-code
  - $ref: fd
  - $ref: jq
  - application: VSCode
    steps: ["brew install code"]
"""


def test_update_selection_keeps_blank_line_of_removed_entry(workspace: Workspace):
    workspace.update_selection("dev", ["zsh", "bat", "jq"])
    assert (workspace.profiles_dir / "dev.yaml").read_text().startswith(
        "applications:\n  # fundamentals\n  - $ref: zsh\n\n  - $ref: bat\n"
    )


def test_update_selection_rejects_unknown_ids(workspace: Workspace):
    with pytest.raises(CatalogError):
        workspace.update_selection("dev", ["nope"])


def test_update_selection_keeps_unknown_refs(workspace: Workspace):
    path = workspace.profiles_dir / "dev.yaml"
    path.write_text(PROFILE.replace("$ref: bat", "$ref: renamed-away"))
    workspace.update_selection("dev", ["zsh"])
    assert workspace.profile("dev").refs == ["zsh", "renamed-away"]


@pytest.mark.parametrize("name", ["../etc", "a/b", ""])
def test_profile_names_are_validated(workspace: Workspace, name: str):
    with pytest.raises(ProfileError):
        workspace.profile(name)


def test_discover_walks_up(workspace: Workspace):
    nested = workspace.root / "applications" / "ai"
    assert Workspace.discover(nested).root == workspace.root.resolve()


def test_fundamentals_are_always_installed_first(workspace: Workspace):
    state = workspace.state("dev")
    assert state.fundamentals == ["home-folders", "vim"]
    assert "vim" not in state.selected and "vim" not in state.implied
    assert state.install_order[:2] == ["home-folders", "vim"]


def test_fundamentals_are_not_written_to_profiles(workspace: Workspace):
    workspace.update_selection("dev", ["vim", "bat"])
    assert workspace.profile("dev").refs == ["bat"]
