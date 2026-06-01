import json
from pathlib import Path
from typing import Any

from alertmanager_report_manager.ingestion import ingest_alertmanager_webhook_payload
from alertmanager_report_manager.storage.sqlite import (
    SCHEMA_VERSION,
    connect,
    get_schema_version,
    initialize_database,
    store_alertmanager_webhook,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "alertmanager"


def load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


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


def test_store_alertmanager_webhook_inserts_alert_event_rows(tmp_path: Path) -> None:
    database_path = tmp_path / "alerts.db"
    payload = load_fixture("webhook_firing_group.json")
    ingestion_result = ingest_alertmanager_webhook_payload(payload)
    assert ingestion_result.webhook is not None

    initialize_database(database_path)
    with connect(database_path) as connection:
        event_ids = store_alertmanager_webhook(connection, ingestion_result.webhook)

    assert len(event_ids) == len(payload["alerts"])

    with connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT
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
            FROM alert_events
            ORDER BY id
            """
        ).fetchall()

    assert len(rows) == len(payload["alerts"])
    assert rows[0]["fingerprint"] == payload["alerts"][0]["fingerprint"]
    assert rows[0]["status"] == payload["alerts"][0]["status"]
    assert rows[0]["starts_at"] == payload["alerts"][0]["startsAt"]
    assert rows[0]["ends_at"] == payload["alerts"][0]["endsAt"]
    assert rows[0]["generator_url"] == payload["alerts"][0]["generatorURL"]
    assert rows[0]["receiver"] == payload["receiver"]
    assert rows[0]["group_key"] == payload["groupKey"]
    assert rows[0]["truncated_alerts"] == payload["truncatedAlerts"]
    assert json.loads(rows[0]["labels_json"]) == payload["alerts"][0]["labels"]
    assert json.loads(rows[0]["annotations_json"]) == payload["alerts"][0]["annotations"]
    assert json.loads(rows[0]["payload_json"]) == payload
