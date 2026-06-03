# Architecture

The project is intentionally small while the product shape is still being defined.

FastAPI is the selected web framework for HTTP adapters. The core ingestion, storage, analytics, and
rendering modules should remain framework-independent.

## Current Boundaries

* `alertmanager_report_manager.cli` exposes local operational commands.
* `alertmanager_report_manager.ingestion` validates Alertmanager webhook payloads and returns
  predictable adapter-friendly responses.
* `alertmanager_report_manager.storage` owns database connections and schema initialization.
* `alertmanager_report_manager.web` exposes FastAPI routes and dependency wiring without owning
  business logic.
* Future normalization, analytics, and rendering code should remain separate modules.

## Out of Scope for the Initial Foundation

* Database abstraction layer or ORM.
* Report rendering engine.
* Background workers or queues.
