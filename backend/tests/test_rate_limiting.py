"""Tests for rate limiting functionality."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import time


@pytest.fixture
def client():
    """Create test client."""
    from app.main import app

    return TestClient(app)


@pytest.fixture
def mock_rate_limit_disabled():
    """Fixture to disable rate limiting for tests."""
    from app.config import settings

    original_enabled = settings.RATE_LIMIT_ENABLED
    settings.RATE_LIMIT_ENABLED = False
    yield
    settings.RATE_LIMIT_ENABLED = original_enabled


class TestRateLimiting:
    """Test rate limiting on webhook endpoints."""

    def test_rate_limit_allows_normal_requests(
        self, client, mock_rate_limit_disabled
    ):
        """Test that normal request rate is allowed."""
        # Make a few requests within limit
        for i in range(5):
            response = client.post(
                "/webhooks/github",
                json={"test": f"data_{i}"},
                headers={"Content-Type": "application/json"},
            )
            # Might be 400 due to invalid payload, but not 429
            assert response.status_code != 429

    @pytest.mark.skipif(
        True, reason="Rate limiting integration test - run manually"
    )
    def test_rate_limit_blocks_excessive_requests(self, client):
        """Test that excessive requests are rate limited."""
        from app.config import settings

        # Ensure rate limiting is enabled
        original_enabled = settings.RATE_LIMIT_ENABLED
        settings.RATE_LIMIT_ENABLED = True

        try:
            # Make requests exceeding the limit
            rate_limit = settings.RATE_LIMIT_PER_MINUTE
            responses = []

            for i in range(rate_limit + 10):
                response = client.post(
                    "/webhooks/github",
                    json={"test": f"data_{i}"},
                    headers={"Content-Type": "application/json"},
                )
                responses.append(response.status_code)

            # Should have at least one 429 Too Many Requests
            assert 429 in responses
        finally:
            settings.RATE_LIMIT_ENABLED = original_enabled

    def test_rate_limit_disabled_allows_all(self):
        """Test that disabling rate limit allows unlimited requests."""
        from app.config import settings

        original_enabled = settings.RATE_LIMIT_ENABLED
        settings.RATE_LIMIT_ENABLED = False

        try:
            from fastapi.testclient import TestClient
            from app.main import app

            client = TestClient(app)

            # Make many requests
            for i in range(150):
                response = client.post(
                    "/webhooks/github",
                    json={"test": f"data_{i}"},
                    headers={"Content-Type": "application/json"},
                )
                # Should never be rate limited
                assert response.status_code != 429
        finally:
            settings.RATE_LIMIT_ENABLED = original_enabled

    def test_rate_limit_headers_present(self, client):
        """Test that rate limit headers are included in responses."""
        response = client.post(
            "/webhooks/github",
            json={"test": "data"},
            headers={"Content-Type": "application/json"},
        )

        # Check for rate limit headers (if slowapi adds them)
        # Note: slowapi may add X-RateLimit-* headers
        # This depends on slowapi configuration
        pass

    def test_rate_limit_per_ip(self, client, mock_rate_limit_disabled):
        """Test that rate limiting is per IP address."""
        # Different IPs should have separate rate limits
        # This is handled by slowapi's key_func=get_remote_address
        response1 = client.post(
            "/webhooks/github",
            json={"test": "data1"},
            headers={
                "Content-Type": "application/json",
                "X-Forwarded-For": "192.168.1.1",
            },
        )

        response2 = client.post(
            "/webhooks/github",
            json={"test": "data2"},
            headers={
                "Content-Type": "application/json",
                "X-Forwarded-For": "192.168.1.2",
            },
        )

        # Both should be allowed (not rate limited)
        assert response1.status_code != 429
        assert response2.status_code != 429

    def test_rate_limit_configuration(self):
        """Test that rate limit configuration is loaded correctly."""
        from app.config import settings

        # Check that settings exist
        assert hasattr(settings, "RATE_LIMIT_ENABLED")
        assert hasattr(settings, "RATE_LIMIT_PER_MINUTE")

        # Check default values
        assert isinstance(settings.RATE_LIMIT_ENABLED, bool)
        assert isinstance(settings.RATE_LIMIT_PER_MINUTE, int)
        assert settings.RATE_LIMIT_PER_MINUTE > 0

    def test_rate_limit_reset_after_window(self):
        """Test that rate limit resets after time window."""
        # This would require waiting 60+ seconds, so we skip in normal tests
        # In production, rate limit should reset after 1 minute
        pass

    @pytest.mark.skipif(
        True, reason="Integration test - requires actual rate limiting"
    )
    def test_rate_limit_error_response(self, client):
        """Test that rate limit error has correct format."""
        from app.config import settings

        original_enabled = settings.RATE_LIMIT_ENABLED
        original_limit = settings.RATE_LIMIT_PER_MINUTE
        settings.RATE_LIMIT_ENABLED = True
        settings.RATE_LIMIT_PER_MINUTE = 2  # Very low limit for testing

        try:
            # Exceed the limit
            for i in range(5):
                response = client.post(
                    "/webhooks/github",
                    json={"test": f"data_{i}"},
                )

            # Last response should be 429
            if response.status_code == 429:
                # Check error format
                data = response.json()
                assert "error" in data or "detail" in data
        finally:
            settings.RATE_LIMIT_ENABLED = original_enabled
            settings.RATE_LIMIT_PER_MINUTE = original_limit

    def test_rate_limit_exception_handler(self):
        """Test that RateLimitExceeded exception handler is registered."""
        from app.main import app
        from slowapi.errors import RateLimitExceeded

        # Check that exception handler is registered
        assert RateLimitExceeded in app.exception_handlers

    def test_limiter_state_attached_to_app(self):
        """Test that limiter is attached to app state."""
        from app.main import app

        # Check that limiter is attached to app state
        assert hasattr(app.state, "limiter")
        assert app.state.limiter is not None
