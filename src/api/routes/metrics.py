"""
Prometheus metrics endpoint.
"""

from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from src.observability.metrics import registry

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics() -> Response:
    """
    Prometheus metrics endpoint.

    Returns:
        Prometheus metrics in text format
    """
    return Response(
        content=generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST,
    )
