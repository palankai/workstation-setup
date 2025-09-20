# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from dataclasses import dataclass
import os
import glob
import pprint
import re
import curses
from itertools import groupby
from typing import NamedTuple, Sequence, Union

FEATURE_FILES = [
    "Brewfile",
    "run.sh",
]

FEATURE_FILES_RE = re.compile(f".*({'|'.join(FEATURE_FILES)})$")
FEATURE_NAME_REGEX = re.compile(f"(.?..-)?(.*)$")


def main() -> None:
    targets = glob.glob("*", root_dir="targets")
    components = FeatureTree.build(discover("components"))

    print("Component tree:")
    pprint.pprint(components)
    print("\nLaunching selector UI... (Press 'u' to update, 'c' to cancel)")

    unchecked, newly_selected = selector_ui(components, "Component Selector")

    print(f"\nResults:")
    print(f"Unchecked items ({len(unchecked)}):")
    for item in unchecked:
        print(f"  - {item.name} ({item.folder})")

    print(f"Newly selected items ({len(newly_selected)}):")
    for item in newly_selected:
        print(f"  - {item.name} ({item.folder})")


def discover(root_dir: str) -> list["FeatureFolder"]:
    return [
        FeatureFolder.parse(feature_folder)
        for feature_folder, g in groupby(
            [
                os.path.dirname(setupfile)
                for setupfile in sorted(
                    glob.glob(
                        "**", recursive=True, root_dir=root_dir, include_hidden=True
                    )
                )
                if FEATURE_FILES_RE.match(setupfile)
            ]
        )
    ]


@dataclass
class FeatureFolder:
    folder: str
    name: str
    categories: tuple[str, ...]
    selected: bool

    @classmethod
    def parse(cls, feature_folder: str) -> "FeatureFolder":
        categories, name = os.path.split(feature_folder)
        return cls(
            folder=feature_folder,
            name=denumbered_name(name),
            categories=tuple(
                [
                    denumbered_name(category)
                    for category in categories.split(os.path.sep)
                ]
            ),
            selected=False,
        )

    def is_part_of_categories(self, categories: tuple[str, ...]) -> bool:
        if len(categories) >= len(self.categories):
            return False
        return self.categories[: len(categories)] == categories

    def is_in_category(self, categories: tuple[str, ...]) -> bool:
        return categories == self.categories


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


def denumbered_name(name: str):
    matches = FEATURE_NAME_REGEX.match(name)
    if not matches:
        return name
    return matches.group(2)


def selector_ui(components: FeatureTree, title: str = "Configuration") -> tuple[list[FeatureFolder], list[FeatureFolder]]:
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

    def flatten_tree(tree: FeatureTree, level: int = 0) -> list[tuple[Union[FeatureTree, FeatureFolder], int]]:
        """Flatten tree structure for display with indentation levels"""
        items = []
        for item in tree.contents:
            items.append((item, level))
            if isinstance(item, FeatureTree) and id(item) in expanded_trees:
                items.extend(flatten_tree(item, level + 1))
        return items

    def main_ui(stdscr):
        curses.curs_set(0)  # Hide cursor
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Menu text (black on white)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)     # Selected line (white on red)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)    # Changed items
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)    # Title text (white on blue)

        stdscr.bkgd(' ', curses.color_pair(4))  # Blue background like raspi-config

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
            added_count, removed_count = count_added_removed(components, original_state, current_state)

            # Calculate window dimensions
            menu_width = min(width - 4, 80)  # Max 80 chars wide, leave margins
            menu_height = min(height - 6, len(display_items) + 4)  # Leave space for borders and buttons
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
            full_redraw_needed = (needs_full_redraw or
                                display_items != last_display_items or
                                scroll_offset != last_scroll_offset or
                                not menu_drawn)

            def draw_menu_item(item_index, force_redraw=False):
                """Draw a single menu item"""
                if item_index >= len(display_items):
                    return

                visible_index = item_index - scroll_offset
                if visible_index < 0 or visible_index >= visible_height:
                    return

                item, level = display_items[item_index]
                y = content_start_y + visible_index

                is_selected = (item_index == selected_index)
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
                        text = text[:max_text_width - 3] + "..."

                    try:
                        # Clear the line first with white background
                        line_clear = " " * (menu_width - 4)
                        stdscr.addstr(y, content_start_x, line_clear, curses.color_pair(1))
                        stdscr.addstr(y, content_start_x, text, color)
                    except curses.error:
                        pass  # Ignore if we can't draw (screen too small)

            if full_redraw_needed:
                # Clear entire background first
                stdscr.clear()

                # Generate title text with change information
                if added_count > 0 or removed_count > 0:
                    if added_count > 0 and removed_count > 0:
                        title_text = f"{title} (added: {added_count}, removed: {removed_count})"
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
                            stdscr.addstr(menu_start_y + y, menu_start_x + x, " ", curses.color_pair(1))

                    # Top border with integrated title
                    if len(title_text) + 4 < menu_width:  # Check if title fits
                        # Calculate spacing for centered title
                        title_padding = (menu_width - len(title_text) - 4) // 2
                        left_border = "─" * title_padding
                        right_border = "─" * (menu_width - len(title_text) - 4 - title_padding)
                        top_border = f"┌{left_border} {title_text} {right_border}┐"
                    else:
                        # Fallback: truncate title if too long
                        max_title_len = menu_width - 6
                        truncated_title = title_text[:max_title_len] + "..." if len(title_text) > max_title_len else title_text
                        title_padding = (menu_width - len(truncated_title) - 4) // 2
                        left_border = "─" * title_padding
                        right_border = "─" * (menu_width - len(truncated_title) - 4 - title_padding)
                        top_border = f"┌{left_border} {truncated_title} {right_border}┐"

                    stdscr.addstr(menu_start_y, menu_start_x, top_border, curses.color_pair(1))

                    # Side borders
                    for i in range(menu_height - 2):
                        stdscr.addstr(menu_start_y + 1 + i, menu_start_x, "│", curses.color_pair(1))
                        stdscr.addstr(menu_start_y + 1 + i, menu_start_x + menu_width - 1, "│", curses.color_pair(1))

                    # Bottom border
                    stdscr.addstr(menu_start_y + menu_height - 1, menu_start_x, "└" + "─" * (menu_width - 2) + "┘", curses.color_pair(1))
                except curses.error:
                    # Fallback to simple border if unicode fails
                    for y in range(menu_height):
                        for x in range(menu_width):
                            try:
                                stdscr.addstr(menu_start_y + y, menu_start_x + x, " ", curses.color_pair(1))
                            except curses.error:
                                pass

                    # Fallback top border with title
                    if len(title_text) + 4 < menu_width:
                        title_padding = (menu_width - len(title_text) - 4) // 2
                        left_border = "-" * title_padding
                        right_border = "-" * (menu_width - len(title_text) - 4 - title_padding)
                        top_border = f"+{left_border} {title_text} {right_border}+"
                    else:
                        max_title_len = menu_width - 6
                        truncated_title = title_text[:max_title_len] + "..." if len(title_text) > max_title_len else title_text
                        title_padding = (menu_width - len(truncated_title) - 4) // 2
                        left_border = "-" * title_padding
                        right_border = "-" * (menu_width - len(truncated_title) - 4 - title_padding)
                        top_border = f"+{left_border} {truncated_title} {right_border}+"

                    stdscr.addstr(menu_start_y, menu_start_x, top_border, curses.color_pair(1))
                    for i in range(menu_height - 2):
                        stdscr.addstr(menu_start_y + 1 + i, menu_start_x, "|", curses.color_pair(1))
                        stdscr.addstr(menu_start_y + 1 + i, menu_start_x + menu_width - 1, "|", curses.color_pair(1))
                    stdscr.addstr(menu_start_y + menu_height - 1, menu_start_x, "+" + "-" * (menu_width - 2) + "+", curses.color_pair(1))

                # Draw buttons
                button_y = height - 2
                update_text = "[U]pdate"
                cancel_text = "[C]ancel"
                try:
                    stdscr.addstr(button_y, width - 20, update_text, curses.color_pair(4))
                    stdscr.addstr(button_y, width - 10, cancel_text, curses.color_pair(4))
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
                        stdscr.addstr(y, content_start_x, line_clear, curses.color_pair(1))
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
                        stdscr.addstr(menu_start_y + menu_height - 1, menu_start_x + menu_width - len(scroll_info) - 2, scroll_info, curses.color_pair(1))
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
                draw_menu_item(selected_index)     # Redraw new selection
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
            elif key in [curses.KEY_ENTER, ord('\n'), ord('\r'), ord(' ')]:
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
            elif key == ord('u') or key == ord('U'):
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
                return unchecked, newly_selected
            elif key == ord('c') or key == ord('C'):
                # Cancel
                return [], []

    def count_changes(tree: Union[FeatureTree, FeatureFolder], original: dict, current: dict) -> int:
        """Count number of changes in a tree/folder"""
        if isinstance(tree, FeatureFolder):
            return 1 if original[id(tree)] != current[id(tree)] else 0
        elif isinstance(tree, FeatureTree):
            total = 0
            for item in tree.contents:
                total += count_changes(item, original, current)
            return total
        return 0

    def count_added_removed(tree: Union[FeatureTree, FeatureFolder], original: dict, current: dict) -> tuple[int, int]:
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
    main()
