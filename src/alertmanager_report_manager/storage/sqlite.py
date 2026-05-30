"""SQLite database setup for alert history storage."""

from __future__ import annotations

import sqlite3
from importlib import resources
from pathlib import Path

SCHEMA_VERSION = 1


def connect(database_path: str | Path) -> sqlite3.Connection:
    """Open a SQLite connection with project defaults."""
    path = Path(database_path)
    if path != Path(":memory:"):
        path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(database_path: str | Path) -> None:
    """Create or update the SQLite database schema."""
    with connect(database_path) as connection:
        schema = resources.files("alertmanager_report_manager.storage").joinpath("schema.sql")
        connection.executescript(schema.read_text(encoding="utf-8"))


def get_schema_version(connection: sqlite3.Connection) -> int:
    """Return the latest applied schema version."""
    row = connection.execute("SELECT MAX(version) AS version FROM schema_migrations").fetchone()
    return int(row["version"])
