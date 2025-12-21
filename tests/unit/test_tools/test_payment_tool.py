"""
Unit tests for Payment Tool.
"""

import pytest
from unittest.mock import patch

from src.tools.payment import PaymentTool, RefundInput, PaymentQueryInput


@pytest.mark.asyncio
class TestPaymentTool:
    """Test suite for PaymentTool."""

    @pytest.fixture
    def tool(self):
        """Create a PaymentTool instance."""
        return PaymentTool()

    @pytest.mark.asyncio
    async def test_process_refund_success(self, tool):
        """Test successful refund processing."""
        # Mock random to always succeed
        with patch('src.tools.payment.random.random', return_value=0.5):
            input_data = RefundInput(
                payment_id="PAY-12345",
                customer_id="C12345",
                amount=49.99,
                reason="Duplicate charge",
            )

            result = await tool.execute(input_data)

            assert result.success is True
            assert result.result["success"] is True
            assert result.result["payment_id"] == "PAY-12345"
            assert result.result["amount"] == 49.99
            assert result.result["status"] == "processed"
            assert "refund_id" in result.result

    @pytest.mark.asyncio
    async def test_process_refund_failure(self, tool):
        """Test refund processing failure."""
        # Mock random to always fail
        with patch('src.tools.payment.random.random', return_value=0.05):
            input_data = RefundInput(
                payment_id="PAY-12345",
                customer_id="C12345",
                amount=49.99,
                reason="Test refund",
            )

            result = await tool.execute(input_data)

            assert result.success is True  # Tool execution succeeded
            assert result.result["success"] is False  # Refund failed
            assert "error" in result.result
            assert result.result["retry_recommended"] is True

    @pytest.mark.asyncio
    async def test_query_payment(self, tool):
        """Test payment query."""
        input_data = PaymentQueryInput(
            payment_id="PAY-12345",
            customer_id="C12345",
        )

        result = await tool.execute(input_data)

        assert result.success is True
        assert result.result["found"] is True
        assert result.result["payment_id"] == "PAY-12345"
        assert result.result["status"] == "completed"
        assert "amount" in result.result
        assert "last4" in result.result

    @pytest.mark.asyncio
    async def test_large_refund_amount(self, tool):
        """Test refund with large amount."""
        with patch('src.tools.payment.random.random', return_value=0.5):
            input_data = RefundInput(
                payment_id="PAY-99999",
                customer_id="C99999",
                amount=999.99,
                reason="Service cancellation",
            )

            result = await tool.execute(input_data)

            assert result.success is True
            assert result.result["amount"] == 999.99
