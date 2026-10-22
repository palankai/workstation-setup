from pathlib import Path

import pytest

from workstation_manager.core import CatalogError, ProfileError, UninstallError, Workspace, set_flag

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
    root: Path,
    folder: str,
    id: str,
    dependencies: str = "[]",
    extra: str = "",
    kind: str = "CLI Tool",
) -> Path:
    path = root / "applications" / folder
    path.mkdir(parents=True)
    (path / "README.md").write_text(
        f"---\nstereotype: application\nid: {id}\nname: {id.title()}\nkind: {kind}\n"
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


def test_container_readmes_are_not_applications(workspace: Workspace):
    (workspace.root / "applications" / "ai" / "README.md").write_text("# AI tools\n")
    group = workspace.root / "applications" / "web"
    group.mkdir()
    (group / "README.md").write_text("---\ntitle: Web\n---\n")
    write_app(workspace.root, "web/browser", "browser")
    catalog = workspace.catalog()
    assert "browser" in catalog and len(catalog) == 9


def test_applications_are_not_searched_for_nested_applications(workspace: Workspace):
    write_app(workspace.root, "jq/nested", "nested")
    assert "nested" not in workspace.catalog()


def test_kinds_come_from_applications(workspace: Workspace):
    write_app(workspace.root, "slack", "slack", kind="Desktop App")
    assert workspace.catalog().kinds == ["CLI Tool", "Desktop App"]


def test_kind_is_required(workspace: Workspace):
    path = workspace.root / "applications" / "nokind"
    path.mkdir()
    (path / "README.md").write_text("---\nstereotype: application\nid: nokind\nname: X\n---\n")
    with pytest.raises(CatalogError, match="missing 'kind'"):
        workspace.catalog()


def test_settings_have_builtin_searches_first(workspace: Workspace):
    builtins = ["Fundamentals", "Deprecated", "Trial", "Archived"]
    assert [s.name for s in workspace.settings().searches] == builtins
    (workspace.applications_dir / "settings.yaml").write_text(
        "searches:\n  - name: Rust\n    query: '#rust'\n"
    )
    searches = workspace.settings().searches
    assert [s.name for s in searches] == [*builtins, "Rust"]
    assert (searches[-1].query, searches[-1].builtin) == ("#rust", False)


def test_invalid_saved_search_is_rejected(workspace: Workspace):
    (workspace.applications_dir / "settings.yaml").write_text("searches:\n  - name: X\n")
    with pytest.raises(CatalogError, match="'name' and a 'query'"):
        workspace.settings()


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


def test_status_flags_default_to_false(workspace: Workspace):
    write_app(workspace.root, "old", "old", extra="deprecated: true\narchived: true\n")
    catalog = workspace.catalog()
    old, jq = catalog.get("old"), catalog.get("jq")
    assert (old.deprecated, old.archived, old.trial) == (True, True, False)
    assert (jq.deprecated, jq.archived, jq.trial) == (False, False, False)


def test_invalid_flag_is_rejected(workspace: Workspace):
    write_app(workspace.root, "bad", "bad", extra="trial: maybe\n")
    with pytest.raises(CatalogError, match="'trial' must be true or false"):
        workspace.catalog()


def test_set_flag_edits_only_its_line(workspace: Workspace):
    readme = workspace.catalog().get("jq").path / "README.md"
    original = readme.read_text()
    set_flag(readme, "deprecated", True)
    set_flag(readme, "archived", True)
    catalog = workspace.catalog()
    assert catalog.get("jq").deprecated and catalog.get("jq").archived
    set_flag(readme, "archived", True)
    assert readme.read_text().count("archived: true") == 1
    set_flag(readme, "deprecated", False)
    set_flag(readme, "archived", False)
    assert readme.read_text() == original
    with pytest.raises(CatalogError, match="can't be changed"):
        set_flag(readme, "fundamental", True)


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


def test_mark_uninstall_deselects_and_lists(workspace: Workspace):
    state = workspace.mark_uninstall("dev", ["bat", "fd"])
    assert state.uninstall == ["bat", "fd"]
    assert "bat" not in state.selected
    text = (workspace.profiles_dir / "dev.yaml").read_text()
    assert text.endswith("uninstall:\n  - $ref: bat\n  - $ref: fd\n")
    assert "# fundamentals" in text and "VSCode" in text


def test_keep_leaves_selection_alone_and_drops_empty_list(workspace: Workspace):
    workspace.mark_uninstall("dev", ["bat"])
    state = workspace.keep("dev", ["bat"])
    assert state.uninstall == [] and "bat" not in state.selected
    assert "uninstall" not in (workspace.profiles_dir / "dev.yaml").read_text()


def test_uninstall_refuses_fundamentals_and_needed_applications(workspace: Workspace):
    with pytest.raises(UninstallError, match="Fundamental"):
        workspace.mark_uninstall("dev", ["vim"])
    workspace.update_selection("dev", ["claude-code"])
    with pytest.raises(UninstallError, match="jq by claude-code"):
        workspace.mark_uninstall("dev", ["jq"])
    # Uninstalling the dependent leaves the dependency alone
    state = workspace.mark_uninstall("dev", ["claude-code"])
    assert state.uninstall == ["claude-code"] and "jq" not in state.install_order


def test_selecting_takes_it_and_its_dependencies_off_the_uninstall_list(workspace: Workspace):
    workspace.mark_uninstall("dev", ["jq", "fd"])
    state = workspace.update_selection("dev", ["claude-code"])
    assert state.uninstall == ["fd"]
