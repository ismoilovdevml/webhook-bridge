"""Custom exceptions for webhook bridge."""

from typing import Optional, Dict, Any


class WebhookBridgeError(Exception):
    """Base exception for all webhook bridge errors."""

    def __init__(self, message: str, details: Optional[Dict[Any, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ProviderError(WebhookBridgeError):
    """Raised when a provider fails to send notification."""

    pass


class ParserError(WebhookBridgeError):
    """Raised when parsing webhook payload fails."""

    pass


class FormatterError(WebhookBridgeError):
    """Raised when formatting message fails."""

    pass


class DatabaseError(WebhookBridgeError):
    """Raised when database operation fails."""

    pass


class ConfigurationError(WebhookBridgeError):
    """Raised when configuration is invalid."""

    pass


class AuthenticationError(WebhookBridgeError):
    """Raised when authentication fails."""

    pass
