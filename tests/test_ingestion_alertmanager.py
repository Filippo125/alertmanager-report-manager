import copy
import json
from pathlib import Path
from typing import Any

import pytest

from alertmanager_report_manager.ingestion import (
    ingest_alertmanager_webhook_json,
    ingest_alertmanager_webhook_payload,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "alertmanager"


def load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("fixture_name", "expected_status"),
    (
        ("webhook_firing_group.json", "firing"),
        ("webhook_resolved_group.json", "resolved"),
    ),
)
def test_valid_alertmanager_webhook_payload_is_accepted(
    fixture_name: str,
    expected_status: str,
) -> None:
    payload = load_fixture(fixture_name)

    result = ingest_alertmanager_webhook_payload(payload)

    assert result.accepted is True
    assert result.errors == ()
    assert result.webhook is not None
    assert result.webhook.status == expected_status
    assert result.webhook.receiver == payload["receiver"]
    assert result.webhook.group_key == payload["groupKey"]
    assert result.webhook.original_payload is payload
    assert result.webhook.alerts[0].original_alert is payload["alerts"][0]
    assert result.response.status_code == 202
    assert result.response.body == {
        "status": "accepted",
        "message": "Alertmanager webhook payload accepted.",
        "receiver": payload["receiver"],
        "groupKey": payload["groupKey"],
        "alertCount": len(payload["alerts"]),
    }


def test_json_webhook_body_is_parsed_and_accepted() -> None:
    payload = load_fixture("webhook_firing_group.json")

    result = ingest_alertmanager_webhook_json(json.dumps(payload))

    assert result.accepted is True
    assert result.webhook is not None
    assert result.webhook.original_payload == payload


def test_missing_top_level_field_returns_validation_error() -> None:
    payload = load_fixture("webhook_firing_group.json")
    payload.pop("receiver")

    result = ingest_alertmanager_webhook_payload(payload)

    assert result.accepted is False
    assert result.webhook is None
    assert result.response.status_code == 400
    assert result.response.body["status"] == "error"
    assert result.response.body["message"] == "Invalid Alertmanager webhook payload."
    assert {"path": "$.receiver", "message": "Missing required field."} in result.response.body[
        "errors"
    ]


def test_missing_alert_field_returns_validation_error() -> None:
    payload = load_fixture("webhook_firing_group.json")
    payload["alerts"][0].pop("fingerprint")

    result = ingest_alertmanager_webhook_payload(payload)

    assert result.accepted is False
    assert {"path": "$.alerts[0].fingerprint", "message": "Missing required field."} in (
        result.response.body["errors"]
    )


def test_malformed_json_body_returns_validation_error() -> None:
    result = ingest_alertmanager_webhook_json('{"receiver":')

    assert result.accepted is False
    assert result.webhook is None
    assert result.response.status_code == 400
    assert result.response.body["errors"] == [{"path": "$", "message": "Malformed JSON body."}]


def test_malformed_payload_object_returns_validation_error() -> None:
    result = ingest_alertmanager_webhook_payload(["not", "an", "object"])

    assert result.accepted is False
    assert result.response.status_code == 400
    assert result.response.body["errors"] == [{"path": "$", "message": "Expected object."}]


def test_validation_does_not_mutate_original_payload() -> None:
    payload = load_fixture("webhook_firing_group.json")
    original = copy.deepcopy(payload)

    ingest_alertmanager_webhook_payload(payload)

    assert payload == original
