CREATE TABLE IF NOT EXISTS schema_migrations (
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS alert_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fingerprint TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('firing', 'resolved')),
  starts_at TEXT,
  ends_at TEXT,
  generator_url TEXT,
  receiver TEXT,
  group_key TEXT,
  truncated_alerts INTEGER NOT NULL DEFAULT 0,
  labels_json TEXT NOT NULL,
  annotations_json TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  received_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_alert_events_fingerprint
  ON alert_events (fingerprint);

CREATE INDEX IF NOT EXISTS idx_alert_events_received_at
  ON alert_events (received_at);

CREATE INDEX IF NOT EXISTS idx_alert_events_receiver
  ON alert_events (receiver);

INSERT OR IGNORE INTO schema_migrations (version)
VALUES (1);
