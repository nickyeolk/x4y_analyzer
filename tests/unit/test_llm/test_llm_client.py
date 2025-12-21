"""
Unit tests for LLM Client.
"""

import pytest
from unittest.mock import AsyncMock, patch

from src.llm.client import MockAnthropicClient, LLMClient, LLMResponse


@pytest.mark.asyncio
class TestMockAnthropicClient:
    """Test suite for MockAnthropicClient."""

    @pytest.fixture
    def client(self):
        """Create a MockAnthropicClient instance."""
        return MockAnthropicClient(api_key="test-key", model="claude-sonnet-4")

    @pytest.mark.asyncio
    async def test_generate_billing_response(self, client):
        """Test generating response for billing query."""
        system = "You are a triage agent."
        messages = [
            {"role": "user", "content": "I was charged twice for my subscription"}
        ]

        response = await client.generate(
            system=system,
            messages=messages,
            max_tokens=1000,
            temperature=0.0,
        )

        assert isinstance(response, LLMResponse)
        assert "billing_agent" in response.content.lower()
        assert response.prompt_tokens > 0
        assert response.completion_tokens > 0
        assert response.model == "claude-sonnet-4"

    @pytest.mark.asyncio
    async def test_generate_technical_response(self, client):
        """Test generating response for technical query."""
        system = "You are a triage agent."
        messages = [
            {"role": "user", "content": "The API is returning 500 errors"}
        ]

        response = await client.generate(
            system=system,
            messages=messages,
        )

        assert "technical_agent" in response.content.lower()
        assert response.total_tokens == response.prompt_tokens + response.completion_tokens

    @pytest.mark.asyncio
    async def test_generate_account_response(self, client):
        """Test generating response for account query."""
        system = "You are a triage agent."
        messages = [
            {"role": "user", "content": "I need to reset my password"}
        ]

        response = await client.generate(
            system=system,
            messages=messages,
        )

        assert "account_agent" in response.content.lower()


@pytest.mark.asyncio
class TestLLMClient:
    """Test suite for LLMClient."""

    @pytest.fixture
    def client(self):
        """Create an LLMClient instance."""
        with patch("src.llm.client.settings") as mock_settings:
            mock_settings.llm_model = "claude-sonnet-4"
            mock_settings.llm_max_tokens = 4096
            mock_settings.llm_temperature = 0.0
            mock_settings.llm_timeout_seconds = 30
            mock_settings.use_mock_llm = True
            mock_settings.anthropic_api_key = "test-key"
            client = LLMClient()
            return client

    @pytest.mark.asyncio
    async def test_generate_success(self, client):
        """Test successful LLM generation."""
        response = await client.generate(
            system="You are a helpful assistant.",
            user_message="Hello, how are you?",
            agent_name="test_agent",
        )

        assert isinstance(response, LLMResponse)
        assert len(response.content) > 0
        assert response.prompt_tokens > 0
        assert response.completion_tokens > 0

    @pytest.mark.asyncio
    async def test_get_usage_summary(self, client):
        """Test getting usage summary."""
        # Generate a response to track usage
        await client.generate(
            system="Test system",
            user_message="Test message",
        )

        summary = client.get_usage_summary()

        assert "total_prompt_tokens" in summary
        assert "total_completion_tokens" in summary
        assert "total_cost" in summary
        assert summary["total_prompt_tokens"] > 0

    @pytest.mark.asyncio
    async def test_reset_usage(self, client):
        """Test resetting usage tracking."""
        # Generate a response
        await client.generate(
            system="Test system",
            user_message="Test message",
        )

        # Reset usage
        client.reset_usage()

        # Check that usage is reset
        summary = client.get_usage_summary()
        assert summary["total_prompt_tokens"] == 0
        assert summary["total_completion_tokens"] == 0
        assert summary["total_cost"] == 0.0
