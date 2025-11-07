"""Notification providers for different platforms."""

from .base import BaseProvider
from .telegram import TelegramProvider
from .slack import SlackProvider
from .mattermost import MattermostProvider
from .discord import DiscordProvider

# Provider registry
PROVIDERS = {
    "telegram": TelegramProvider,
    "slack": SlackProvider,
    "mattermost": MattermostProvider,
    "discord": DiscordProvider,
}


def get_provider(provider_type: str, config: dict) -> BaseProvider:
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
    "PROVIDERS",
    "get_provider",
]
