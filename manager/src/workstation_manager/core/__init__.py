"""Selection logic shared by the server and future CLI; no web dependencies."""

from .catalog import Application, Catalog, CatalogError, Step, load_catalog
from .profiles import InlineEntry, Profile, ProfileError, list_profiles, load_profile
from .workspace import ProfileState, Workspace, WorkspaceError

__all__ = [
    "Application",
    "Catalog",
    "CatalogError",
    "InlineEntry",
    "Profile",
    "ProfileError",
    "ProfileState",
    "Step",
    "Workspace",
    "WorkspaceError",
    "list_profiles",
    "load_catalog",
    "load_profile",
]
