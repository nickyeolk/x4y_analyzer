"""
Health check endpoints.
"""

from fastapi import APIRouter
from datetime import datetime, timezone

from src.api.models.responses import HealthResponse
from config.settings import settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        Health status and application info
    """
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        environment=settings.app_env,
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/readiness", response_model=HealthResponse)
async def readiness_check() -> HealthResponse:
    """
    Readiness check endpoint for Kubernetes/load balancers.

    Returns:
        Readiness status
    """
    # In a real app, check dependencies (DB, LLM API, etc.)
    return HealthResponse(
        status="ready",
        version="0.1.0",
        environment=settings.app_env,
        timestamp=datetime.now(timezone.utc),
    )
