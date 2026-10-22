from dataclasses import dataclass
from pathlib import Path

from ruamel.yaml import YAML, YAMLError

from .catalog import CatalogError

SETTINGS = "settings.yaml"


@dataclass(frozen=True)
class SavedSearch:
    name: str
    query: str
    builtin: bool = False


BUILTIN_SEARCHES = tuple(
    SavedSearch(name, query, builtin=True)
    for name, query in [
        ("Fundamentals", "is:fundamental"),
        ("Deprecated", "is:deprecated"),
        ("Trial", "is:trial"),
        ("Archived", "is:archived"),
    ]
)


@dataclass(frozen=True)
class Settings:
    """Catalog-wide settings from applications/settings.yaml; the file is optional."""

    searches: tuple[SavedSearch, ...]


def load_settings(applications_dir: Path) -> Settings:
    path = applications_dir / SETTINGS
    data = {}
    if path.is_file():
        try:
            data = YAML(typ="safe").load(path.read_text()) or {}
        except YAMLError as e:
            raise CatalogError(f"{path}: invalid YAML: {e}") from None
        if not isinstance(data, dict):
            raise CatalogError(f"{path}: must be a mapping")

    searches = []
    for entry in data.get("searches") or []:
        if not (
            isinstance(entry, dict)
            and isinstance(entry.get("name"), str)
            and isinstance(entry.get("query"), str)
        ):
            raise CatalogError(f"{path}: each search needs a 'name' and a 'query'")
        searches.append(SavedSearch(entry["name"], entry["query"]))
    return Settings((*BUILTIN_SEARCHES, *searches))
