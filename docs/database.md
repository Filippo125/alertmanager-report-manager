# Database

SQLite is the initial persistence target because it keeps local development and small deployments simple.

## Schema Management

The initial schema lives in `src/alertmanager_report_manager/storage/schema.sql`.

The `schema_migrations` table records applied schema versions. The first version creates the foundational `alert_events` table for storing normalized alert history alongside the original webhook payload.

Initialize a database file with:

```shell
alertmanager-report-manager init-db data/alerts.db
```

## Storage Model

The first schema stores alert event labels, annotations, and original payloads as JSON text. This avoids committing to an ORM or a richer relational model before the ingestion and reporting requirements are implemented.
