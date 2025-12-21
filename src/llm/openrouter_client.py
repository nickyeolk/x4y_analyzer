"""
OpenRouter LLM client with observability and retry logic.

Provides access to GPT-4o via OpenRouter API.
"""

import asyncio
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime

from config.settings import settings
from src.llm.retry import retry_on_llm_error
from src.llm.token_counter import estimate_tokens
from src.observability.logger import get_logger
from src.observability.tracer import trace_span, add_span_attributes
from src.observability.metrics import record_llm_usage
from src.utils.errors import LLMError

logger = get_logger(__name__)


class LLMResponse:
    """LLM response wrapper."""

    def __init__(
        self,
        content: str,
        prompt_tokens: int,
        completion_tokens: int,
        model: str,
        stop_reason: str = "stop",
    ):
        self.content = content
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = prompt_tokens + completion_tokens
        self.model = model
        self.stop_reason = stop_reason

    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "usage": {
                "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "total_tokens": self.total_tokens,
            },
            "model": self.model,
            "stop_reason": self.stop_reason,
        }


class OpenRouterClient:
    """
    OpenRouter client for accessing GPT-4o and other models.

    Provides observability, retry logic, and consistent interface.
    """

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = httpx.AsyncClient(timeout=settings.llm_timeout_seconds)
        logger.info("openrouter_client_initialized", model=model)

    async def generate(
        self,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate a response using OpenRouter API.

        Args:
            system: System prompt
            messages: Conversation messages
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            LLM response
        """
        with trace_span("llm.generate", {"model": self.model}):
            start_time = datetime.utcnow()

            # Format messages for OpenAI-compatible API
            formatted_messages = [{"role": "system", "content": system}]
            formatted_messages.extend(messages)

            # Estimate input tokens
            input_text = system + " ".join([m["content"] for m in messages])
            estimated_input_tokens = estimate_tokens(input_text)

            add_span_attributes(
                prompt_length=len(input_text),
                estimated_tokens=estimated_input_tokens,
            )

            logger.info(
                "llm_request_started",
                model=self.model,
                estimated_input_tokens=estimated_input_tokens,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            try:
                # Call OpenRouter API with retry logic
                response = await self._call_api_with_retry(
                    formatted_messages,
                    max_tokens,
                    temperature,
                )

                # Parse response
                content = response["choices"][0]["message"]["content"]
                usage = response["usage"]
                prompt_tokens = usage.get("prompt_tokens", estimated_input_tokens)
                completion_tokens = usage.get("completion_tokens", estimate_tokens(content))
                finish_reason = response["choices"][0].get("finish_reason", "stop")

                # Record metrics
                record_llm_usage(
                    model=self.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                )

                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

                logger.info(
                    "llm_request_completed",
                    model=self.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    duration_ms=duration_ms,
                    finish_reason=finish_reason,
                )

                add_span_attributes(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    finish_reason=finish_reason,
                )

                return LLMResponse(
                    content=content,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    model=self.model,
                    stop_reason=finish_reason,
                )

            except Exception as e:
                duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                logger.error(
                    "llm_request_failed",
                    model=self.model,
                    error=str(e),
                    error_type=type(e).__name__,
                    duration_ms=duration_ms,
                )
                raise LLMError(f"LLM request failed: {str(e)}") from e

    @retry_on_llm_error
    async def _call_api_with_retry(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
    ) -> Dict[str, Any]:
        """
        Call OpenRouter API with automatic retry on transient errors.

        Args:
            messages: Formatted messages
            max_tokens: Max tokens to generate
            temperature: Sampling temperature

        Returns:
            API response dict
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/startup-analyzer",  # Optional
            "X-Title": "Startup Analyzer",  # Optional
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        response = await self.client.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
        )

        if response.status_code != 200:
            error_text = response.text
            logger.error(
                "openrouter_api_error",
                status_code=response.status_code,
                error=error_text,
            )
            raise LLMError(f"OpenRouter API error: {response.status_code} - {error_text}")

        return response.json()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


def get_llm_client() -> OpenRouterClient:
    """
    Get configured LLM client instance.

    Returns:
        OpenRouterClient instance
    """
    if not settings.openrouter_api_key:
        logger.warning("openrouter_api_key_not_set",
                      message="OpenRouter API key not configured")
        raise ValueError("OPENROUTER_API_KEY environment variable must be set")

    return OpenRouterClient(
        api_key=settings.openrouter_api_key,
        model=settings.llm_model,
    )
