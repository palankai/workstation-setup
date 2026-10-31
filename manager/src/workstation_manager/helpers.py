"""Helpers for application *.py steps, which run with the manager's own interpreter."""

import os
from pathlib import Path

# The repository this package lives in; steps get the one being run from as WORKSTATION_ROOT
REPO_ROOT = Path(__file__).resolve().parents[3]


def app_id() -> str:
    return os.environ["APP_ID"]


def app_dir() -> Path:
    return Path(os.environ["APP_DIR"])


def repo_root() -> Path:
    return Path(os.environ.get("WORKSTATION_ROOT") or REPO_ROOT)
