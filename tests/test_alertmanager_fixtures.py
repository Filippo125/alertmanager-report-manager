import json
from pathlib import Path
from typing import Any

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "alertmanager"
SCENARIO_DIR = FIXTURE_DIR / "scenarios"

WEBHOOK_FIXTURES = {
    "webhook_firing_group.json": "firing",
    "webhook_resolved_group.json": "resolved",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "receiver",
    "status",
    "alerts",
    "groupLabels",
    "commonLabels",
    "commonAnnotations",
    "externalURL",
    "version",
    "groupKey",
    "truncatedAlerts",
}

REQUIRED_ALERT_FIELDS = {
    "status",
    "labels",
    "annotations",
    "startsAt",
    "endsAt",
    "generatorURL",
    "fingerprint",
}

REQUIRED_CUSTOM_LABELS = {
    "team",
    "service",
    "category",
    "criticality",
    "ticket_policy",
}


def load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def load_scenario_fixture(scenario: str, name: str) -> dict[str, Any]:
    return json.loads((SCENARIO_DIR / scenario / name).read_text(encoding="utf-8"))


def test_alertmanager_fixture_names_are_stable() -> None:
    assert sorted(path.name for path in FIXTURE_DIR.glob("*.json")) == sorted(WEBHOOK_FIXTURES)


@pytest.mark.parametrize(("fixture_name", "expected_status"), WEBHOOK_FIXTURES.items())
def test_alertmanager_webhook_fixtures_match_supported_shape(
    fixture_name: str,
    expected_status: str,
) -> None:
    payload = load_fixture(fixture_name)

    assert REQUIRED_TOP_LEVEL_FIELDS.issubset(payload)
    assert payload["status"] == expected_status
    assert payload["version"] == "4"
    assert payload["externalURL"].endswith(".example.invalid")
    assert payload["truncatedAlerts"] == 0
    assert len(payload["alerts"]) >= 2
    assert isinstance(payload["groupLabels"], dict)
    assert isinstance(payload["commonLabels"], dict)
    assert isinstance(payload["commonAnnotations"], dict)
    assert REQUIRED_CUSTOM_LABELS.issubset(payload["commonLabels"])

    for alert in payload["alerts"]:
        assert REQUIRED_ALERT_FIELDS.issubset(alert)
        assert alert["status"] == expected_status
        assert isinstance(alert["labels"], dict)
        assert isinstance(alert["annotations"], dict)
        assert REQUIRED_CUSTOM_LABELS.issubset(alert["labels"])
        assert alert["fingerprint"]


def test_duplicate_delivery_scenario_replays_alert_and_adds_unique_event() -> None:
    first_call = load_scenario_fixture("duplicate_delivery", "first_call.json")
    second_call = load_scenario_fixture("duplicate_delivery", "second_call.json")

    assert first_call["status"] == "firing"
    assert second_call["status"] == "firing"
    assert first_call["groupKey"] == second_call["groupKey"]
    assert len(first_call["alerts"]) == 1
    assert len(second_call["alerts"]) == 2

    first_alert = first_call["alerts"][0]
    replayed_alert = second_call["alerts"][0]
    unique_alert = second_call["alerts"][1]

    assert first_alert["fingerprint"] == replayed_alert["fingerprint"]
    assert first_alert["startsAt"] == replayed_alert["startsAt"]
    assert first_alert["endsAt"] == replayed_alert["endsAt"]
    assert first_alert["status"] == replayed_alert["status"]

    assert unique_alert["fingerprint"] != first_alert["fingerprint"]
    assert unique_alert["startsAt"] != first_alert["startsAt"]
    assert unique_alert["labels"]["instance"] != first_alert["labels"]["instance"]
    assert unique_alert["labels"]["alertname"] == first_alert["labels"]["alertname"]
    assert unique_alert["labels"]["service"] == first_alert["labels"]["service"]
