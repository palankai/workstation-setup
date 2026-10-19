from dataclasses import dataclass
from pathlib import Path

from .catalog import Catalog, load_catalog
from .profiles import Profile, list_profiles, load_profile

APPLICATIONS = "applications"
PROFILES = "profiles"


class WorkspaceError(Exception):
    pass


@dataclass(frozen=True)
class ProfileState:
    profile: Profile
    fundamentals: list[str]
    selected: list[str]
    implied: list[str]
    missing: list[str]
    install_order: list[str]


@dataclass(frozen=True)
class Workspace:
    """The workstation-setup repository: applications catalog plus profiles."""

    root: Path

    @classmethod
    def discover(cls, start: Path | None = None) -> "Workspace":
        start = (start or Path.cwd()).resolve()
        for candidate in (start, *start.parents):
            if (candidate / APPLICATIONS).is_dir() and (candidate / PROFILES).is_dir():
                return cls(candidate)
        raise WorkspaceError(
            f"No '{APPLICATIONS}' and '{PROFILES}' folders found from {start} upwards"
        )

    @property
    def applications_dir(self) -> Path:
        return self.root / APPLICATIONS

    @property
    def profiles_dir(self) -> Path:
        return self.root / PROFILES

    def catalog(self) -> Catalog:
        return load_catalog(self.applications_dir)

    def profiles(self) -> list[str]:
        return list_profiles(self.profiles_dir)

    def profile(self, name: str) -> Profile:
        return load_profile(self.profiles_dir, name)

    def state(self, name: str, catalog: Catalog | None = None) -> ProfileState:
        catalog = catalog or self.catalog()
        profile = self.profile(name)
        fundamentals = catalog.fundamentals
        selected = [
            ref for ref in profile.refs if ref in catalog and ref not in fundamentals
        ]
        missing = [ref for ref in profile.refs if ref not in catalog]
        install_order = catalog.resolve([*fundamentals, *selected])
        implied = [
            id for id in install_order if id not in selected and id not in fundamentals
        ]
        return ProfileState(
            profile, fundamentals, selected, implied, missing, install_order
        )

    def update_selection(self, name: str, ids: list[str]) -> ProfileState:
        catalog = self.catalog()
        for id in ids:
            catalog.get(id)
        profile = self.profile(name)
        unknown = [ref for ref in profile.refs if ref not in catalog]
        explicit = [id for id in ids if not catalog.get(id).fundamental]
        profile.set_selection([*explicit, *unknown])
        profile.save()
        return self.state(name, catalog)
