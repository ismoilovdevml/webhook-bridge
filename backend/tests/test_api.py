"""Tests for API endpoints."""
import pytest


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "webhook-bridge"


class TestDashboardEndpoint:
    """Test dashboard endpoint."""

    @pytest.mark.skip(reason="Integration test - requires real DB setup")
    def test_dashboard_stats(self, client):
        """Test dashboard stats endpoint."""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert "events" in data
        assert "distribution" in data


class TestProvidersEndpoint:
    """Test providers endpoint."""

    @pytest.mark.skip(reason="Integration test - requires real DB setup")
    def test_list_providers(self, client):
        """Test listing providers."""
        response = client.get("/api/providers")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
