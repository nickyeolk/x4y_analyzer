"""
Unit tests for Database Tool.
"""

import pytest

from src.tools.database import DatabaseTool, DatabaseQueryInput


@pytest.mark.asyncio
class TestDatabaseTool:
    """Test suite for DatabaseTool."""

    @pytest.fixture
    def tool(self):
        """Create a DatabaseTool instance."""
        return DatabaseTool()

    @pytest.mark.asyncio
    async def test_query_customer_info_found(self, tool):
        """Test querying existing customer information."""
        input_data = DatabaseQueryInput(
            query_type="customer_info",
            customer_id="C12345",
        )

        result = await tool.execute(input_data)

        assert result.success is True
        assert result.result["found"] is True
        assert result.result["customer"]["customer_id"] == "C12345"
        assert result.result["customer"]["name"] == "John Doe"
        assert result.result["customer"]["tier"] == "pro"

    @pytest.mark.asyncio
    async def test_query_customer_info_not_found(self, tool):
        """Test querying non-existent customer."""
        input_data = DatabaseQueryInput(
            query_type="customer_info",
            customer_id="C99999",
        )

        result = await tool.execute(input_data)

        assert result.success is True
        assert result.result["found"] is False
        assert "not found" in result.result["message"].lower()

    @pytest.mark.asyncio
    async def test_query_ticket_history(self, tool):
        """Test querying ticket history."""
        input_data = DatabaseQueryInput(
            query_type="ticket_history",
            customer_id="C12345",
            limit=5,
        )

        result = await tool.execute(input_data)

        assert result.success is True
        assert result.result["found"] is True
        assert len(result.result["tickets"]) > 0
        assert result.result["total_count"] == 2
        assert result.result["tickets"][0]["ticket_id"] == "T-001"

    @pytest.mark.asyncio
    async def test_query_payment_history(self, tool):
        """Test querying payment history."""
        input_data = DatabaseQueryInput(
            query_type="payment_history",
            customer_id="C67890",
            limit=10,
        )

        result = await tool.execute(input_data)

        assert result.success is True
        assert result.result["found"] is True
        assert len(result.result["payments"]) > 0
        assert result.result["payments"][0]["amount"] == 199.99

    @pytest.mark.asyncio
    async def test_invalid_query_type(self, tool):
        """Test with invalid query type."""
        input_data = DatabaseQueryInput(
            query_type="invalid_type",
            customer_id="C12345",
        )

        result = await tool.execute(input_data)

        assert result.success is True
        assert "error" in result.result
        assert "supported_types" in result.result
