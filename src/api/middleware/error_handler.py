"""
Global error handling middleware.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

from src.utils.errors import AgentLandError, ValidationError as CustomValidationError
from src.observability.context import get_correlation_id
from src.observability.logger import get_logger

logger = get_logger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """
    Global error handler for the application.

    Args:
        request: FastAPI request
        call_next: Next handler

    Returns:
        Response or error response
    """
    try:
        return await call_next(request)
    except AgentLandError as e:
        # Handle our custom exceptions
        correlation_id = get_correlation_id()
        error_type = type(e).__name__

        logger.error(
            "application_error",
            error_type=error_type,
            error=str(e),
            path=request.url.path,
        )

        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if isinstance(e, CustomValidationError):
            status_code = status.HTTP_400_BAD_REQUEST

        return JSONResponse(
            status_code=status_code,
            content={
                "error": error_type,
                "message": str(e),
                "correlation_id": correlation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
    except Exception as e:
        # Handle unexpected exceptions
        correlation_id = get_correlation_id()

        logger.exception(
            "unexpected_error",
            error=str(e),
            path=request.url.path,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "correlation_id": correlation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
