"""
Integration tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.mark.integration
class TestTicketAPI:
    """Test suite for ticket API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_create_billing_ticket(self, client):
        """Test creating a billing ticket."""
        ticket_data = {
            "customer_id": "C12345",
            "subject": "Billing issue",
            "body": "I was charged twice for my subscription",
            "email": "customer@example.com",
        }

        response = client.post("/tickets", json=ticket_data)
        assert response.status_code == 200

        data = response.json()
        assert "ticket_id" in data
        assert "correlation_id" in data
        assert "routing" in data
        assert "resolution" in data
        assert "agent_interactions" in data

    def test_create_technical_ticket(self, client):
        """Test creating a technical support ticket."""
        ticket_data = {
            "customer_id": "C67890",
            "subject": "API Error",
            "body": "Getting 500 errors when calling the API endpoint",
            "email": "dev@example.com",
        }

        response = client.post("/tickets", json=ticket_data)
        assert response.status_code == 200

        data = response.json()
        assert data["routing"]["assigned_agent"] in [
            "technical_agent",
            "escalation_agent",
        ]

    def test_create_ticket_with_category_hint(self, client):
        """Test creating a ticket with category hint."""
        ticket_data = {
            "customer_id": "C12345",
            "subject": "Need help",
            "body": "I have a question",
            "category_hint": "account",
            "email": "user@example.com",
        }

        response = client.post("/tickets", json=ticket_data)
        assert response.status_code == 200

        data = response.json()
        assert "ticket_id" in data

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Prometheus metrics format
        assert "python_gc_objects_collected_total" in response.text or "TYPE" in response.text
