"""
OpenRouter LLM client with observability and retry logic.

Provides access to GPT-4o via OpenRouter API with LangSmith integration.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from config.settings import settings
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

    Uses LangChain's ChatOpenAI for automatic LangSmith tracing.
    Provides observability, retry logic, and consistent interface.
    """

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

        # Initialize LangChain ChatOpenAI with OpenRouter endpoint
        self.llm = ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.7,  # Default, can be overridden
            max_tokens=4096,  # Default, can be overridden
            timeout=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
        )

        logger.info("openrouter_client_initialized", model=model, langsmith_enabled=settings.langchain_tracing_v2)

    async def generate(
        self,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate a response using OpenRouter API via LangChain.

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

            # Format messages for LangChain
            langchain_messages = [SystemMessage(content=system)]
            for msg in messages:
                if msg["role"] == "user":
                    langchain_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    # Note: For now we only support user messages after system
                    # Can extend to support multi-turn conversations later
                    pass

            # Estimate input tokens for logging
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
                # Update LLM config for this call
                llm_with_config = self.llm.bind(
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                # Call LangChain (automatically traced by LangSmith!)
                response = await llm_with_config.ainvoke(langchain_messages)

                # Extract content
                content = response.content

                # Get token usage from response metadata
                usage = response.response_metadata.get("token_usage", {})
                prompt_tokens = usage.get("prompt_tokens", estimated_input_tokens)
                completion_tokens = usage.get("completion_tokens", estimate_tokens(content))
                finish_reason = response.response_metadata.get("finish_reason", "stop")

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

    async def close(self):
        """Close resources (no-op for LangChain client)."""
        # LangChain handles its own connection pooling
        pass

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
