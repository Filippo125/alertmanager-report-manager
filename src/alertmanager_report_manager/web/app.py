"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from alertmanager_report_manager import __version__
from alertmanager_report_manager.storage import initialize_database
from alertmanager_report_manager.web.config import resolve_database_path
from alertmanager_report_manager.web.routes import router


def create_app(database_path: str | Path | None = None) -> FastAPI:
    """Create the Alertmanager Report Manager ASGI application."""
    resolved_database_path = resolve_database_path(database_path)

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        initialize_database(resolved_database_path)
        yield

    application = FastAPI(
        title="Alertmanager Report Manager",
        version=__version__,
        description="Webhook ingestion and reporting API for Prometheus Alertmanager.",
        lifespan=lifespan,
    )
    application.state.database_path = resolved_database_path
    application.include_router(router)
    return application


app = create_app()
