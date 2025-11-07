"""Slack Webhook provider."""

import httpx
from typing import Any, Dict
from .base import BaseProvider
from ..utils.logger import get_logger
from ..utils.exceptions import ProviderError

logger = get_logger(__name__)


class SlackProvider(BaseProvider):
    """Slack notification provider using Incoming Webhooks."""

    def _validate_config(self) -> None:
        """Validate Slack configuration."""
        self.webhook_url = self._get_required_field("webhook_url")
        self.channel = self._get_optional_field("channel")
        self.username = self._get_optional_field("username", "Git Notifier")
        self.icon_emoji = self._get_optional_field("icon_emoji", ":rocket:")

    async def send(self, message: Dict[str, Any]) -> bool:
        """
        Send message to Slack.

        Args:
            message: Message dict with 'blocks' or 'text'

        Returns:
            True if sent successfully

        Raises:
            ProviderError: If sending fails
        """
        try:
            # Build payload
            payload: Dict[str, Any] = {
                "username": self.username,
                "icon_emoji": self.icon_emoji,
            }

            # Add channel if specified
            if self.channel:
                payload["channel"] = self.channel

            # Prefer blocks over text
            if "blocks" in message:
                payload["blocks"] = message["blocks"]
                # Add fallback text
                payload["text"] = message.get("text", "New notification")
            elif "text" in message:
                payload["text"] = message["text"]
            else:
                raise ProviderError("Message must contain 'blocks' or 'text'")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.webhook_url, json=payload)

                if response.status_code == 200:
                    if response.text == "ok":
                        logger.info("Successfully sent message to Slack")
                        return True
                    else:
                        raise ProviderError(
                            f"Slack returned unexpected response: {response.text}",
                            details={"response": response.text},
                        )
                else:
                    raise ProviderError(
                        f"Slack webhook returned {response.status_code}",
                        details={
                            "status_code": response.status_code,
                            "body": response.text,
                        },
                    )

        except httpx.RequestError as e:
            logger.error(f"Network error sending to Slack: {e}")
            raise ProviderError(f"Network error: {str(e)}", details={"error": str(e)})
        except ProviderError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending to Slack: {e}")
            raise ProviderError(
                f"Unexpected error: {str(e)}", details={"error": str(e)}
            )

    async def test_connection(self) -> bool:
        """
        Test Slack webhook connection.

        Returns:
            True if connection is successful
        """
        try:
            test_payload = {
                "text": "Test connection from Webhook Bridge",
                "username": self.username,
                "icon_emoji": self.icon_emoji,
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.webhook_url, json=test_payload)

                if response.status_code == 200 and response.text == "ok":
                    logger.info("Slack webhook test successful")
                    return True

                logger.error(f"Slack test failed: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Slack connection test failed: {e}")
            return False
