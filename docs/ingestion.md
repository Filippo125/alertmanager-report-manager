# Webhook Ingestion

The ingestion boundary is a callable interface that HTTP adapters, CLIs, or tests can reuse without
coupling validation to persistence or report generation.

The first HTTP adapter uses FastAPI and exposes `POST /webhooks/alertmanager`. It delegates payload
parsing and validation to the callable interface documented here, then stores accepted alerts in
SQLite.

## Callable Interface

Import the Alertmanager ingestion helpers from:

```python
from alertmanager_report_manager.ingestion import (
    ingest_alertmanager_webhook_json,
    ingest_alertmanager_webhook_payload,
)
```

Use `ingest_alertmanager_webhook_json(raw_body)` when receiving a raw JSON webhook body as `str`,
`bytes`, or `bytearray`.

Use `ingest_alertmanager_webhook_payload(payload)` when the JSON body has already been decoded into
a Python object.

Both functions return an `IngestionResult` with:

* `accepted`: boolean acceptance flag.
* `response.status_code`: `202` for accepted payloads, `400` for validation errors.
* `response.body`: stable response object suitable for an HTTP JSON response.
* `webhook`: validated `AlertmanagerWebhook` when accepted, otherwise `None`.
* `errors`: validation errors when rejected.

Accepted results preserve the original decoded payload at `result.webhook.original_payload` so later
persistence code can store the complete Alertmanager delivery even when only selected fields are
normalized.

The HTTP endpoint writes only accepted payloads. Invalid or malformed payloads return validation
errors and do not insert alert event rows.

## Request Shape

The supported Alertmanager payload shape is documented in
[`alertmanager-webhook-payloads.md`](alertmanager-webhook-payloads.md). In summary, the top-level
object must include:

* `receiver`
* `status`
* `alerts`
* `groupLabels`
* `commonLabels`
* `commonAnnotations`
* `externalURL`
* `version`
* `groupKey`
* `truncatedAlerts`

Each alert object must include:

* `status`
* `labels`
* `annotations`
* `startsAt`
* `endsAt`
* `generatorURL`
* `fingerprint`

The accepted status values are `firing` and `resolved`. The `alerts` field must contain at least one
alert. Label and annotation fields must be objects. `truncatedAlerts` must be a non-negative integer.

## Responses

Accepted payloads return:

```json
{
  "status_code": 202,
  "body": {
    "status": "accepted",
    "message": "Alertmanager webhook payload accepted.",
    "receiver": "alertmanager-report-manager",
    "groupKey": "{}:{alertname=\"HighErrorRate\"}",
    "alertCount": 2
  }
}
```

Invalid payloads return `400` with path-specific validation errors:

```json
{
  "status_code": 400,
  "body": {
    "status": "error",
    "message": "Invalid Alertmanager webhook payload.",
    "errors": [
      {
        "path": "$.receiver",
        "message": "Missing required field."
      }
    ]
  }
}
```

Malformed JSON bodies are rejected before payload validation:

```json
{
  "status_code": 400,
  "body": {
    "status": "error",
    "message": "Invalid Alertmanager webhook payload.",
    "errors": [
      {
        "path": "$",
        "message": "Malformed JSON body."
      }
    ]
  }
}
```
