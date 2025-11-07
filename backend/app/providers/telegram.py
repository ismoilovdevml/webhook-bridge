"""Telegram Bot API provider."""

import httpx
from typing import Any, Dict
from .base import BaseProvider
from ..utils.logger import get_logger
from ..utils.exceptions import ProviderError

logger = get_logger(__name__)


class TelegramProvider(BaseProvider):
    """Telegram notification provider using Bot API."""

    def _validate_config(self) -> None:
        """Validate Telegram configuration."""
        self.bot_token = self._get_required_field("bot_token")
        self.chat_id = self._get_required_field("chat_id")
        self.thread_id = self._get_optional_field("thread_id")
        self.parse_mode = self._get_optional_field("parse_mode", "HTML")

        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send(self, message: Dict[str, Any]) -> bool:
        """
        Send message to Telegram.

        Args:
            message: Message dict with 'text' and optional 'parse_mode'

        Returns:
            True if sent successfully

        Raises:
            ProviderError: If sending fails
        """
        try:
            text = message.get("text", "")
            if not text:
                raise ProviderError("Message text is empty")

            parse_mode = message.get("parse_mode", self.parse_mode)

            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True,
            }

            # Add thread_id if configured (for forum groups)
            if self.thread_id:
                payload["message_thread_id"] = self.thread_id

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/sendMessage", json=payload
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        logger.info("Successfully sent message to Telegram")
                        return True
                    else:
                        error_msg = data.get("description", "Unknown error")
                        raise ProviderError(
                            f"Telegram API error: {error_msg}",
                            details={"response": data},
                        )
                else:
                    raise ProviderError(
                        f"Telegram API returned {response.status_code}",
                        details={
                            "status_code": response.status_code,
                            "body": response.text,
                        },
                    )

        except httpx.RequestError as e:
            logger.error(f"Network error sending to Telegram: {e}")
            raise ProviderError(f"Network error: {str(e)}", details={"error": str(e)})
        except ProviderError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending to Telegram: {e}")
            raise ProviderError(
                f"Unexpected error: {str(e)}", details={"error": str(e)}
            )

    async def test_connection(self) -> bool:
        """
        Test Telegram bot connection.

        Returns:
            True if connection is successful
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.api_url}/getMe")

                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        bot_info = data.get("result", {})
                        logger.info(
                            f"Telegram bot connected: @{bot_info.get('username', 'unknown')}"
                        )
                        return True

                logger.error(f"Telegram test failed: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False
