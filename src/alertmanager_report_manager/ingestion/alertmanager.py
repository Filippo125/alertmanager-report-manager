"""Alertmanager webhook ingestion and validation."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from json import JSONDecodeError
from typing import Any, cast

ALLOWED_STATUSES = frozenset({"firing", "resolved"})

_TOP_LEVEL_FIELDS = (
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
)
_TOP_LEVEL_STRING_FIELDS = ("receiver", "externalURL", "version", "groupKey")
_TOP_LEVEL_OBJECT_FIELDS = ("groupLabels", "commonLabels", "commonAnnotations")
_ALERT_FIELDS = (
    "status",
    "labels",
    "annotations",
    "startsAt",
    "endsAt",
    "generatorURL",
    "fingerprint",
)
_ALERT_STRING_FIELDS = ("startsAt", "endsAt", "generatorURL", "fingerprint")
_ALERT_OBJECT_FIELDS = ("labels", "annotations")


@dataclass(frozen=True, slots=True)
class WebhookValidationError:
    """A validation problem tied to a stable payload path."""

    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"path": self.path, "message": self.message}


@dataclass(frozen=True, slots=True)
class IngestionResponse:
    """Predictable response shape for adapters such as CLIs or HTTP endpoints."""

    status_code: int
    body: dict[str, Any]


@dataclass(frozen=True, slots=True)
class AlertmanagerAlert:
    """Validated Alertmanager alert entry with its original object preserved."""

    status: str
    labels: Mapping[str, Any]
    annotations: Mapping[str, Any]
    starts_at: str
    ends_at: str
    generator_url: str
    fingerprint: str
    original_alert: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class AlertmanagerWebhook:
    """Validated Alertmanager webhook payload ready for downstream persistence."""

    receiver: str
    status: str
    alerts: tuple[AlertmanagerAlert, ...]
    group_labels: Mapping[str, Any]
    common_labels: Mapping[str, Any]
    common_annotations: Mapping[str, Any]
    external_url: str
    version: str
    group_key: str
    truncated_alerts: int
    original_payload: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class IngestionResult:
    """Accepted webhook or validation response."""

    accepted: bool
    response: IngestionResponse
    webhook: AlertmanagerWebhook | None = None
    errors: tuple[WebhookValidationError, ...] = ()


def ingest_alertmanager_webhook_json(raw_body: str | bytes | bytearray) -> IngestionResult:
    """Parse and validate a raw Alertmanager webhook JSON body."""
    try:
        payload = json.loads(raw_body)
    except (JSONDecodeError, UnicodeDecodeError, TypeError):
        return _reject((WebhookValidationError("$", "Malformed JSON body."),))

    return ingest_alertmanager_webhook_payload(payload)


def ingest_alertmanager_webhook_payload(payload: object) -> IngestionResult:
    """Validate an Alertmanager webhook payload object."""
    errors = _validate_payload(payload)
    if errors:
        return _reject(errors)

    webhook = _build_webhook(cast(Mapping[str, Any], payload))
    return IngestionResult(
        accepted=True,
        webhook=webhook,
        response=IngestionResponse(
            status_code=202,
            body={
                "status": "accepted",
                "message": "Alertmanager webhook payload accepted.",
                "receiver": webhook.receiver,
                "groupKey": webhook.group_key,
                "alertCount": len(webhook.alerts),
            },
        ),
    )


def _validate_payload(payload: object) -> tuple[WebhookValidationError, ...]:
    errors: list[WebhookValidationError] = []

    if not isinstance(payload, Mapping):
        return (WebhookValidationError("$", "Expected object."),)

    for field in _TOP_LEVEL_FIELDS:
        if field not in payload:
            errors.append(WebhookValidationError(f"$.{field}", "Missing required field."))

    if "status" in payload:
        _validate_status("$.status", payload["status"], errors)

    for field in _TOP_LEVEL_STRING_FIELDS:
        if field in payload:
            _validate_non_empty_string(f"$.{field}", payload[field], errors)

    for field in _TOP_LEVEL_OBJECT_FIELDS:
        if field in payload:
            _validate_mapping(f"$.{field}", payload[field], errors)

    if "truncatedAlerts" in payload:
        _validate_non_negative_integer("$.truncatedAlerts", payload["truncatedAlerts"], errors)

    if "alerts" in payload:
        _validate_alerts(payload["alerts"], errors)

    return tuple(errors)


def _validate_alerts(alerts: object, errors: list[WebhookValidationError]) -> None:
    if not isinstance(alerts, list):
        errors.append(WebhookValidationError("$.alerts", "Expected array."))
        return

    if not alerts:
        errors.append(WebhookValidationError("$.alerts", "Expected at least one alert."))
        return

    for index, alert in enumerate(alerts):
        alert_path = f"$.alerts[{index}]"
        if not isinstance(alert, Mapping):
            errors.append(WebhookValidationError(alert_path, "Expected object."))
            continue

        for field in _ALERT_FIELDS:
            if field not in alert:
                errors.append(
                    WebhookValidationError(f"{alert_path}.{field}", "Missing required field.")
                )

        if "status" in alert:
            _validate_status(f"{alert_path}.status", alert["status"], errors)

        for field in _ALERT_STRING_FIELDS:
            if field in alert:
                _validate_non_empty_string(f"{alert_path}.{field}", alert[field], errors)

        for field in _ALERT_OBJECT_FIELDS:
            if field in alert:
                _validate_mapping(f"{alert_path}.{field}", alert[field], errors)


def _validate_status(
    path: str,
    value: object,
    errors: list[WebhookValidationError],
) -> None:
    if not isinstance(value, str) or not value:
        errors.append(WebhookValidationError(path, "Expected non-empty string."))
        return

    if value not in ALLOWED_STATUSES:
        expected = ", ".join(sorted(ALLOWED_STATUSES))
        errors.append(WebhookValidationError(path, f"Expected one of: {expected}."))


def _validate_non_empty_string(
    path: str,
    value: object,
    errors: list[WebhookValidationError],
) -> None:
    if not isinstance(value, str) or not value:
        errors.append(WebhookValidationError(path, "Expected non-empty string."))


def _validate_mapping(
    path: str,
    value: object,
    errors: list[WebhookValidationError],
) -> None:
    if not isinstance(value, Mapping):
        errors.append(WebhookValidationError(path, "Expected object."))


def _validate_non_negative_integer(
    path: str,
    value: object,
    errors: list[WebhookValidationError],
) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        errors.append(WebhookValidationError(path, "Expected non-negative integer."))


def _build_webhook(payload: Mapping[str, Any]) -> AlertmanagerWebhook:
    alerts = tuple(
        AlertmanagerAlert(
            status=cast(str, alert["status"]),
            labels=cast(Mapping[str, Any], alert["labels"]),
            annotations=cast(Mapping[str, Any], alert["annotations"]),
            starts_at=cast(str, alert["startsAt"]),
            ends_at=cast(str, alert["endsAt"]),
            generator_url=cast(str, alert["generatorURL"]),
            fingerprint=cast(str, alert["fingerprint"]),
            original_alert=alert,
        )
        for alert in cast(list[Mapping[str, Any]], payload["alerts"])
    )

    return AlertmanagerWebhook(
        receiver=cast(str, payload["receiver"]),
        status=cast(str, payload["status"]),
        alerts=alerts,
        group_labels=cast(Mapping[str, Any], payload["groupLabels"]),
        common_labels=cast(Mapping[str, Any], payload["commonLabels"]),
        common_annotations=cast(Mapping[str, Any], payload["commonAnnotations"]),
        external_url=cast(str, payload["externalURL"]),
        version=cast(str, payload["version"]),
        group_key=cast(str, payload["groupKey"]),
        truncated_alerts=cast(int, payload["truncatedAlerts"]),
        original_payload=payload,
    )


def _reject(errors: tuple[WebhookValidationError, ...]) -> IngestionResult:
    return IngestionResult(
        accepted=False,
        errors=errors,
        response=IngestionResponse(
            status_code=400,
            body={
                "status": "error",
                "message": "Invalid Alertmanager webhook payload.",
                "errors": [error.as_dict() for error in errors],
            },
        ),
    )
