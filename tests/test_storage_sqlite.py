from pathlib import Path

from alertmanager_report_manager.storage.sqlite import (
    SCHEMA_VERSION,
    connect,
    get_schema_version,
    initialize_database,
)


def test_initialize_database_creates_schema(tmp_path: Path) -> None:
    database_path = tmp_path / "alerts.db"

    initialize_database(database_path)

    with connect(database_path) as connection:
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

        assert {"alert_events", "schema_migrations"}.issubset(tables)
        assert get_schema_version(connection) == SCHEMA_VERSION


def test_initialize_database_is_idempotent(tmp_path: Path) -> None:
    database_path = tmp_path / "alerts.db"

    initialize_database(database_path)
    initialize_database(database_path)

    with connect(database_path) as connection:
        migration_rows = connection.execute("SELECT COUNT(*) AS total FROM schema_migrations")
        assert migration_rows.fetchone()["total"] == 1
