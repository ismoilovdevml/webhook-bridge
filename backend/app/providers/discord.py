"""Discord Webhook provider."""

import httpx
from typing import Any, Dict
from .base import BaseProvider
from ..utils.logger import get_logger
from ..utils.exceptions import ProviderError

logger = get_logger(__name__)


class DiscordProvider(BaseProvider):
    """Discord notification provider using Webhooks."""

    def _validate_config(self) -> None:
        """Validate Discord configuration."""
        self.webhook_url = self._get_required_field("webhook_url")
        self.username = self._get_optional_field("username", "Git Notifier")
        self.avatar_url = self._get_optional_field("avatar_url")

    async def send(self, message: Dict[str, Any]) -> bool:
        """
        Send message to Discord.

        Args:
            message: Message dict with 'text' (markdown)

        Returns:
            True if sent successfully

        Raises:
            ProviderError: If sending fails
        """
        try:
            text = message.get("text", "")
            if not text:
                raise ProviderError("Message text is empty")

            # Discord uses embeds for rich formatting
            # Convert simple text to embed format
            embed = self._create_embed(text, message)

            # Build payload
            payload: Dict[str, Any] = {
                "username": self.username,
                "embeds": [embed],
            }

            # Add avatar if configured
            if self.avatar_url:
                payload["avatar_url"] = self.avatar_url

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.webhook_url, json=payload)

                # Discord returns 204 No Content on success
                if response.status_code in [200, 204]:
                    logger.info("Successfully sent message to Discord")
                    return True
                else:
                    raise ProviderError(
                        f"Discord webhook returned {response.status_code}",
                        details={
                            "status_code": response.status_code,
                            "body": response.text,
                        },
                    )

        except httpx.RequestError as e:
            logger.error(f"Network error sending to Discord: {e}")
            raise ProviderError(f"Network error: {str(e)}", details={"error": str(e)})
        except ProviderError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending to Discord: {e}")
            raise ProviderError(
                f"Unexpected error: {str(e)}", details={"error": str(e)}
            )

    def _create_embed(self, text: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create Discord embed from text message.

        Args:
            text: Message text
            message: Original message dict

        Returns:
            Discord embed dict
        """
        # Split text into title and description
        lines = text.split("\n", 1)
        title = lines[0].strip("#* ") if lines else "Notification"
        description = lines[1] if len(lines) > 1 else ""

        embed: Dict[str, Any] = {
            "title": title[:256],  # Discord title limit
            "description": description[:4096],  # Discord description limit
            "color": self._get_embed_color(text),
        }

        # Add URL if present in message
        if "url" in message:
            embed["url"] = message["url"]

        # Add timestamp
        import datetime

        embed["timestamp"] = datetime.datetime.utcnow().isoformat()

        return embed

    def _get_embed_color(self, text: str) -> int:
        """
        Get embed color based on message content.

        Args:
            text: Message text

        Returns:
            Color as integer (RGB)
        """
        text_lower = text.lower()

        # Success/positive events - Green
        if any(word in text_lower for word in ["✅", "success", "merged", "passed"]):
            return 0x2ECC71  # Green

        # Error/negative events - Red
        if any(word in text_lower for word in ["❌", "failed", "error", "failure"]):
            return 0xE74C3C  # Red

        # Warning/pending events - Yellow
        if any(word in text_lower for word in ["⏳", "running", "pending", "warning"]):
            return 0xF39C12  # Yellow

        # Default - Blue
        return 0x3498DB  # Blue

    async def test_connection(self) -> bool:
        """
        Test Discord webhook connection.

        Returns:
            True if connection is successful
        """
        try:
            test_embed = {
                "title": "Test Connection",
                "description": "Test connection from Webhook Bridge",
                "color": 0x3498DB,
            }

            test_payload = {
                "username": self.username,
                "embeds": [test_embed],
            }

            if self.avatar_url:
                test_payload["avatar_url"] = self.avatar_url

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.webhook_url, json=test_payload)

                if response.status_code in [200, 204]:
                    logger.info("Discord webhook test successful")
                    return True

                logger.error(f"Discord test failed: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Discord connection test failed: {e}")
            return False
