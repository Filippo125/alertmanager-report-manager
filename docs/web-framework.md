# Web Framework Decision

The selected web framework is **FastAPI**.

## Decision

Use FastAPI as the HTTP/API adapter layer for Alertmanager webhook ingestion and future report APIs.
Run it as an ASGI application, with Uvicorn as the default local and container server.

Initial dependency constraints:

```toml
dependencies = [
  "fastapi>=0.136,<0.137",
]

[project.optional-dependencies]
web = [
  "uvicorn[standard]>=0.47,<0.48",
]
```

FastAPI and Uvicorn are still pre-1.0 packages, so dependencies are minor-bounded. Upgrade one minor
line at a time with the full test suite and API smoke tests.

## Rationale

FastAPI fits this project better than a generic web framework because the first HTTP boundary is an
API-style webhook receiver, not a server-rendered web product.

The framework provides:

* OpenAPI and JSON Schema generation for request and response contracts.
* Pydantic-backed validation when the project is ready to move schema validation closer to HTTP
  adapters.
* Dependency injection for storage connections, authentication, configuration, and clock providers.
* ASGI support through Starlette for middleware, test clients, background tasks, lifecycle hooks,
  and future async integrations.
* A small enough surface area to keep ingestion, persistence, analytics, and report rendering in
  separate modules.

## Alternatives Considered

* **Starlette**: very lightweight and ASGI-native, but it would leave more manual work for OpenAPI,
  request schemas, and dependency wiring. It remains available underneath FastAPI.
* **Flask**: mature and extensible through extensions and application factories, but API validation,
  OpenAPI generation, and typed dependency wiring would require more third-party choices.
* **Django**: strong batteries-included ecosystem, but introduces an ORM, settings system, and app
  structure that are larger than this project's current ingestion and reporting needs.

## Architecture Rules

HTTP code lives under the `alertmanager_report_manager.web` package.

Routes should:

* Translate HTTP requests into calls to ingestion, storage, or report services.
* Return explicit response models.
* Use FastAPI dependencies for adapter concerns such as database connections, configuration, auth,
  and request metadata.

Routes should not:

* Implement Alertmanager parsing rules directly.
* Write SQL inline.
* Generate reports inline.
* Depend on process-global mutable state.

The current `alertmanager_report_manager.ingestion` callable interface stays framework-independent so
it can be tested directly and reused by non-HTTP adapters. The first HTTP adapter exposes
`POST /webhooks/alertmanager` and persists accepted alerts through the storage module.

## Sources

* [FastAPI features](https://fastapi.tiangolo.com/features/)
* [FastAPI dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
* [Starlette introduction](https://starlette.dev/)
* [Flask extensions](https://flask.palletsprojects.com/en/stable/extensions/)
* [Flask application factories](https://flask.palletsprojects.com/en/stable/patterns/appfactories/)
