"""Tests for webhook signature validation."""

import pytest
import hmac
import hashlib
from fastapi import HTTPException
from app.utils.webhook_signature import (
    WebhookSignatureValidator,
    validate_webhook_signature,
)
from app.config import settings


class TestWebhookSignatureValidator:
    """Test webhook signature validation."""

    def test_github_signature_valid(self):
        """Test valid GitHub signature."""
        payload = b'{"test": "data"}'
        secret = "test_secret"

        # Create valid signature
        mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
        signature = mac.hexdigest()

        headers = {"x-hub-signature-256": f"sha256={signature}"}

        # Temporarily set webhook secret
        original_secret = settings.WEBHOOK_SECRET
        settings.WEBHOOK_SECRET = secret

        try:
            result = WebhookSignatureValidator.validate_github(headers, payload)
            assert result is True
        finally:
            settings.WEBHOOK_SECRET = original_secret

    def test_github_signature_invalid(self):
        """Test invalid GitHub signature."""
        payload = b'{"test": "data"}'
        headers = {"x-hub-signature-256": "sha256=invalid_signature"}

        settings.WEBHOOK_SECRET = "test_secret"

        with pytest.raises(HTTPException) as exc_info:
            WebhookSignatureValidator.validate_github(headers, payload)

        assert exc_info.value.status_code == 401
        assert "Invalid signature" in str(exc_info.value.detail)

    def test_github_signature_missing_header(self):
        """Test GitHub signature with missing header."""
        payload = b'{"test": "data"}'
        headers = {}

        settings.WEBHOOK_SECRET = "test_secret"

        with pytest.raises(HTTPException) as exc_info:
            WebhookSignatureValidator.validate_github(headers, payload)

        assert exc_info.value.status_code == 401

    def test_gitlab_token_valid(self):
        """Test valid GitLab token."""
        payload = b'{"test": "data"}'
        token = "test_secret"

        headers = {"x-gitlab-token": token}

        original_secret = settings.WEBHOOK_SECRET
        settings.WEBHOOK_SECRET = token

        try:
            result = WebhookSignatureValidator.validate_gitlab(headers, payload)
            assert result is True
        finally:
            settings.WEBHOOK_SECRET = original_secret

    def test_gitlab_token_invalid(self):
        """Test invalid GitLab token."""
        payload = b'{"test": "data"}'
        headers = {"x-gitlab-token": "wrong_token"}

        settings.WEBHOOK_SECRET = "correct_token"

        with pytest.raises(HTTPException) as exc_info:
            WebhookSignatureValidator.validate_gitlab(headers, payload)

        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)

    def test_bitbucket_signature_valid(self):
        """Test valid Bitbucket signature."""
        payload = b'{"test": "data"}'
        secret = "test_secret"

        mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
        signature = mac.hexdigest()

        headers = {"x-hub-signature": f"sha256={signature}"}

        original_secret = settings.WEBHOOK_SECRET
        settings.WEBHOOK_SECRET = secret

        try:
            result = WebhookSignatureValidator.validate_bitbucket(headers, payload)
            assert result is True
        finally:
            settings.WEBHOOK_SECRET = original_secret

    def test_validate_wrapper_github(self):
        """Test validate wrapper for GitHub."""
        payload = b'{"test": "data"}'
        secret = "test_secret"

        mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
        signature = mac.hexdigest()

        headers = {"x-hub-signature-256": f"sha256={signature}"}

        original_secret = settings.WEBHOOK_SECRET
        settings.WEBHOOK_SECRET = secret

        try:
            result = validate_webhook_signature("github", headers, payload)
            assert result is True
        finally:
            settings.WEBHOOK_SECRET = original_secret

    def test_validate_unknown_platform(self):
        """Test validation with unknown platform."""
        payload = b'{"test": "data"}'
        headers = {}

        # Should skip validation for unknown platforms
        result = validate_webhook_signature("unknown", headers, payload)
        assert result is True

    def test_validation_skipped_without_secret(self):
        """Test validation is skipped when WEBHOOK_SECRET is empty."""
        payload = b'{"test": "data"}'
        headers = {}

        original_secret = settings.WEBHOOK_SECRET
        settings.WEBHOOK_SECRET = ""

        try:
            result = WebhookSignatureValidator.validate_github(headers, payload)
            assert result is True
        finally:
            settings.WEBHOOK_SECRET = original_secret
