"""
Decorators for automatic observability instrumentation.
"""

import time
import functools
import inspect
from typing import Any, Callable, TypeVar, cast

from src.observability.tracer import trace_span, add_span_attributes
from src.observability.logger import get_logger
from src.observability.metrics import (
    record_agent_invocation,
    record_agent_error,
    record_tool_call,
    record_tool_error,
)

F = TypeVar("F", bound=Callable[..., Any])

logger = get_logger(__name__)


def trace_agent(agent_name: str) -> Callable[[F], F]:
    """
    Decorator to automatically trace agent execution with observability.

    Args:
        agent_name: Name of the agent

    Returns:
        Decorated function

    Example:
        @trace_agent("triage")
        async def execute(self, state):
            ...
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            success = False

            with trace_span(f"agent.{agent_name}", {"agent.name": agent_name}):
                try:
                    logger.info(
                        "agent_started",
                        agent=agent_name,
                    )

                    result = await func(*args, **kwargs)
                    success = True

                    # Extract metadata if result is a dict with decision info
                    if isinstance(result, dict):
                        if "confidence" in result:
                            add_span_attributes(confidence=result["confidence"])
                        if "reasoning" in result:
                            add_span_attributes(reasoning=result["reasoning"])

                    duration = time.time() - start_time
                    logger.info(
                        "agent_completed",
                        agent=agent_name,
                        duration_seconds=duration,
                        success=True,
                    )

                    return result

                except Exception as e:
                    duration = time.time() - start_time
                    error_type = type(e).__name__

                    logger.error(
                        "agent_error",
                        agent=agent_name,
                        error=str(e),
                        error_type=error_type,
                        duration_seconds=duration,
                    )

                    record_agent_error(agent_name, error_type)
                    raise

                finally:
                    record_agent_invocation(agent_name, success)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            success = False

            with trace_span(f"agent.{agent_name}", {"agent.name": agent_name}):
                try:
                    logger.info(
                        "agent_started",
                        agent=agent_name,
                    )

                    result = func(*args, **kwargs)
                    success = True

                    if isinstance(result, dict):
                        if "confidence" in result:
                            add_span_attributes(confidence=result["confidence"])
                        if "reasoning" in result:
                            add_span_attributes(reasoning=result["reasoning"])

                    duration = time.time() - start_time
                    logger.info(
                        "agent_completed",
                        agent=agent_name,
                        duration_seconds=duration,
                        success=True,
                    )

                    return result

                except Exception as e:
                    duration = time.time() - start_time
                    error_type = type(e).__name__

                    logger.error(
                        "agent_error",
                        agent=agent_name,
                        error=str(e),
                        error_type=error_type,
                        duration_seconds=duration,
                    )

                    record_agent_error(agent_name, error_type)
                    raise

                finally:
                    record_agent_invocation(agent_name, success)

        # Return appropriate wrapper based on whether function is async
        if inspect.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        else:
            return cast(F, sync_wrapper)

    return decorator


def trace_tool(tool_name: str) -> Callable[[F], F]:
    """
    Decorator to automatically trace tool execution with observability.

    Args:
        tool_name: Name of the tool

    Returns:
        Decorated function

    Example:
        @trace_tool("payment_gateway")
        async def execute(self, input_data):
            ...
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            success = False

            with trace_span(f"tool.{tool_name}", {"tool.name": tool_name}):
                try:
                    # Log input if provided
                    if args and len(args) > 1:
                        add_span_attributes(tool_input=str(args[1]))

                    logger.info(
                        "tool_started",
                        tool=tool_name,
                    )

                    result = await func(*args, **kwargs)
                    success = True
                    duration = time.time() - start_time

                    logger.info(
                        "tool_completed",
                        tool=tool_name,
                        duration_seconds=duration,
                        success=True,
                    )

                    record_tool_call(tool_name, success, duration)
                    return result

                except Exception as e:
                    duration = time.time() - start_time
                    error_type = type(e).__name__

                    logger.error(
                        "tool_error",
                        tool=tool_name,
                        error=str(e),
                        error_type=error_type,
                        duration_seconds=duration,
                    )

                    record_tool_call(tool_name, success, duration)
                    record_tool_error(tool_name, error_type)
                    raise

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            success = False

            with trace_span(f"tool.{tool_name}", {"tool.name": tool_name}):
                try:
                    if args and len(args) > 1:
                        add_span_attributes(tool_input=str(args[1]))

                    logger.info(
                        "tool_started",
                        tool=tool_name,
                    )

                    result = func(*args, **kwargs)
                    success = True
                    duration = time.time() - start_time

                    logger.info(
                        "tool_completed",
                        tool=tool_name,
                        duration_seconds=duration,
                        success=True,
                    )

                    record_tool_call(tool_name, success, duration)
                    return result

                except Exception as e:
                    duration = time.time() - start_time
                    error_type = type(e).__name__

                    logger.error(
                        "tool_error",
                        tool=tool_name,
                        error=str(e),
                        error_type=error_type,
                        duration_seconds=duration,
                    )

                    record_tool_call(tool_name, success, duration)
                    record_tool_error(tool_name, error_type)
                    raise

        if inspect.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        else:
            return cast(F, sync_wrapper)

    return decorator
