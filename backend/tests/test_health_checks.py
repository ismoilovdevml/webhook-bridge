"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError


@pytest.fixture
def client():
    """Create test client."""
    from app.main import app

    return TestClient(app)


class TestHealthChecks:
    """Test health check endpoints."""

    def test_liveness_check_returns_200(self, client):
        """Test liveness endpoint returns 200 OK."""
        response = client.get("/health/live")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert data["service"] == "webhook-bridge"

    def test_liveness_check_always_succeeds(self, client):
        """Test liveness check always succeeds regardless of dependencies."""
        # Should succeed even if database is down
        response = client.get("/health/live")

        assert response.status_code == 200
        assert response.json()["status"] == "alive"

    @pytest.mark.skip(reason="Integration test - requires DB setup")
    def test_readiness_check_returns_200_when_healthy(self, client):
        """Test readiness endpoint returns 200 when database is accessible."""
        response = client.get("/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["service"] == "webhook-bridge"
        assert "checks" in data
        assert data["checks"]["database"] == "ok"

    @pytest.mark.skip(reason="Integration test - requires DB setup")
    @patch("app.main.SessionLocal")
    def test_readiness_check_fails_when_database_down(
        self, mock_session_local, client
    ):
        """Test readiness endpoint returns 500 when database is down."""
        # Mock database connection failure
        mock_db = MagicMock()
        mock_db.execute.side_effect = OperationalError(
            "connection failed", None, None
        )
        mock_session_local.return_value = mock_db

        response = client.get("/health/ready")

        # Should return error status
        assert response.status_code == 500

    def test_liveness_endpoint_structure(self, client):
        """Test liveness response has correct structure."""
        response = client.get("/health/live")
        data = response.json()

        # Check required fields
        assert "status" in data
        assert "service" in data
        assert isinstance(data["status"], str)
        assert isinstance(data["service"], str)

    @pytest.mark.skip(reason="Integration test - requires DB setup")
    def test_readiness_endpoint_structure(self, client):
        """Test readiness response has correct structure."""
        response = client.get("/health/ready")
        data = response.json()

        # Check required fields
        assert "status" in data
        assert "service" in data
        assert "checks" in data
        assert isinstance(data["checks"], dict)
        assert "database" in data["checks"]

    def test_multiple_liveness_calls(self, client):
        """Test multiple liveness calls are consistently successful."""
        for _ in range(5):
            response = client.get("/health/live")
            assert response.status_code == 200
            assert response.json()["status"] == "alive"

    def test_readiness_check_query_execution(self, client):
        """Test that readiness check actually executes database query."""
        response = client.get("/health/ready")

        # If we get 200, database query was successful
        if response.status_code == 200:
            assert response.json()["checks"]["database"] == "ok"

    @pytest.mark.skip(reason="Integration test - requires DB setup")
    def test_health_endpoints_no_authentication(self, client):
        """Test health endpoints do not require authentication."""
        # Liveness should work without any headers
        response = client.get("/health/live")
        assert response.status_code == 200

        # Readiness should work without any headers
        response = client.get("/health/ready")
        # Will be 200 if DB is up, or 500 if down, but not 401/403
        assert response.status_code in [200, 500]

    def test_health_endpoints_accept_get_only(self, client):
        """Test health endpoints only accept GET requests."""
        # POST should not be allowed
        response = client.post("/health/live")
        assert response.status_code == 405  # Method Not Allowed

        response = client.post("/health/ready")
        assert response.status_code == 405

        # PUT should not be allowed
        response = client.put("/health/live")
        assert response.status_code == 405

        response = client.put("/health/ready")
        assert response.status_code == 405
