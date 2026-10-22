"""Helpers for application *.py steps, which run with the manager's own interpreter."""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def app_id() -> str:
    return os.environ["APP_ID"]


def app_dir() -> Path:
    return Path(os.environ["APP_DIR"])
