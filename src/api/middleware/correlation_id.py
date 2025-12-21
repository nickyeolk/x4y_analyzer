"""
Middleware for correlation ID injection.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import structlog

from src.observability.context import generate_correlation_id, set_correlation_id, get_correlation_id


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to inject correlation IDs into requests.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Process request and inject correlation ID.

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response with correlation ID header
        """
        # Check if correlation ID provided in header, otherwise generate
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = generate_correlation_id()

        # Set in context for the request
        set_correlation_id(correlation_id)

        # Bind to structlog context
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        # Process request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        # Clear context after request
        structlog.contextvars.clear_contextvars()

        return response
