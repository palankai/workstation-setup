from dataclasses import dataclass
from pathlib import Path

from .catalog import Catalog, load_catalog
from .profiles import Profile, list_profiles, load_profile
from .settings import Settings, load_settings

APPLICATIONS = "applications"
PROFILES = "profiles"


class WorkspaceError(Exception):
    pass


class UninstallError(Exception):
    pass


@dataclass(frozen=True)
class ProfileState:
    profile: Profile
    fundamentals: list[str]
    selected: list[str]
    implied: list[str]
    # Marked for uninstall; never selected or needed by what's installed
    uninstall: list[str]
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

    def settings(self) -> Settings:
        return load_settings(self.applications_dir)

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
        refs = [*profile.refs, *profile.uninstall]
        missing = list(dict.fromkeys(ref for ref in refs if ref not in catalog))
        install_order = catalog.resolve([*fundamentals, *selected])
        implied = [
            id for id in install_order if id not in selected and id not in fundamentals
        ]
        uninstall = [ref for ref in profile.uninstall if ref in catalog]
        return ProfileState(
            profile, fundamentals, selected, implied, uninstall, missing, install_order
        )

    def update_selection(self, name: str, ids: list[str]) -> ProfileState:
        """Whatever the new selection installs comes off the uninstall list."""
        catalog = self.catalog()
        installed = set(catalog.resolve([*catalog.fundamentals, *ids]))
        marked = self.state(name, catalog).uninstall
        return self.save_profile(name, ids, [id for id in marked if id not in installed])

    def save_profile(self, name: str, selected: list[str], uninstall: list[str]) -> ProfileState:
        """Writes the selection and the uninstall list; refs to unknown ids are kept.

        Fails if the uninstall list has fundamentals or anything the selection installs.
        """
        catalog = self.catalog()
        uninstall = [catalog.get(id).id for id in dict.fromkeys(uninstall)]
        explicit = [id for id in selected if not catalog.get(id).fundamental]
        if fundamentals := [id for id in uninstall if catalog.get(id).fundamental]:
            raise UninstallError(f"Fundamental, always installed: {', '.join(fundamentals)}")
        roots = [*catalog.fundamentals, *explicit]
        installed = catalog.resolve(roots)
        if needed := [id for id in uninstall if id in installed]:
            raise UninstallError("Still needed: " + "; ".join(_needed_by(catalog, roots, id) for id in needed))
        profile = self.profile(name)
        unknown = [ref for ref in profile.refs if ref not in catalog]
        unknown_uninstall = [ref for ref in profile.uninstall if ref not in catalog]
        profile.set_selection([*explicit, *unknown])
        profile.set_uninstall([*uninstall, *unknown_uninstall])
        profile.save()
        return self.state(name, catalog)

    def mark_uninstall(self, name: str, ids: list[str]) -> ProfileState:
        """Deselects the applications and puts them on the uninstall list."""
        state = self.state(name)
        selected = [id for id in state.selected if id not in ids]
        return self.save_profile(name, selected, [*state.uninstall, *ids])

    def keep(self, name: str, ids: list[str]) -> ProfileState:
        """Takes applications off the uninstall list; they stay unselected."""
        catalog = self.catalog()
        for id in ids:
            catalog.get(id)
        state = self.state(name, catalog)
        return self.save_profile(name, state.selected, [id for id in state.uninstall if id not in ids])


def _needed_by(catalog: Catalog, roots: list[str], id: str) -> str:
    users = [root for root in roots if root != id and id in catalog.resolve([root])]
    return f"{id} by {', '.join(users)}" if users else f"{id} is selected"
