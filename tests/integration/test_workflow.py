"""
Integration tests for ticket workflow orchestration.
"""

import pytest
from unittest.mock import patch

from src.orchestration.graph import TicketWorkflow


@pytest.mark.integration
@pytest.mark.asyncio
class TestTicketWorkflow:
    """Test suite for TicketWorkflow integration."""

    @pytest.fixture
    def workflow(self):
        """Create a TicketWorkflow instance."""
        return TicketWorkflow()

    @pytest.mark.asyncio
    async def test_billing_ticket_workflow(self, workflow):
        """Test complete workflow for a billing ticket."""
        result = await workflow.execute(
            ticket_id="TEST-001",
            correlation_id="test-corr-001",
            customer_id="C12345",
            subject="Billing issue",
            body="I was charged twice for my subscription",
            email="test@example.com",
        )

        # Assertions
        assert result is not None
        assert "routing" in result
        assert result["routing"]["assigned_agent"] in ["billing_agent", "escalation_agent"]
        assert "resolution" in result
        assert "agent_interactions" in result
        assert len(result["agent_interactions"]) >= 1

    @pytest.mark.asyncio
    async def test_technical_ticket_workflow(self, workflow):
        """Test complete workflow for a technical ticket."""
        result = await workflow.execute(
            ticket_id="TEST-002",
            correlation_id="test-corr-002",
            customer_id="C12345",
            subject="API Error",
            body="I'm getting 500 errors when calling the API",
            email="developer@example.com",
        )

        assert result is not None
        assert "routing" in result
        assert result["routing"]["assigned_agent"] in ["technical_agent", "escalation_agent"]
        assert "resolution" in result

    @pytest.mark.asyncio
    async def test_account_ticket_workflow(self, workflow):
        """Test complete workflow for an account ticket."""
        result = await workflow.execute(
            ticket_id="TEST-003",
            correlation_id="test-corr-003",
            customer_id="C67890",
            subject="Password reset",
            body="I need to reset my password",
            email="user@example.com",
        )

        assert result is not None
        assert "routing" in result
        assert result["routing"]["assigned_agent"] in ["account_agent", "escalation_agent"]
        assert "resolution" in result

    @pytest.mark.asyncio
    async def test_workflow_token_tracking(self, workflow):
        """Test that workflow tracks token usage."""
        result = await workflow.execute(
            ticket_id="TEST-004",
            correlation_id="test-corr-004",
            customer_id="C12345",
            subject="General inquiry",
            body="I have a question about your service",
            email="inquiry@example.com",
        )

        assert "metadata" in result
        assert "token_usage" in result["metadata"]
        # Should have token usage from at least triage
        assert len(result["metadata"]["token_usage"]) > 0

    @pytest.mark.asyncio
    async def test_workflow_with_category_hint(self, workflow):
        """Test workflow with category hint."""
        result = await workflow.execute(
            ticket_id="TEST-005",
            correlation_id="test-corr-005",
            customer_id="C12345",
            subject="Support request",
            body="I need help",
            category_hint="billing",
            email="help@example.com",
        )

        assert result is not None
        assert "ticket_content" in result
        assert result["ticket_content"].get("category_hint") == "billing"
