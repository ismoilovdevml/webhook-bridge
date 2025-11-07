"""Notification providers for different platforms."""

from typing import Dict, Any, Type

from .base import BaseProvider
from .telegram import TelegramProvider
from .slack import SlackProvider
from .mattermost import MattermostProvider
from .discord import DiscordProvider
from .email import EmailProvider

# Provider registry
PROVIDERS: Dict[str, Type[BaseProvider]] = {
    "telegram": TelegramProvider,
    "slack": SlackProvider,
    "mattermost": MattermostProvider,
    "discord": DiscordProvider,
    "email": EmailProvider,
}


def get_provider(provider_type: str, config: Dict[Any, Any]) -> BaseProvider:
    """
    Get provider instance by type.

    Args:
        provider_type: Type of provider (telegram, slack, etc.)
        config: Provider configuration

    Returns:
        Provider instance

    Raises:
        ValueError: If provider type is unknown
    """
    provider_class = PROVIDERS.get(provider_type)
    if not provider_class:
        raise ValueError(
            f"Unknown provider type: {provider_type}. "
            f"Available: {', '.join(PROVIDERS.keys())}"
        )
    return provider_class(config)


__all__ = [
    "BaseProvider",
    "TelegramProvider",
    "SlackProvider",
    "MattermostProvider",
    "DiscordProvider",
    "EmailProvider",
    "PROVIDERS",
    "get_provider",
]
