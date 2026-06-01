import json
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from alertmanager_report_manager.storage import connect
from alertmanager_report_manager.web import create_app

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "alertmanager"


def load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_healthz_returns_ok(tmp_path: Path) -> None:
    database_path = tmp_path / "alerts.db"

    with TestClient(create_app(database_path=database_path)) as client:
        response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert database_path.exists()


def test_alertmanager_webhook_accepts_firing_payload(tmp_path: Path) -> None:
    database_path = tmp_path / "alerts.db"
    payload = load_fixture("webhook_firing_group.json")

    with TestClient(create_app(database_path=database_path)) as client:
        response = client.post("/webhooks/alertmanager", json=payload)

    assert response.status_code == 202
    assert response.json() == {
        "status": "accepted",
        "message": "Alertmanager webhook payload accepted.",
        "receiver": payload["receiver"],
        "groupKey": payload["groupKey"],
        "alertCount": len(payload["alerts"]),
    }

    with connect(database_path) as connection:
        row = connection.execute("SELECT COUNT(*) AS total FROM alert_events").fetchone()
        assert row["total"] == len(payload["alerts"])


def test_alertmanager_webhook_accepts_resolved_payload(tmp_path: Path) -> None:
    database_path = tmp_path / "alerts.db"
    payload = load_fixture("webhook_resolved_group.json")

    with TestClient(create_app(database_path=database_path)) as client:
        response = client.post("/webhooks/alertmanager", json=payload)

    assert response.status_code == 202
    assert response.json()["alertCount"] == len(payload["alerts"])

    with connect(database_path) as connection:
        row = connection.execute("SELECT DISTINCT status FROM alert_events").fetchone()
        assert row["status"] == "resolved"


def test_alertmanager_webhook_rejects_missing_required_field(tmp_path: Path) -> None:
    database_path = tmp_path / "alerts.db"
    payload = load_fixture("webhook_firing_group.json")
    payload.pop("receiver")

    with TestClient(create_app(database_path=database_path)) as client:
        response = client.post("/webhooks/alertmanager", json=payload)

    assert response.status_code == 400
    assert {"path": "$.receiver", "message": "Missing required field."} in response.json()["errors"]

    with connect(database_path) as connection:
        row = connection.execute("SELECT COUNT(*) AS total FROM alert_events").fetchone()
        assert row["total"] == 0


def test_alertmanager_webhook_rejects_malformed_json(tmp_path: Path) -> None:
    database_path = tmp_path / "alerts.db"

    with TestClient(create_app(database_path=database_path)) as client:
        response = client.post(
            "/webhooks/alertmanager",
            content='{"receiver":',
            headers={"content-type": "application/json"},
        )

    assert response.status_code == 400
    assert response.json() == {
        "status": "error",
        "message": "Invalid Alertmanager webhook payload.",
        "errors": [{"path": "$", "message": "Malformed JSON body."}],
    }

    with connect(database_path) as connection:
        row = connection.execute("SELECT COUNT(*) AS total FROM alert_events").fetchone()
        assert row["total"] == 0
