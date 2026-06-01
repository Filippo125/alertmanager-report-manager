"""Configuration helpers for the FastAPI adapter."""

from __future__ import annotations

import os
from pathlib import Path

DATABASE_PATH_ENV = "ALERTMANAGER_REPORT_MANAGER_DATABASE"
DEFAULT_DATABASE_PATH = Path("data/alerts.db")


def resolve_database_path(database_path: str | Path | None = None) -> Path:
    """Resolve the SQLite database path for the web adapter."""
    if database_path is not None:
        return Path(database_path)

    return Path(os.environ.get(DATABASE_PATH_ENV, DEFAULT_DATABASE_PATH))
