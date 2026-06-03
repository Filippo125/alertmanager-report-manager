# Agent Guidelines

This repository contains AlertManager Report Manager, a lightweight reporting and analytics platform for Prometheus Alertmanager.

Use this file as guidance for coding agents working in this project.

## Project Context

- The product collects Alertmanager webhook events.
- It stores alert history for long-term analysis.
- It generates reports that help identify noisy alerts, recurring issues, monitoring gaps, and alert quality problems.
- The project is currently in an early stage, with the README defining the intended product direction.

## Technology Stack

- Primary language: Python.
- Python is preferred because the project needs strong data manipulation, alert aggregation, and HTML/PDF report generation capabilities.
- Runtime version: Python 3.11 or newer.
- Web framework: FastAPI for HTTP/API adapters, served by Uvicorn in local and container runtime usage.
- Database layer: SQLite via the Python standard library for the initial foundation.
- Package manager: standard `pip` editable install for now.
- Test command: `python -m pytest`.
- Format/lint command: `python -m ruff check .` and `python -m ruff format .`.

Do not introduce additional Python frameworks or reporting libraries until the project has a concrete implementation need. Prefer mature, well-maintained libraries that keep deployment and operations simple.

## Working Principles

- Keep changes tightly scoped to the requested task.
- Preserve the product direction described in `README.md`.
- Do not introduce a framework, database, queue, or report engine without a clear reason.
- Prefer simple, inspectable implementations before adding abstractions.
- Keep operational reporting concepts explicit: alerts, labels, annotations, receivers, firing/resolved states, grouping, recurrence, noise, ownership, and report periods.
- Document important product or architecture decisions when they affect future contributors.

## Expected Development Shape

When implementation starts, favor a structure that keeps these concerns separate:

- Webhook ingestion and validation.
- FastAPI route adapters and dependency wiring.
- Historical persistence.
- Alert normalization and classification.
- Report query logic.
- HTML/PDF report rendering.
- Configuration and deployment assets.

Avoid mixing ingestion, storage, analytics, and rendering logic in the same module unless the project is still being prototyped and the tradeoff is intentional.

## Testing Expectations

- Add focused tests for parsing, normalization, recurrence detection, and report aggregation logic.
- Include realistic Alertmanager webhook payload samples when testing ingestion behavior.
- Prefer deterministic tests for time-windowed reporting by injecting or fixing the clock.
- If adding a persistence layer, test schema migrations and query behavior.

## Documentation Expectations

- Keep user-facing documentation in English, matching the existing README style.
- Keep project documentation in `docs/` as plain Markdown until a documentation generator is needed.
- Update `README.md` when adding setup instructions, commands, architecture, or supported features.
- If adding configuration, document required and optional settings with examples.
- If adding APIs or webhook endpoints, document request shape, authentication assumptions, and expected responses.

## Safety Notes

- Do not discard existing user changes.
- Do not commit generated reports, local databases, secrets, credentials, or environment-specific files.
- Treat Alertmanager payloads as potentially sensitive because labels and annotations can contain hostnames, service names, owners, and incident details.
