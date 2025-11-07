"""Mattermost Webhook provider."""

import httpx
from typing import Any, Dict
from .base import BaseProvider
from ..utils.logger import get_logger
from ..utils.exceptions import ProviderError

logger = get_logger(__name__)


class MattermostProvider(BaseProvider):
    """Mattermost notification provider using Incoming Webhooks."""

    def _validate_config(self) -> None:
        """Validate Mattermost configuration."""
        self.webhook_url = self._get_required_field("webhook_url")
        self.channel = self._get_optional_field("channel")
        self.username = self._get_optional_field("username", "Git Notifier")
        self.icon_url = self._get_optional_field("icon_url")

    async def send(self, message: Dict[str, Any]) -> bool:
        """
        Send message to Mattermost.

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

            # Build payload
            payload: Dict[str, Any] = {
                "text": text,
                "username": self.username,
            }

            # Add optional fields
            if self.channel:
                payload["channel"] = self.channel
            if self.icon_url:
                payload["icon_url"] = self.icon_url

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.webhook_url, json=payload)

                if response.status_code == 200:
                    logger.info("Successfully sent message to Mattermost")
                    return True
                else:
                    raise ProviderError(
                        f"Mattermost webhook returned {response.status_code}",
                        details={
                            "status_code": response.status_code,
                            "body": response.text,
                        },
                    )

        except httpx.RequestError as e:
            logger.error(f"Network error sending to Mattermost: {e}")
            raise ProviderError(f"Network error: {str(e)}", details={"error": str(e)})
        except ProviderError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending to Mattermost: {e}")
            raise ProviderError(
                f"Unexpected error: {str(e)}", details={"error": str(e)}
            )

    async def test_connection(self) -> bool:
        """
        Test Mattermost webhook connection.

        Returns:
            True if connection is successful
        """
        try:
            test_payload = {
                "text": "Test connection from Webhook Bridge",
                "username": self.username,
            }

            if self.icon_url:
                test_payload["icon_url"] = self.icon_url

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.webhook_url, json=test_payload)

                if response.status_code == 200:
                    logger.info("Mattermost webhook test successful")
                    return True

                logger.error(f"Mattermost test failed: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Mattermost connection test failed: {e}")
            return False
