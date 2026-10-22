"""Selection logic shared by the server and future CLI; no web dependencies."""

from .catalog import EDITABLE_FLAGS, Application, Catalog, CatalogError, Step, load_catalog, set_flag
from .profiles import InlineEntry, Profile, ProfileError, list_profiles, load_profile
from .settings import SavedSearch, Settings, load_settings
from .workspace import ProfileState, Workspace, WorkspaceError

__all__ = [
    "EDITABLE_FLAGS",
    "Application",
    "Catalog",
    "CatalogError",
    "InlineEntry",
    "Profile",
    "ProfileError",
    "ProfileState",
    "SavedSearch",
    "Settings",
    "Step",
    "Workspace",
    "WorkspaceError",
    "list_profiles",
    "load_catalog",
    "load_profile",
    "load_settings",
    "set_flag",
]
