"""
OpenTelemetry tracer helpers for agent observability.
"""

from typing import Any, Optional
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from config.observability import get_tracer


@contextmanager
def trace_span(
    name: str,
    attributes: Optional[dict[str, Any]] = None,
    set_status_on_exception: bool = True,
):
    """
    Context manager for creating a trace span.

    Args:
        name: Span name
        attributes: Optional attributes to add to the span
        set_status_on_exception: Whether to set error status on exception

    Yields:
        The created span

    Example:
        with trace_span("agent_execution", {"agent": "triage"}):
            result = agent.execute()
    """
    tracer = get_tracer()
    with tracer.start_as_current_span(name) as span:
        if attributes:
            span.set_attributes(attributes)

        try:
            yield span
        except Exception as e:
            if set_status_on_exception:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
            raise


def add_span_attributes(**kwargs: Any) -> None:
    """
    Add attributes to the current span.

    Args:
        **kwargs: Attributes to add to the current span

    Example:
        add_span_attributes(agent="triage", confidence=0.95)
    """
    span = trace.get_current_span()
    if span.is_recording():
        for key, value in kwargs.items():
            # Convert complex types to strings
            if isinstance(value, (dict, list)):
                import json

                value = json.dumps(value)
            span.set_attribute(key, value)


def add_span_event(name: str, attributes: Optional[dict[str, Any]] = None) -> None:
    """
    Add an event to the current span.

    Args:
        name: Event name
        attributes: Optional event attributes

    Example:
        add_span_event("tool_called", {"tool": "payment_gateway", "success": True})
    """
    span = trace.get_current_span()
    if span.is_recording():
        span.add_event(name, attributes or {})


def get_current_trace_id() -> Optional[str]:
    """
    Get the current trace ID.

    Returns:
        Trace ID as hex string, or None if no active span
    """
    span = trace.get_current_span()
    if span.is_recording():
        trace_id = span.get_span_context().trace_id
        return format(trace_id, "032x")
    return None


def get_current_span_id() -> Optional[str]:
    """
    Get the current span ID.

    Returns:
        Span ID as hex string, or None if no active span
    """
    span = trace.get_current_span()
    if span.is_recording():
        span_id = span.get_span_context().span_id
        return format(span_id, "016x")
    return None
