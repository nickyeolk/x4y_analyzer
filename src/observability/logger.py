"""
Structured logger wrapper with automatic trace context injection.
"""

import structlog
from typing import Any

from src.observability.tracer import get_current_trace_id, get_current_span_id


class ObservableLogger:
    """
    Logger wrapper that automatically adds trace context to log entries.
    """

    def __init__(self, name: str):
        """
        Initialize observable logger.

        Args:
            name: Logger name (typically module __name__)
        """
        self._logger = structlog.get_logger(name)

    def _bind_trace_context(self, **kwargs: Any) -> structlog.stdlib.BoundLogger:
        """Bind trace context to logger if available."""
        trace_id = get_current_trace_id()
        span_id = get_current_span_id()

        context = {}
        if trace_id:
            context["trace_id"] = trace_id
        if span_id:
            context["span_id"] = span_id

        return self._logger.bind(**context, **kwargs)

    def debug(self, event: str, **kwargs: Any) -> None:
        """Log debug message with trace context."""
        self._bind_trace_context(**kwargs).debug(event)

    def info(self, event: str, **kwargs: Any) -> None:
        """Log info message with trace context."""
        self._bind_trace_context(**kwargs).info(event)

    def warning(self, event: str, **kwargs: Any) -> None:
        """Log warning message with trace context."""
        self._bind_trace_context(**kwargs).warning(event)

    def error(self, event: str, **kwargs: Any) -> None:
        """Log error message with trace context."""
        self._bind_trace_context(**kwargs).error(event)

    def exception(self, event: str, **kwargs: Any) -> None:
        """Log exception with trace context."""
        self._bind_trace_context(**kwargs).exception(event)

    def bind(self, **kwargs: Any) -> "ObservableLogger":
        """
        Return a new logger with bound context.

        Args:
            **kwargs: Context to bind

        Returns:
            New logger instance with bound context
        """
        bound = ObservableLogger(self._logger._context.get("logger", __name__))
        bound._logger = self._logger.bind(**kwargs)
        return bound


def get_logger(name: str) -> ObservableLogger:
    """
    Get an observable logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        ObservableLogger instance

    Example:
        logger = get_logger(__name__)
        logger.info("agent_started", agent="triage")
    """
    return ObservableLogger(name)
