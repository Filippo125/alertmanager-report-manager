"""Webhook ingestion boundaries."""

from alertmanager_report_manager.ingestion.alertmanager import (
    AlertmanagerAlert,
    AlertmanagerWebhook,
    IngestionResponse,
    IngestionResult,
    WebhookValidationError,
    ingest_alertmanager_webhook_json,
    ingest_alertmanager_webhook_payload,
)

__all__ = [
    "AlertmanagerAlert",
    "AlertmanagerWebhook",
    "IngestionResponse",
    "IngestionResult",
    "WebhookValidationError",
    "ingest_alertmanager_webhook_json",
    "ingest_alertmanager_webhook_payload",
]
