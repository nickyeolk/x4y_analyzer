"""
Unit tests for Triage Agent.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.triage_agent import TriageAgent
from src.llm.client import LLMResponse


@pytest.mark.asyncio
class TestTriageAgent:
    """Test suite for TriageAgent."""

    @pytest.fixture
    def agent(self):
        """Create a TriageAgent instance."""
        with patch("src.agents.triage_agent.get_llm_client"), \
             patch("src.agents.triage_agent.get_tool_registry"):
            agent = TriageAgent()
            agent.llm_client = AsyncMock()
            # Mock tool registry with AsyncMock for tool execution
            mock_tool = AsyncMock()
            mock_tool.execute = AsyncMock(return_value=AsyncMock(
                success=False,
                result={"found": False}
            ))
            agent.tool_registry = MagicMock()
            agent.tool_registry.get = MagicMock(return_value=mock_tool)
            return agent

    @pytest.mark.asyncio
    async def test_execute_billing_route(self, agent):
        """Test routing to billing agent."""
        # Setup mock LLM response
        agent.llm_client.generate = AsyncMock(
            return_value=LLMResponse(
                content="ROUTE: billing_agent | URGENCY: medium | CONFIDENCE: 0.92 | REASONING: Billing issue detected",
                prompt_tokens=100,
                completion_tokens=50,
                model="claude-sonnet-4",
            )
        )

        # Setup state
        state = {
            "ticket_content": {
                "subject": "Billing issue",
                "body": "I was charged twice",
            },
            "customer_context": {
                "customer_id": "C12345",
            },
            "timestamp": "2024-12-11T10:00:00",
        }

        # Execute
        result = await agent.execute(state)

        # Assertions
        assert "routing" in result
        assert result["routing"]["assigned_agent"] == "billing_agent"
        assert result["routing"]["urgency"] == "medium"
        assert result["routing"]["confidence_score"] == 0.92
        assert "agent_interactions" in result
        assert len(result["agent_interactions"]) == 1

    @pytest.mark.asyncio
    async def test_execute_technical_route(self, agent):
        """Test routing to technical agent."""
        agent.llm_client.generate = AsyncMock(
            return_value=LLMResponse(
                content="ROUTE: technical_agent | URGENCY: high | CONFIDENCE: 0.88 | REASONING: Technical error reported",
                prompt_tokens=100,
                completion_tokens=50,
                model="claude-sonnet-4",
            )
        )

        state = {
            "ticket_content": {
                "subject": "API error",
                "body": "Getting 500 error when calling the API",
            },
            "customer_context": {
                "customer_id": "C12345",
            },
            "timestamp": "2024-12-11T10:00:00",
        }

        result = await agent.execute(state)

        assert result["routing"]["assigned_agent"] == "technical_agent"
        assert result["routing"]["urgency"] == "high"

    @pytest.mark.asyncio
    async def test_parse_routing_response(self, agent):
        """Test parsing of routing response."""
        response = "ROUTE: account_agent | URGENCY: low | CONFIDENCE: 0.75 | REASONING: Account update needed"

        routing = agent._parse_routing_response(response)

        assert routing["assigned_agent"] == "account_agent"
        assert routing["urgency"] == "low"
        assert routing["confidence_score"] == 0.75
        assert "Account update needed" in routing["reasoning"]
