"""
Retry logic with exponential backoff for LLM API calls.
"""

from typing import TypeVar, Callable, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log,
)
import logging

from src.utils.errors import LLMRateLimitError, LLMTimeoutError

logger = logging.getLogger(__name__)

T = TypeVar("T")


def create_retry_decorator(
    max_attempts: int = 3,
    min_wait: int = 2,
    max_wait: int = 10,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Create a retry decorator for LLM API calls.

    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)

    Returns:
        Retry decorator
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((LLMRateLimitError, LLMTimeoutError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO),
        reraise=True,
    )


# Default retry decorator
retry_on_llm_error = create_retry_decorator()
