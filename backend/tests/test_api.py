"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self):
        """Test health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "webhook-bridge"


class TestDashboardEndpoint:
    """Test dashboard endpoint."""

    def test_dashboard_stats(self):
        """Test dashboard stats endpoint."""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert "events" in data
        assert "distribution" in data


class TestProvidersEndpoint:
    """Test providers endpoint."""

    def test_list_providers(self):
        """Test listing providers."""
        response = client.get("/api/providers")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
