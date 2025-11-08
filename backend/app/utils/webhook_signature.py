"""Webhook signature validation for Git platforms."""

import hmac
import hashlib
from typing import Dict
from fastapi import HTTPException
from ..config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class WebhookSignatureValidator:
    """Validate webhook signatures from different Git platforms."""

    @staticmethod
    def validate_github(headers: Dict[str, str], payload: bytes) -> bool:
        """
        Validate GitHub webhook signature.

        GitHub sends X-Hub-Signature-256 header with HMAC-SHA256 signature.
        Format: sha256=<signature>
        """
        if not settings.WEBHOOK_SECRET:
            logger.warning("WEBHOOK_SECRET not set, skipping GitHub validation")
            return True  # Skip validation if secret not configured

        signature_header = headers.get("x-hub-signature-256", "")
        if not signature_header:
            # Fallback to older sha1 signature
            signature_header = headers.get("x-hub-signature", "")
            if not signature_header:
                raise HTTPException(
                    status_code=401, detail="Missing X-Hub-Signature-256 header"
                )
            algo = "sha1"
            signature = signature_header.replace("sha1=", "")
        else:
            algo = "sha256"
            signature = signature_header.replace("sha256=", "")

        # Compute expected signature
        if algo == "sha256":
            mac = hmac.new(
                settings.WEBHOOK_SECRET.encode(),
                msg=payload,
                digestmod=hashlib.sha256,
            )
        else:
            mac = hmac.new(
                settings.WEBHOOK_SECRET.encode(),
                msg=payload,
                digestmod=hashlib.sha1,
            )

        expected_signature = mac.hexdigest()

        # Compare signatures
        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

        return True

    @staticmethod
    def validate_gitlab(headers: Dict[str, str], payload: bytes) -> bool:
        """
        Validate GitLab webhook signature.

        GitLab sends X-Gitlab-Token header with secret token.
        """
        if not settings.WEBHOOK_SECRET:
            logger.warning("WEBHOOK_SECRET not set, skipping GitLab validation")
            return True

        token = headers.get("x-gitlab-token", "")
        if not token:
            raise HTTPException(status_code=401, detail="Missing X-Gitlab-Token header")

        if not hmac.compare_digest(token, settings.WEBHOOK_SECRET):
            raise HTTPException(status_code=401, detail="Invalid token")

        return True

    @staticmethod
    def validate_bitbucket(headers: Dict[str, str], payload: bytes) -> bool:
        """
        Validate Bitbucket webhook signature.

        Bitbucket sends X-Hub-Signature header with HMAC-SHA256 signature.
        Format: sha256=<signature>
        """
        if not settings.WEBHOOK_SECRET:
            logger.warning("WEBHOOK_SECRET not set, skipping Bitbucket validation")
            return True

        signature_header = headers.get("x-hub-signature", "")
        if not signature_header:
            raise HTTPException(
                status_code=401, detail="Missing X-Hub-Signature header"
            )

        signature = signature_header.replace("sha256=", "")

        # Compute expected signature
        mac = hmac.new(
            settings.WEBHOOK_SECRET.encode(),
            msg=payload,
            digestmod=hashlib.sha256,
        )
        expected_signature = mac.hexdigest()

        # Compare signatures
        if not hmac.compare_digest(signature, expected_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

        return True

    @classmethod
    def validate(cls, platform: str, headers: Dict[str, str], payload: bytes) -> bool:
        """
        Validate webhook signature based on platform.

        Args:
            platform: Git platform name (github, gitlab, bitbucket)
            headers: Request headers
            payload: Request body bytes

        Returns:
            True if signature is valid

        Raises:
            HTTPException: If signature is invalid
        """
        validators = {
            "github": cls.validate_github,
            "gitlab": cls.validate_gitlab,
            "bitbucket": cls.validate_bitbucket,
        }

        validator = validators.get(platform.lower())
        if not validator:
            logger.warning(f"No signature validator for platform: {platform}")
            return True  # Skip validation for unknown platforms

        return validator(headers, payload)


# Convenience function
def validate_webhook_signature(
    platform: str, headers: Dict[str, str], payload: bytes
) -> bool:
    """Validate webhook signature."""
    return WebhookSignatureValidator.validate(platform, headers, payload)
