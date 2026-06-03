"""SQLite database setup for alert history storage."""

from __future__ import annotations

import json
import sqlite3
from importlib import resources
from pathlib import Path
from typing import Any

from alertmanager_report_manager.ingestion import AlertmanagerWebhook

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


def store_alertmanager_webhook(
    connection: sqlite3.Connection,
    webhook: AlertmanagerWebhook,
) -> tuple[int, ...]:
    """Store each alert from a validated Alertmanager webhook as an event row."""
    payload_json = _dump_json(webhook.original_payload)
    event_ids: list[int] = []

    for alert in webhook.alerts:
        cursor = connection.execute(
            """
            INSERT INTO alert_events (
              fingerprint,
              status,
              starts_at,
              ends_at,
              generator_url,
              receiver,
              group_key,
              truncated_alerts,
              labels_json,
              annotations_json,
              payload_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                alert.fingerprint,
                alert.status,
                alert.starts_at,
                alert.ends_at,
                alert.generator_url,
                webhook.receiver,
                webhook.group_key,
                webhook.truncated_alerts,
                _dump_json(alert.labels),
                _dump_json(alert.annotations),
                payload_json,
            ),
        )
        event_ids.append(int(cursor.lastrowid))

    return tuple(event_ids)


def _dump_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
