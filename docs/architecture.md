# Architecture

The project is intentionally small while the product shape is still being defined.

## Current Boundaries

* `alertmanager_report_manager.cli` exposes local operational commands.
* `alertmanager_report_manager.storage` owns database connections and schema initialization.
* Future ingestion, normalization, analytics, and rendering code should remain separate modules.

## Out of Scope for the Initial Foundation

* Web framework selection.
* Database abstraction layer or ORM.
* Report rendering engine.
* Background workers or queues.
