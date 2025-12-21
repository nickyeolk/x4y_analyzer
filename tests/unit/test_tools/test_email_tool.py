"""
Unit tests for Email Tool.
"""

import pytest
from unittest.mock import patch

from src.tools.email import EmailTool, EmailInput


@pytest.mark.asyncio
class TestEmailTool:
    """Test suite for EmailTool."""

    @pytest.fixture
    def tool(self):
        """Create an EmailTool instance."""
        return EmailTool()

    @pytest.mark.asyncio
    async def test_send_email_success(self, tool):
        """Test successful email sending."""
        # Mock random to always succeed
        with patch('src.tools.email.random.random', return_value=0.5):
            input_data = EmailInput(
                to="customer@example.com",
                subject="Your ticket has been resolved",
                body="Thank you for contacting support. Your issue has been resolved.",
                template="ticket_resolved",
            )

            result = await tool.execute(input_data)

            assert result.success is True
            assert result.result["success"] is True
            assert result.result["recipient"] == "customer@example.com"
            assert "message_id" in result.result
            assert result.result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_send_email_failure(self, tool):
        """Test email sending failure."""
        # Mock random to always fail
        with patch('src.tools.email.random.random', return_value=0.01):
            input_data = EmailInput(
                to="customer@example.com",
                subject="Test email",
                body="Test body",
            )

            result = await tool.execute(input_data)

            assert result.success is True  # Tool execution succeeded
            assert result.result["success"] is False  # Email sending failed
            assert "error" in result.result
            assert result.result["retry_recommended"] is True

    @pytest.mark.asyncio
    async def test_email_with_template(self, tool):
        """Test email with custom template."""
        with patch('src.tools.email.random.random', return_value=0.5):
            input_data = EmailInput(
                to="test@example.com",
                subject="Welcome!",
                body="Welcome to our service",
                template="welcome",
            )

            result = await tool.execute(input_data)

            assert result.success is True
            assert result.result["subject"] == "Welcome!"
