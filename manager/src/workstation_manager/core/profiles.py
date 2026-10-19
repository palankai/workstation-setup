import re
from collections.abc import Iterable
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

from ruamel.yaml import YAML, YAMLError
from ruamel.yaml.comments import CommentedMap, CommentedSeq

REF = "$ref"
SUFFIX = ".yaml"
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


class ProfileError(Exception):
    pass


@dataclass(frozen=True)
class InlineEntry:
    """A profile entry that defines an application in place instead of a $ref."""

    label: str
    data: dict


def _yaml() -> YAML:
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.preserve_quotes = True
    return yaml


class Profile:
    def __init__(self, name: str, path: Path, document: CommentedMap):
        self.name = name
        self.path = path
        self._document = document

    @property
    def _entries(self) -> CommentedSeq:
        entries = self._document.get("applications")
        if entries is None:
            entries = self._document["applications"] = CommentedSeq()
        return entries

    @property
    def refs(self) -> list[str]:
        return [ref for ref in map(_ref_of, self._entries) if ref is not None]

    @property
    def inline(self) -> list[InlineEntry]:
        return [
            InlineEntry(label=_label_of(entry), data=dict(entry))
            for entry in self._entries
            if _ref_of(entry) is None
        ]

    def set_selection(self, ids: Iterable[str]) -> None:
        """Make the $ref entries match ids; inline entries and comments are kept."""
        wanted = list(dict.fromkeys(ids))
        entries = self._entries
        for index in reversed(range(len(entries))):
            ref = _ref_of(entries[index])
            if ref is not None and ref not in wanted:
                _delete_keeping_comment(entries, index)
        existing = set(self.refs)
        for id in wanted:
            if id not in existing:
                entries.insert(self._insert_position(id), CommentedMap({REF: id}))

    def _insert_position(self, id: str) -> int:
        """Sorted position within the last block of sorted refs.

        Blocks end at a comment or blank line, or where sorting breaks, so
        hand-ordered blocks above (like fundamentals) are left alone.
        """
        entries = self._entries
        start = len(entries)
        previous = None
        for index in reversed(range(len(entries))):
            ref = _ref_of(entries[index])
            if ref is not None:
                if previous is not None and ref > previous:
                    break
                previous = ref
            start = index
            if index > 0 and _has_trailing_comment(entries[index - 1]):
                break
        end = start
        for index in range(start, len(entries)):
            ref = _ref_of(entries[index])
            if ref is None:
                continue
            if ref > id:
                return index
            end = index + 1
        return end

    def dump(self) -> str:
        stream = StringIO()
        _yaml().dump(self._document, stream)
        return stream.getvalue()

    def save(self) -> None:
        self.path.write_text(self.dump())


def _delete_keeping_comment(entries: CommentedSeq, index: int) -> None:
    # ruamel attaches a following comment or blank line to the entry above it
    entry = entries[index]
    trailing = None
    if isinstance(entry, CommentedMap) and entry:
        trailing = entry.ca.items.get(list(entry)[-1])
    if trailing and index > 0 and isinstance(entries[index - 1], CommentedMap):
        previous = entries[index - 1]
        last_key = list(previous)[-1]
        if last_key not in previous.ca.items:
            previous.ca.items[last_key] = trailing
    del entries[index]


def _has_trailing_comment(entry: object) -> bool:
    return isinstance(entry, CommentedMap) and bool(entry) and list(entry)[-1] in entry.ca.items


def _ref_of(entry: object) -> str | None:
    if isinstance(entry, dict) and REF in entry:
        return str(entry[REF])
    return None


def _label_of(entry: object) -> str:
    if isinstance(entry, dict):
        for key in ("application", "name", "id"):
            if key in entry:
                return str(entry[key])
    return str(entry)


def list_profiles(root: Path) -> list[str]:
    return sorted(p.stem for p in root.glob(f"*{SUFFIX}"))


def profile_path(root: Path, name: str) -> Path:
    if not NAME_RE.match(name):
        raise ProfileError(f"Invalid profile name '{name}'")
    return root / f"{name}{SUFFIX}"


def load_profile(root: Path, name: str) -> Profile:
    path = profile_path(root, name)
    if not path.exists():
        raise ProfileError(f"Profile '{name}' not found")
    try:
        document = _yaml().load(path.read_text())
    except YAMLError as e:
        raise ProfileError(f"{path}: invalid YAML: {e}") from None
    if document is None:
        document = CommentedMap()
    if not isinstance(document, CommentedMap):
        raise ProfileError(f"{path}: profile must be a mapping")
    entries = document.get("applications")
    if entries is not None and not isinstance(entries, CommentedSeq):
        raise ProfileError(f"{path}: 'applications' must be a list")
    return Profile(name, path, document)
