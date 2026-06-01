# Alertmanager Webhook Payloads

The project keeps reusable Alertmanager webhook samples in:

```text
tests/fixtures/alertmanager/
```

Current fixtures:

* `webhook_firing_group.json` contains a `firing` notification with multiple alerts in one group.
* `webhook_resolved_group.json` contains a `resolved` notification with multiple alerts in one group.

Scenario fixtures live under `tests/fixtures/alertmanager/scenarios/`:

* `duplicate_delivery/first_call.json` and `duplicate_delivery/second_call.json` represent
  consecutive deliveries where the second call replays the first firing alert event and adds one
  unique firing alert in the same Alertmanager group. The replayed alert intentionally keeps the
  same `groupKey`, alert `fingerprint`, alert status, and alert timestamps.

The fixtures are synthetic. They use reserved example hostnames, generic service names, and no real
customer names, secrets, hostnames, or incident details.

## Supported Payload Shape

The ingestion and storage work should assume the standard JSON webhook shape represented by the
fixtures:

* `receiver`: Alertmanager receiver name.
* `status`: group status, currently `firing` or `resolved`.
* `alerts`: one or more alert objects in the notification group.
* `groupLabels`: labels used by Alertmanager to group the notification.
* `commonLabels`: labels shared by every alert in the group.
* `commonAnnotations`: annotations shared by every alert in the group.
* `externalURL`: Alertmanager URL that emitted the notification.
* `version`: webhook payload version.
* `groupKey`: Alertmanager group key.
* `truncatedAlerts`: number of alerts omitted by Alertmanager.

Each alert object includes:

* `status`: alert status, currently `firing` or `resolved`.
* `labels`: alert labels.
* `annotations`: alert annotations.
* `startsAt`: alert start timestamp.
* `endsAt`: alert end timestamp, or Alertmanager's zero timestamp while firing.
* `generatorURL`: source Prometheus expression URL.
* `fingerprint`: stable Alertmanager alert fingerprint.

The fixture labels intentionally include operational dimensions that reports are expected to use:

* `team`
* `service`
* `category`
* `criticality`
* `ticket_policy`

Future tests can reference the fixtures by file name through `tests/fixtures/alertmanager`.
Scenario tests can reference ordered calls through `tests/fixtures/alertmanager/scenarios`.

## Deferred Fields

The current fixtures do not define behavior for:

* Non-JSON webhook bodies.
* Receiver-specific payload extensions outside the standard Alertmanager fields.
* Authentication headers or HTTP request metadata.
* Expanding omitted alerts when `truncatedAlerts` is greater than zero.
* Interpreting annotation URLs beyond storing and reporting them as annotation values.
* Rendering Alertmanager templates embedded in labels or annotations.

The ingestion interface rejects malformed JSON bodies and preserves the original decoded webhook
payload for downstream persistence even when only a subset of fields is normalized for reporting.
