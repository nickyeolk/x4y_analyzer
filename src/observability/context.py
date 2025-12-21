"""
Context management for correlation IDs and request tracking.
"""

import uuid
from contextvars import ContextVar
from typing import Optional

# Context variable for correlation ID
correlation_id_var: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


def generate_correlation_id() -> str:
    """
    Generate a new correlation ID.

    Returns:
        UUID-based correlation ID
    """
    return f"CID-{uuid.uuid4().hex[:16]}"


def set_correlation_id(correlation_id: str) -> None:
    """
    Set the correlation ID for the current context.

    Args:
        correlation_id: Correlation ID to set
    """
    correlation_id_var.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    """
    Get the correlation ID for the current context.

    Returns:
        Current correlation ID or None
    """
    return correlation_id_var.get()


def get_or_create_correlation_id() -> str:
    """
    Get existing correlation ID or create a new one.

    Returns:
        Correlation ID
    """
    correlation_id = get_correlation_id()
    if correlation_id is None:
        correlation_id = generate_correlation_id()
        set_correlation_id(correlation_id)
    return correlation_id
