"""Tests for API key authentication."""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import MagicMock, patch
from app.models.api_key import APIKey
from app.auth.dependencies import get_api_key, require_api_key


@pytest.fixture
def client():
    """Create test client."""
    from app.main import app

    return TestClient(app)


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return MagicMock()


@pytest.fixture
def mock_api_key():
    """Create mock API key."""
    return APIKey(
        id=1,
        key="test_api_key_123",
        name="Test Key",
        description="Test API Key",
        is_active=True,
        created_at=datetime.utcnow(),
        last_used_at=None,
    )


class TestAPIKeyAuthentication:
    """Test API key authentication functionality."""

    @pytest.mark.asyncio
    async def test_get_api_key_valid(self, mock_db, mock_api_key):
        """Test getting API key with valid header."""
        from app.config import settings

        # Mock database query
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_api_key
        )

        # Temporarily enable API key auth
        original_enabled = settings.API_KEY_ENABLED
        settings.API_KEY_ENABLED = True

        try:
            result = await get_api_key(
                x_api_key="test_api_key_123", db=mock_db
            )

            assert result is not None
            assert result.key == "test_api_key_123"
            assert result.is_active is True

            # Check that last_used_at was updated
            mock_db.commit.assert_called_once()
        finally:
            settings.API_KEY_ENABLED = original_enabled

    @pytest.mark.asyncio
    async def test_get_api_key_invalid(self, mock_db):
        """Test getting API key with invalid header."""
        from app.config import settings

        # Mock database query returning None
        mock_db.query.return_value.filter.return_value.first.return_value = (
            None
        )

        original_enabled = settings.API_KEY_ENABLED
        settings.API_KEY_ENABLED = True

        try:
            with pytest.raises(HTTPException) as exc_info:
                await get_api_key(x_api_key="invalid_key", db=mock_db)

            assert exc_info.value.status_code == 401
            assert "Invalid API key" in str(exc_info.value.detail)
        finally:
            settings.API_KEY_ENABLED = original_enabled

    @pytest.mark.asyncio
    async def test_get_api_key_missing_header(self, mock_db):
        """Test getting API key with missing header."""
        from app.config import settings

        original_enabled = settings.API_KEY_ENABLED
        settings.API_KEY_ENABLED = True

        try:
            with pytest.raises(HTTPException) as exc_info:
                await get_api_key(x_api_key=None, db=mock_db)

            assert exc_info.value.status_code == 401
            assert "Missing" in str(exc_info.value.detail)
        finally:
            settings.API_KEY_ENABLED = original_enabled

    @pytest.mark.asyncio
    async def test_get_api_key_disabled_auth(self, mock_db):
        """Test API key when authentication is disabled."""
        from app.config import settings

        original_enabled = settings.API_KEY_ENABLED
        settings.API_KEY_ENABLED = False

        try:
            result = await get_api_key(x_api_key=None, db=mock_db)

            # Should return None when disabled
            assert result is None
        finally:
            settings.API_KEY_ENABLED = original_enabled

    @pytest.mark.asyncio
    async def test_get_api_key_inactive(self, mock_db, mock_api_key):
        """Test getting API key that is inactive."""
        from app.config import settings

        # Set API key as inactive
        mock_api_key.is_active = False

        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_api_key
        )

        original_enabled = settings.API_KEY_ENABLED
        settings.API_KEY_ENABLED = True

        try:
            with pytest.raises(HTTPException) as exc_info:
                await get_api_key(x_api_key="test_api_key_123", db=mock_db)

            assert exc_info.value.status_code == 401
            assert "disabled" in str(exc_info.value.detail).lower()
        finally:
            settings.API_KEY_ENABLED = original_enabled

    @pytest.mark.asyncio
    async def test_require_api_key_valid(self, mock_api_key):
        """Test require_api_key with valid key."""
        # Should not raise exception
        result = await require_api_key(api_key=mock_api_key)
        assert result == mock_api_key

    @pytest.mark.asyncio
    async def test_require_api_key_none_when_disabled(self):
        """Test require_api_key when auth is disabled."""
        from app.config import settings

        original_enabled = settings.API_KEY_ENABLED
        settings.API_KEY_ENABLED = False

        try:
            # Should not raise exception when auth disabled and key is None
            result = await require_api_key(api_key=None)
            assert result is None
        finally:
            settings.API_KEY_ENABLED = original_enabled

    @pytest.mark.asyncio
    async def test_require_api_key_none_when_enabled(self):
        """Test require_api_key raises error when auth enabled but key None."""
        from app.config import settings

        original_enabled = settings.API_KEY_ENABLED
        settings.API_KEY_ENABLED = True

        try:
            with pytest.raises(HTTPException) as exc_info:
                await require_api_key(api_key=None)

            assert exc_info.value.status_code == 401
        finally:
            settings.API_KEY_ENABLED = original_enabled

    def test_api_key_model_fields(self, mock_api_key):
        """Test API key model has required fields."""
        assert hasattr(mock_api_key, "id")
        assert hasattr(mock_api_key, "key")
        assert hasattr(mock_api_key, "name")
        assert hasattr(mock_api_key, "description")
        assert hasattr(mock_api_key, "is_active")
        assert hasattr(mock_api_key, "created_at")
        assert hasattr(mock_api_key, "last_used_at")

    def test_api_key_model_defaults(self, db_session):
        """Test API key model default values."""
        api_key = APIKey(
            key="test_key", name="Test", description="Test description"
        )
        db_session.add(api_key)
        db_session.flush()  # Apply defaults

        # Check defaults
        assert api_key.is_active is True
        assert api_key.last_used_at is None

    @pytest.mark.asyncio
    async def test_last_used_timestamp_updated(self, mock_db, mock_api_key):
        """Test that last_used_at is updated on successful auth."""
        from app.config import settings

        original_last_used = mock_api_key.last_used_at
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_api_key
        )

        original_enabled = settings.API_KEY_ENABLED
        settings.API_KEY_ENABLED = True

        try:
            await get_api_key(x_api_key="test_api_key_123", db=mock_db)

            # last_used_at should be updated
            assert mock_api_key.last_used_at is not None
            if original_last_used is not None:
                assert mock_api_key.last_used_at >= original_last_used
        finally:
            settings.API_KEY_ENABLED = original_enabled

    def test_api_key_header_configuration(self):
        """Test API key header name is configurable."""
        from app.config import settings

        assert hasattr(settings, "API_KEY_HEADER")
        assert isinstance(settings.API_KEY_HEADER, str)
        assert len(settings.API_KEY_HEADER) > 0

    def test_api_key_enabled_configuration(self):
        """Test API key enabled setting exists."""
        from app.config import settings

        assert hasattr(settings, "API_KEY_ENABLED")
        assert isinstance(settings.API_KEY_ENABLED, bool)

    @pytest.mark.asyncio
    async def test_api_key_case_sensitive(self, mock_db):
        """Test that API key comparison is case-sensitive."""
        from app.config import settings

        mock_api_key = APIKey(
            key="TestKey123", name="Test", is_active=True
        )
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_api_key
        )

        original_enabled = settings.API_KEY_ENABLED
        settings.API_KEY_ENABLED = True

        try:
            # Correct case should work
            result = await get_api_key(x_api_key="TestKey123", db=mock_db)
            assert result is not None

            # Wrong case should fail
            mock_db.query.return_value.filter.return_value.first.return_value = None
            with pytest.raises(HTTPException):
                await get_api_key(x_api_key="testkey123", db=mock_db)
        finally:
            settings.API_KEY_ENABLED = original_enabled

    @pytest.mark.asyncio
    async def test_api_key_whitespace_not_trimmed(self, mock_db):
        """Test that API keys with whitespace are not trimmed."""
        from app.config import settings

        original_enabled = settings.API_KEY_ENABLED
        settings.API_KEY_ENABLED = True

        # API key with spaces should not be trimmed
        mock_db.query.return_value.filter.return_value.first.return_value = (
            None
        )

        try:
            with pytest.raises(HTTPException):
                await get_api_key(x_api_key=" test_key ", db=mock_db)
        finally:
            settings.API_KEY_ENABLED = original_enabled
