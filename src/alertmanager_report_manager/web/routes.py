"""FastAPI route adapters."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from alertmanager_report_manager.ingestion import ingest_alertmanager_webhook_json
from alertmanager_report_manager.storage import connect, store_alertmanager_webhook

router = APIRouter()


@router.get(
    "/healthz",
    tags=["health"],
    summary="Return application health status.",
)
def healthz() -> JSONResponse:
    return JSONResponse(status_code=200, content={"status": "ok"})


@router.post(
    "/webhooks/alertmanager",
    status_code=202,
    tags=["webhooks"],
    summary="Ingest an Alertmanager webhook payload.",
    responses={
        202: {
            "description": "Alertmanager webhook payload accepted.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "accepted",
                        "message": "Alertmanager webhook payload accepted.",
                        "receiver": "alertmanager-report-manager",
                        "groupKey": '{}:{alertname="HighErrorRate"}',
                        "alertCount": 2,
                    }
                }
            },
        },
        400: {
            "description": "Invalid Alertmanager webhook payload.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Invalid Alertmanager webhook payload.",
                        "errors": [
                            {
                                "path": "$.receiver",
                                "message": "Missing required field.",
                            }
                        ],
                    }
                }
            },
        },
    },
)
async def ingest_alertmanager_webhook(request: Request) -> JSONResponse:
    raw_body = await request.body()
    result = ingest_alertmanager_webhook_json(raw_body)
    if result.accepted and result.webhook is not None:
        with connect(request.app.state.database_path) as connection:
            store_alertmanager_webhook(connection, result.webhook)

    return JSONResponse(status_code=result.response.status_code, content=result.response.body)
