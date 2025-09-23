# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from argparse import ArgumentParser
from asyncio.unix_events import SelectorEventLoop
from dataclasses import dataclass
import os
import os.path
import glob
import re
import curses
from itertools import groupby
import sys
from typing import Union

FEATURE_FILES = [
    "Brewfile",
    "run.sh",
]

FEATURE_FILES_RE = re.compile(f".*({'|'.join(FEATURE_FILES)})$")
FEATURE_NAME_REGEX = re.compile(f"([0-9]?[0-9][0-9]-)?(.*)$")


def main(environ: dict[str, str], prog: str, argv: list[str]) -> None:
    targets = glob.glob("*", root_dir="targets")
    args = get_parser(prog, targets).parse_args(argv)
    target: str = str(args.target)


    broken_links = discover_broken_links("fundamentals") + discover_broken_links("components") + discover_broken_links(os.path.join("targets", target))
    if len(broken_links):
        print(f"🚨 {len(broken_links)} Broken links found")
        for broken_link in broken_links:
            print(f" - {broken_link}")
        sys.exit(1)

    selected = discover_existing_links(target)

    components = FeatureTree.build(discover("components", selected))

    unchecked, newly_selected, to_update = selector_ui(
        components, f"Component Selector [{target}]"
    )
    if not to_update:
        print(f"Abort updating {target}")
        sys.exit(0)

    print(f"\nResults:")
    print(f"Unchecked items ({len(unchecked)}):")
    remove_links(target, unchecked)

    print(f"Newly selected items ({len(newly_selected)}):")
    make_links(target, newly_selected)

    instructions = InstructionSet(target)
    for feature in discover(os.path.join("fundamentals")):
        instructions.extend("fundamentals", feature)

    for feature in discover(os.path.join("targets", target)):
        for dependency in find_dependencies(os.path.join("targets", target), feature.folder):
            dep_feature = FeatureFolder.make(
                root_dir="components",
                feature_folder=dependency,
                selected=True,
            )
            instructions.extend("components", dep_feature)
        instructions.extend("components", feature)

    script_lines = instructions.make_single_updater()
    script_path = os.path.join("targets", target, ".upgrade.sh")
    with open(script_path, "w") as f:
        _ = f.write("\n".join(script_lines))
        _ = f.write("\n")
    os.chmod(script_path, 0o755)


def get_parser(prog: str, targets: list[str]) -> ArgumentParser:
    parser = ArgumentParser(prog)
    _ = parser.add_argument("target", choices=targets)
    return parser


def discover(root_dir: str, selected: list[str] | None = None) -> list["FeatureFolder"]:
    if selected is None:
        selected = []
    return [
        FeatureFolder.make(
            root_dir=root_dir,
            feature_folder=feature_folder,
            selected=os.path.join(root_dir, feature_folder) in selected,
        )
        for feature_folder in find_features(root_dir)
    ]


def find_features(root: str, dir: str = "") -> list[str]:
    features: list[str] = []

    folders = os.scandir(os.path.join(root, dir))
    for folder in folders:
        if is_feature_folder(folder.path):
            features.append(os.path.join(dir, folder.name))
        elif folder.is_dir():
            features.extend(find_features(root, os.path.join(dir, folder.name)))
    return sorted(features)


def is_feature_folder(path: str) -> bool:
    if not os.path.exists(path):
        return False
    if not os.path.isdir(path):
        return False
    for filename in os.listdir(path):
        if FEATURE_FILES_RE.match(filename):
            return True
    return False


def find_dependencies(root: str, feature_path: str) -> list[str]:
    root = os.path.abspath(root)
    dependency_folder = os.path.join(root, feature_path, "dependencies")
    if not os.path.exists(dependency_folder) or not os.path.isdir(dependency_folder):
        return []
    dependencies: list[str] = []
    for feature in find_features(dependency_folder):
        if os.path.islink(os.path.join(dependency_folder, feature)):
            link = os.path.abspath(os.path.join(dependency_folder,os.readlink(os.path.join(dependency_folder, feature))))
            dependency = link.replace(root + os.sep, "")
            dependencies.extend(find_dependencies(root, dependency))
            dependencies.append(dependency)
        pass
    return dependencies



def make_links(target: str, feature_folders: list["FeatureFolder"]):
    for feature_folder in feature_folders:
        source = os.path.join(
            os.path.join(*[".."] * (feature_folder.relative_path_count + 2)),
            feature_folder.root,
            feature_folder.folder,
        )

        destination_folder = os.path.join(
            "targets", target, feature_folder.category_folder
        )
        destination = os.path.join(destination_folder, feature_folder.container_folder)

        os.makedirs(destination_folder, exist_ok=True)
        if os.path.lexists(destination):
            os.unlink(destination)
        os.symlink(source, destination)


def remove_links(target: str, feature_folders: list["FeatureFolder"]):
    for feature_folder in feature_folders:
        destination_folder = os.path.join(
            "targets", target, feature_folder.category_folder
        )
        destination = os.path.join(destination_folder, feature_folder.container_folder)

        if os.path.lexists(destination):
            os.unlink(destination)

            # Remove empty parent directories up to targets/target
            current_dir = destination_folder
            target_base = os.path.join("targets", target)

            while current_dir != target_base and os.path.exists(current_dir):
                try:
                    if not os.listdir(current_dir):  # Directory is empty
                        os.rmdir(current_dir)
                        current_dir = os.path.dirname(current_dir)
                    else:
                        break  # Directory not empty, stop
                except OSError:
                    break  # Can't remove directory, stop


def discover_existing_links(target: str) -> list[str]:
    target_path = os.path.join("targets", target)
    existing_links: list[str] = []
    for root, dirs, files in os.walk(target_path):
        for name in dirs + files:
            full_path = os.path.join(root, name)
            if os.path.islink(full_path):
                existing_links.append(os.readlink(full_path))
    cleaned_links: list[str] = []
    for link in existing_links:
        parts = link.split(os.path.sep)
        cleaned_parts = [part for part in parts if part != ".."]
        if cleaned_parts:
            cleaned_links.append(os.path.sep.join(cleaned_parts))
    existing_links = cleaned_links
    return existing_links


def discover_broken_links(target_path: str) -> list["BrokenLink"]:
    broken_links: list[BrokenLink] = []
    for root, dirs, files in os.walk(target_path):
        for name in dirs + files:
            full_path = os.path.join(root, name)
            if os.path.islink(full_path):
                link_target = os.readlink(full_path)
                # Check if the link target exists
                if os.path.isabs(link_target):
                    # Absolute path
                    if not os.path.exists(link_target):
                        broken_links.append(
                            BrokenLink(path=full_path, destination=link_target)
                        )
                else:
                    # Relative path - resolve relative to the link's directory
                    resolved_target = os.path.join(
                        os.path.dirname(full_path), link_target
                    )
                    if not os.path.exists(resolved_target):
                        broken_links.append(
                            BrokenLink(path=full_path, destination=link_target)
                        )
    return broken_links


@dataclass(frozen=True)
class BrokenLink:
    path: str
    destination: str


class InstructionSet:
    target: str
    functions: list[str]
    function_names: list[str]
    _features: list[str]

    def __init__(self, target: str):
        self.target = target
        self.functions = []
        self.function_names = []
        self._features = []


    def extend(self, base: str,  feature_folder: "FeatureFolder"):
        if os.path.join(base, feature_folder.folder) in self._features:
            return
        self._features.append(os.path.join(base, feature_folder.folder))
        function_name, function_lines = feature_folder.make_script(base)
        self.function_names.append(function_name)
        self.functions.extend(function_lines)
        self.functions.append("")

    def read_content(self, fn: str, indent: str = "") -> list[str]:
        with open(fn, "r") as f:
            return [indent + line.rstrip() for line in f.readlines() if line.strip()]

    def make_unique_function_name(self, feature_folder: "FeatureFolder", fn: str) -> str:
        return "_".join(
            ["run"] + [cat.replace("-", "_") for cat in feature_folder.categories] +
            [feature_folder.name.replace("-", "_")] +
            [os.path.splitext(os.path.basename(fn))[0].replace("-", "_")]
        )
    def make_shell_function(self, fn: str, name: str) -> list[str]:
        lines = [
            f"function {name}() {{",
        ]
        lines.extend(self.read_content(fn, indent="    "))
        lines.append("}")
        return lines

    def make_single_updater(self) -> list[str]:
        lines = [
            "#!/bin/bash",
            "",
            "# DO NOT EDIT this script by hand, this script is generated!",
            "# Instead, edit the components and fundamentals and re-run compile-targets.py",
            "set -e",
            "",
            "source ~/.workstation-setup-config",
            'source "$WORKSTATION_INSTALLATION_PATH/_config.sh"',
            'source "$WORKSTATION_INSTALLATION_PATH/_setup_functions.sh"',
            '',
            'SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"'

        ]
        lines.append('if [ "$(pwd)" != "$SCRIPT_DIR" ]; then')
        lines.append('    echo "Please run this script from its own directory: $SCRIPT_DIR"')
        lines.append("    exit 1")
        lines.append("fi")
        lines.append(f'if [ "$WORKSTATION" != "{self.target}" ]; then')
        lines.append(f'    echo "This script is intended for \'"{self.target}"\', but you are running it on \'$WORKSTATION\'."')
        lines.append("    exit 1")
        lines.append("fi")
        lines.append("")
        lines.append("function help() {")
        lines.append('    echo "Usage: $0 <command>"')
        lines.append('    echo "Available commands:"')
        lines.append('    echo "  run_upgrade                   Run the full upgrade process"')
        lines.append('    echo "  brew_upgrade                  Update Homebrew and upgrade all packages"')
        lines.append('    echo "  brew_cleanup                  Cleanup old Homebrew packages and caches"')
        lines.append('    echo "  brew_upgrade_and_cleanup      Update Homebrew and upgrade all packages"')
        lines.append('    echo "  help                          Show this help message"')
        lines.append('    echo ""')
        lines.append('    echo "Included feature functions:"')
        for function_name in self.function_names:
            lines.append(f'    echo "  {function_name}"')
        lines.append('}')
        lines.append("")

        lines.append("function run_upgrade() {")
        lines.append("    mkdir -p .once")
        lines.append("    brew_upgrade")
        lines.append("")
        for function_name in self.function_names:
            lines.append(f"    {function_name}")
        lines.append("")
        lines.append("    brew_cleanup")
        lines.append("}")

        lines.append("function brew_upgrade_and_cleanup() {")
        lines.append("    brew_upgrade")
        lines.append("    brew_cleanup")
        lines.append("}")
        lines.append("")
        lines.append("function brew_upgrade() {")
        lines.append("    brew update")
        lines.append("    brew upgrade")
        lines.append("}")
        lines.append("")

        lines.append("function brew_cleanup() {")
        lines.append("    brew cleanup --prune=all --scrub")
        lines.append("}")
        lines.append("")

        lines.append("")
        lines.append("# Install function implementations")
        for function in self.functions:
            lines.append(function)
        lines.append("")
        lines.append("# Internal functions")
        lines.extend(run_once_function())
        lines.append("")
        lines.append('if [ $# -eq 0 ]; then')
        lines.append('    help')
        lines.append('    exit 0')
        lines.append('fi')
        lines.append("")
        lines.append('COMMAND="$1"')
        lines.append('if declare -F "$COMMAND" > /dev/null; then')
        lines.append('    "$@"')
        lines.append('else')
        lines.append('    echo "❌ Error: Unknown command \'$COMMAND\'" >&2')
        lines.append('    echo >&2 # Print a blank line for spacing')
        lines.append('    help')
        lines.append('    exit 1 # Exit with an error code')
        lines.append('fi')
        lines.append("")


        return lines



# def make_brew_install_function(brewlines: list[str]) -> list[str]:
#     lines = [
#         "function install_brew_packages() {",
#     ]
#     lines.append("    brew bundle -q --file=- <<EOF")
#     lines.extend(["        " + line for line in brewlines])
#     lines.append("EOF")
#     lines.append("}")
#     return lines




class FeatureFolder:
    root: str
    folder: str
    name: str
    categories: tuple[str, ...]
    contents: tuple[str, ...]
    selected: bool
    home: str

    def __init__(
        self,
        *,
        root: str,
        feature_folder: str,
        contents: tuple[str, ...],
        selected: bool = False,
        home: str
    ):
        categories, name = os.path.split(feature_folder)
        self.root=root
        self.folder=feature_folder
        self.name=denumbered_name(name)
        self.contents=contents
        self.home=home
        self.categories=tuple(
            [
                denumbered_name(category)
                for category in categories.split(os.path.sep)
            ]
        )
        self.selected=selected

    @classmethod
    def make(cls, root_dir: str, feature_folder: str, selected: bool = False) -> "FeatureFolder":
        if os.path.islink(os.path.join(root_dir, feature_folder)):
            home = os.path.abspath(os.path.join(root_dir, feature_folder, '..', os.readlink(os.path.join(root_dir, feature_folder))))
        else:
            home = os.path.abspath(os.path.join(root_dir, feature_folder))
        return cls(
            root=root_dir,
            feature_folder=feature_folder,
            selected=selected,
            home=home,
            contents=tuple(
                sorted(glob.glob(
                    "**",
                    root_dir=os.path.join(root_dir, feature_folder),
                    include_hidden=True,
                ))
            ),
        )


    def is_part_of_categories(self, categories: tuple[str, ...]) -> bool:
        if len(categories) >= len(self.categories):
            return False
        return self.categories[: len(categories)] == categories

    def is_in_category(self, categories: tuple[str, ...]) -> bool:
        return categories == self.categories

    @property
    def category_folder(self):
        return os.path.dirname(self.folder)

    @property
    def container_folder(self):
        return os.path.basename(self.folder)

    @property
    def relative_path_count(self):
        return len(self.categories)

    def make_script(self, base: str) -> tuple[str, list[str]]:
        shell_function_name = make_function_name(["install", base] + list(self.categories) + [self.name])
        function_names: list[str] = []
        functions: list[str] = []
        for content in self.contents:
            full_path = os.path.join(
                self.root, self.folder, content
            )
            if os.path.isfile(full_path):
                inner_function_name = make_function_name(["run", content])
                file_content = read_content(full_path)

                if content.endswith("Brewfile"):
                    function_names.append(inner_function_name)
                    functions.extend(make_shell_function_for_brewfile(inner_function_name, file_content, source_file_name=full_path, indent=4))
                if content.endswith("once.sh"):
                    lock_name = make_function_name(["install"] + list(self.categories) + [self.name, content])
                    function_names.append(f'_run_once "{lock_name}" {inner_function_name}')
                    functions.extend(make_shell_function(inner_function_name, file_content, source_file_name=full_path, indent=4, home=self.home))
                elif content.endswith(".sh"):
                    function_names.append(inner_function_name)
                    functions.extend(make_shell_function(inner_function_name, file_content, source_file_name=full_path, indent=4, home=self.home))

        lines = [
            f"function {shell_function_name}() {{",
            f"    echo \"Installing feature: {self.folder}\"",
        ]
        lines.extend(functions)
        lines.append("")
        for fn in function_names:
            lines.append(f"    {fn}")
        lines.append(f'    echo "  Feature ({self.folder}) installed successfully."')
        lines.append("}")
        return shell_function_name, lines


@dataclass(frozen=True)
class FeatureTree:
    name: str
    contents: tuple[Union["FeatureTree", "FeatureFolder"], ...]

    @classmethod
    def build(
        cls,
        feature_folders: list["FeatureFolder"],
        categories: tuple[str, ...] = tuple(),
    ) -> "FeatureTree":
        contents: list[FeatureFolder] = []
        children: list[FeatureFolder] = []

        for feature_folder in feature_folders:
            if feature_folder.is_in_category(categories):
                contents.append(feature_folder)
            elif feature_folder.is_part_of_categories(categories):
                children.append(feature_folder)

        sub_tree = []
        for category, _ in groupby(
            children, key=lambda ff: ff.categories[: len(categories) + 1]
        ):
            sub_tree.append(cls.build(children, categories=category))

        return cls(
            name="root" if not len(categories) else categories[-1],
            contents=tuple(sub_tree + contents),
        )


def read_content(fn: str, indent: int = 0) -> list[str]:
    with open(fn, "r") as f:
        return [" " * indent + line.rstrip() for line in f.readlines() if line.strip()]


def denumbered_name(name: str):
    matches = FEATURE_NAME_REGEX.match(name)
    if not matches:
        return name
    return matches.group(2)

def make_function_name(parts: list[str]) -> str:
    return "_".join([part.replace("-", "_").replace(".", "_").replace("//", "_") for part in parts])

def make_shell_function(name: str, content: list[str], indent: int = 0, home: str | None = None, source_file_name: str | None = None) -> list[str]:
    lines = [
        f"function {name}() {{",
    ]
    if source_file_name:
        lines.append(f"    # Source: {source_file_name}")
    if home:
        lines.append(f'    pushd . > /dev/null')
        lines.append(f'    cd "{home}"')
    lines.extend(["    " + line for line in content])
    if source_file_name:
        lines.append(f"    echo \"  [✓] Script ({source_file_name}) executed successfully.\"")
    else:
        lines.append(f"    echo \"  [✓] Functtion ({name}) executed successfully.\"")
    if home:
        lines.append(f'    popd > /dev/null')
    lines.append("}")
    if indent > 0:
        lines = [" " * indent + line for line in lines]
    return lines

def run_once_function() -> list[str]:
    lines = [
        "function _run_once() {",
        "    LOCK=$1",
        "    shift",
        "    if [ ! -f .once/installed-$LOCK-once ]; then",
        "        $@",
        "        touch .once/installed-$LOCK-once",
        "    fi",
        "}",
    ]
    return lines


def make_shell_function_for_brewfile(name: str, content: list[str], indent: int = 0, source_file_name: str | None = None) -> list[str]:
    lines = [
        f"function {name}() {{",
    ]
    if source_file_name:
        lines.append(f"    # Source: {source_file_name}")
    lines.append("    brew bundle -q --file=- <<EOF")
    lines.extend(["        " + line for line in content])
    lines.append("EOF")
    if source_file_name:
        lines.append(f"    echo \"  [✓] Brewfile ({source_file_name}) applied successfully.\"")
    lines.append("}")
    # Indent all lines except the "EOF"
    if indent > 0:
        lines = [" " * indent + line if line.strip() != "EOF" else line for line in lines]
    return lines


def selector_ui(
    components: FeatureTree, title: str = "Configuration"
) -> tuple[list[FeatureFolder], list[FeatureFolder], bool]:
    """
    Display a cursive UI for selecting components.
    Returns (unchecked_items, newly_selected_items)
    """
    # Store original state for each FeatureFolder
    original_state = {}
    current_state = {}
    expanded_trees = set()  # Track which FeatureTree items are expanded

    def collect_folders(tree: Union[FeatureTree, FeatureFolder], state_dict: dict):
        if isinstance(tree, FeatureFolder):
            state_dict[id(tree)] = tree.selected
        elif isinstance(tree, FeatureTree):
            for item in tree.contents:
                collect_folders(item, state_dict)

    collect_folders(components, original_state)
    current_state = original_state.copy()

    def flatten_tree(
        tree: FeatureTree, level: int = 0
    ) -> list[tuple[Union[FeatureTree, FeatureFolder], int]]:
        """Flatten tree structure for display with indentation levels"""
        items = []
        for item in tree.contents:
            items.append((item, level))
            if isinstance(item, FeatureTree) and id(item) in expanded_trees:
                items.extend(flatten_tree(item, level + 1))
        return items

    def main_ui(stdscr):
        curses.curs_set(0)  # Hide cursor
        curses.init_pair(
            1, curses.COLOR_BLACK, curses.COLOR_WHITE
        )  # Menu text (black on white)
        curses.init_pair(
            2, curses.COLOR_WHITE, curses.COLOR_RED
        )  # Selected line (white on red)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Changed items
        curses.init_pair(
            4, curses.COLOR_WHITE, curses.COLOR_BLUE
        )  # Title text (white on blue)

        stdscr.bkgd(" ", curses.color_pair(4))  # Blue background like raspi-config

        selected_index = 0
        scroll_offset = 0
        last_display_items = []
        last_selected = -1
        last_scroll_offset = -1
        needs_full_redraw = True
        menu_drawn = False

        while True:
            height, width = stdscr.getmaxyx()

            # Get flattened items for current display
            display_items = flatten_tree(components)

            # Calculate changes in entire tree
            added_count, removed_count = count_added_removed(
                components, original_state, current_state
            )

            # Calculate window dimensions
            menu_width = min(width - 4, 80)  # Max 80 chars wide, leave margins
            menu_height = min(
                height - 6, len(display_items) + 4
            )  # Leave space for borders and buttons
            menu_start_x = (width - menu_width) // 2
            menu_start_y = 2  # Start higher since title is now in border

            # Calculate visible items
            visible_height = menu_height - 4  # Account for borders and padding
            if selected_index < scroll_offset:
                scroll_offset = selected_index
            elif selected_index >= scroll_offset + visible_height:
                scroll_offset = selected_index - visible_height + 1

            # Calculate drawing coordinates first
            content_start_y = menu_start_y + 2
            content_start_x = menu_start_x + 2

            # Full redraw needed?
            full_redraw_needed = (
                needs_full_redraw
                or display_items != last_display_items
                or scroll_offset != last_scroll_offset
                or not menu_drawn
            )

            def draw_menu_item(item_index, force_redraw=False):
                """Draw a single menu item"""
                if item_index >= len(display_items):
                    return

                visible_index = item_index - scroll_offset
                if visible_index < 0 or visible_index >= visible_height:
                    return

                item, level = display_items[item_index]
                y = content_start_y + visible_index

                is_selected = item_index == selected_index
                color = curses.color_pair(2) if is_selected else curses.color_pair(1)

                # Create indentation
                indent = "  " * level
                text = ""

                if isinstance(item, FeatureTree):
                    # Expandable submenu
                    is_expanded = id(item) in expanded_trees
                    expand_icon = "▼" if is_expanded else "▶"
                    submenu_changes = count_changes(item, original_state, current_state)

                    if submenu_changes > 0:
                        text = f"{indent}{expand_icon} {item.name} (Changed: {submenu_changes})"
                        if not is_selected:
                            color = curses.color_pair(3)  # Changed items in cyan
                    else:
                        text = f"{indent}{expand_icon} {item.name}"

                elif isinstance(item, FeatureFolder):
                    # Checkbox
                    original = original_state[id(item)]
                    current = current_state[id(item)]

                    if original and current:
                        checkbox = "[X]"  # Originally selected, still selected
                    elif not original and current:
                        checkbox = "[X]*"  # Newly selected
                        if not is_selected:
                            color = curses.color_pair(3)  # Changed items in cyan
                    elif original and not current:
                        checkbox = "[ ]-"  # Newly unselected
                        if not is_selected:
                            color = curses.color_pair(3)  # Changed items in cyan
                    else:
                        checkbox = "[ ]"  # Originally unselected, still unselected

                    text = f"{indent}{checkbox} {item.name}"

                # Truncate text if too long
                if text:
                    max_text_width = menu_width - 4
                    if len(text) > max_text_width:
                        text = text[: max_text_width - 3] + "..."

                    try:
                        # Clear the line first with white background
                        line_clear = " " * (menu_width - 4)
                        stdscr.addstr(
                            y, content_start_x, line_clear, curses.color_pair(1)
                        )
                        stdscr.addstr(y, content_start_x, text, color)
                    except curses.error:
                        pass  # Ignore if we can't draw (screen too small)

            if full_redraw_needed:
                # Clear entire background first
                stdscr.clear()

                # Generate title text with change information
                if added_count > 0 or removed_count > 0:
                    if added_count > 0 and removed_count > 0:
                        title_text = (
                            f"{title} (added: {added_count}, removed: {removed_count})"
                        )
                    elif added_count > 0:
                        title_text = f"{title} (added: {added_count})"
                    else:
                        title_text = f"{title} (removed: {removed_count})"
                else:
                    title_text = f"{title} (nothing changed)"

                # Draw menu border with integrated title
                try:
                    # Fill menu area with white background
                    for y in range(menu_height):
                        for x in range(menu_width):
                            stdscr.addstr(
                                menu_start_y + y,
                                menu_start_x + x,
                                " ",
                                curses.color_pair(1),
                            )

                    # Top border with integrated title
                    if len(title_text) + 4 < menu_width:  # Check if title fits
                        # Calculate spacing for centered title
                        title_padding = (menu_width - len(title_text) - 4) // 2
                        left_border = "─" * title_padding
                        right_border = "─" * (
                            menu_width - len(title_text) - 4 - title_padding
                        )
                        top_border = f"┌{left_border} {title_text} {right_border}┐"
                    else:
                        # Fallback: truncate title if too long
                        max_title_len = menu_width - 6
                        truncated_title = (
                            title_text[:max_title_len] + "..."
                            if len(title_text) > max_title_len
                            else title_text
                        )
                        title_padding = (menu_width - len(truncated_title) - 4) // 2
                        left_border = "─" * title_padding
                        right_border = "─" * (
                            menu_width - len(truncated_title) - 4 - title_padding
                        )
                        top_border = f"┌{left_border} {truncated_title} {right_border}┐"

                    stdscr.addstr(
                        menu_start_y, menu_start_x, top_border, curses.color_pair(1)
                    )

                    # Side borders
                    for i in range(menu_height - 2):
                        stdscr.addstr(
                            menu_start_y + 1 + i,
                            menu_start_x,
                            "│",
                            curses.color_pair(1),
                        )
                        stdscr.addstr(
                            menu_start_y + 1 + i,
                            menu_start_x + menu_width - 1,
                            "│",
                            curses.color_pair(1),
                        )

                    # Bottom border
                    stdscr.addstr(
                        menu_start_y + menu_height - 1,
                        menu_start_x,
                        "└" + "─" * (menu_width - 2) + "┘",
                        curses.color_pair(1),
                    )
                except curses.error:
                    # Fallback to simple border if unicode fails
                    for y in range(menu_height):
                        for x in range(menu_width):
                            try:
                                stdscr.addstr(
                                    menu_start_y + y,
                                    menu_start_x + x,
                                    " ",
                                    curses.color_pair(1),
                                )
                            except curses.error:
                                pass

                    # Fallback top border with title
                    if len(title_text) + 4 < menu_width:
                        title_padding = (menu_width - len(title_text) - 4) // 2
                        left_border = "-" * title_padding
                        right_border = "-" * (
                            menu_width - len(title_text) - 4 - title_padding
                        )
                        top_border = f"+{left_border} {title_text} {right_border}+"
                    else:
                        max_title_len = menu_width - 6
                        truncated_title = (
                            title_text[:max_title_len] + "..."
                            if len(title_text) > max_title_len
                            else title_text
                        )
                        title_padding = (menu_width - len(truncated_title) - 4) // 2
                        left_border = "-" * title_padding
                        right_border = "-" * (
                            menu_width - len(truncated_title) - 4 - title_padding
                        )
                        top_border = f"+{left_border} {truncated_title} {right_border}+"

                    stdscr.addstr(
                        menu_start_y, menu_start_x, top_border, curses.color_pair(1)
                    )
                    for i in range(menu_height - 2):
                        stdscr.addstr(
                            menu_start_y + 1 + i,
                            menu_start_x,
                            "|",
                            curses.color_pair(1),
                        )
                        stdscr.addstr(
                            menu_start_y + 1 + i,
                            menu_start_x + menu_width - 1,
                            "|",
                            curses.color_pair(1),
                        )
                    stdscr.addstr(
                        menu_start_y + menu_height - 1,
                        menu_start_x,
                        "+" + "-" * (menu_width - 2) + "+",
                        curses.color_pair(1),
                    )

                # Draw buttons
                button_y = height - 2
                update_text = "[U]pdate"
                cancel_text = "[Q]uit"
                try:
                    stdscr.addstr(
                        button_y, width - 20, update_text, curses.color_pair(4)
                    )
                    stdscr.addstr(
                        button_y, width - 10, cancel_text, curses.color_pair(4)
                    )
                except curses.error:
                    pass

                menu_drawn = True

            # Draw/redraw menu items
            if full_redraw_needed:
                # Clear all content lines first, then draw items
                for i in range(visible_height):
                    y = content_start_y + i
                    line_clear = " " * (menu_width - 4)
                    try:
                        stdscr.addstr(
                            y, content_start_x, line_clear, curses.color_pair(1)
                        )
                    except curses.error:
                        pass

                # Draw all menu items
                for i in range(visible_height):
                    item_index = scroll_offset + i
                    draw_menu_item(item_index)

                # Draw scroll indicator if needed
                if len(display_items) > visible_height:
                    scroll_info = f"[{scroll_offset + 1}-{min(scroll_offset + visible_height, len(display_items))} of {len(display_items)}]"
                    try:
                        stdscr.addstr(
                            menu_start_y + menu_height - 1,
                            menu_start_x + menu_width - len(scroll_info) - 2,
                            scroll_info,
                            curses.color_pair(1),
                        )
                    except curses.error:
                        pass

                # Update tracking variables
                last_display_items = display_items.copy()
                last_scroll_offset = scroll_offset
                needs_full_redraw = False
                stdscr.refresh()

            elif selected_index != last_selected:
                # Only redraw the changed lines
                if last_selected >= 0:
                    draw_menu_item(last_selected)  # Redraw old selection
                draw_menu_item(selected_index)  # Redraw new selection
                stdscr.refresh()

            last_selected = selected_index

            # Handle input
            key = stdscr.getch()

            if key == curses.KEY_UP:
                if selected_index > 0:
                    selected_index -= 1
            elif key == curses.KEY_DOWN:
                if selected_index < len(display_items) - 1:
                    selected_index += 1
            elif key in [curses.KEY_ENTER, ord("\n"), ord("\r"), ord(" ")]:
                if selected_index < len(display_items):
                    item, level = display_items[selected_index]
                    if isinstance(item, FeatureTree):
                        # Toggle expand/collapse
                        if id(item) in expanded_trees:
                            expanded_trees.remove(id(item))
                        else:
                            expanded_trees.add(id(item))
                        needs_full_redraw = True
                    elif isinstance(item, FeatureFolder):
                        # Toggle checkbox
                        current_state[id(item)] = not current_state[id(item)]
                        needs_full_redraw = True
            elif key == ord("u") or key == ord("U"):
                # Update - calculate changes and return
                unchecked = []
                newly_selected = []

                def collect_changes(tree: Union[FeatureTree, FeatureFolder]):
                    if isinstance(tree, FeatureFolder):
                        original = original_state[id(tree)]
                        current = current_state[id(tree)]
                        if original and not current:
                            unchecked.append(tree)
                        elif not original and current:
                            newly_selected.append(tree)
                    elif isinstance(tree, FeatureTree):
                        for item in tree.contents:
                            collect_changes(item)

                collect_changes(components)
                return unchecked, newly_selected, True
            elif key == ord("q") or key == ord("Q"):
                # Cancel
                return [], [], False

    def count_changes(
        tree: Union[FeatureTree, FeatureFolder], original: dict, current: dict
    ) -> int:
        """Count number of changes in a tree/folder"""
        if isinstance(tree, FeatureFolder):
            return 1 if original[id(tree)] != current[id(tree)] else 0
        elif isinstance(tree, FeatureTree):
            total = 0
            for item in tree.contents:
                total += count_changes(item, original, current)
            return total
        return 0

    def count_added_removed(
        tree: Union[FeatureTree, FeatureFolder], original: dict, current: dict
    ) -> tuple[int, int]:
        """Count added and removed items separately. Returns (added_count, removed_count)"""
        if isinstance(tree, FeatureFolder):
            original_state = original[id(tree)]
            current_state = current[id(tree)]
            if not original_state and current_state:
                return (1, 0)  # Added
            elif original_state and not current_state:
                return (0, 1)  # Removed
            else:
                return (0, 0)  # No change
        elif isinstance(tree, FeatureTree):
            total_added = 0
            total_removed = 0
            for item in tree.contents:
                added, removed = count_added_removed(item, original, current)
                total_added += added
                total_removed += removed
            return (total_added, total_removed)
        return (0, 0)

    return curses.wrapper(main_ui)


if __name__ == "__main__":
    main(dict(os.environ), sys.argv[0], sys.argv[1:])
