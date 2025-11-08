"""Email provider using SMTP."""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Dict
from .base import BaseProvider
from ..utils.logger import get_logger
from ..utils.exceptions import ProviderError

logger = get_logger(__name__)


class EmailProvider(BaseProvider):
    """Email notification provider using SMTP."""

    def _validate_config(self) -> None:
        """Validate Email configuration."""
        self.smtp_host = self._get_required_field("smtp_host")
        self.smtp_port = self._get_optional_field("smtp_port", 587)
        self.smtp_user = self._get_required_field("smtp_user")
        self.smtp_password = self._get_required_field("smtp_password")
        self.from_email = self._get_optional_field("from_email", self.smtp_user)
        self.to_emails = self._get_required_field("to_emails")  # Comma-separated
        self.use_tls = self._get_optional_field("use_tls", True)

    async def send(self, message: Dict[str, Any]) -> bool:
        """
        Send email notification.

        Args:
            message: Message dict with 'text' and optional 'subject'

        Returns:
            True if sent successfully

        Raises:
            ProviderError: If sending fails
        """
        try:
            text = message.get("text", "")
            subject = message.get("subject", "Git Notification")

            if not text:
                raise ProviderError("Message text is empty")

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = self.to_emails

            # Plain text and HTML
            part = MIMEText(text, "plain")
            msg.attach(part)

            # Send email (async)
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=self.use_tls,
            )

            logger.info("Successfully sent email notification")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise ProviderError(f"Email error: {str(e)}", details={"error": str(e)})

    async def test_connection(self) -> bool:
        """
        Test SMTP connection.

        Returns:
            True if connection is successful
        """
        try:
            # Test async SMTP connection
            smtp = aiosmtplib.SMTP(
                hostname=self.smtp_host, port=self.smtp_port, timeout=10
            )
            await smtp.connect()
            if self.use_tls:
                await smtp.starttls()
            await smtp.login(self.smtp_user, self.smtp_password)
            await smtp.quit()
            logger.info("Email SMTP connection test successful")
            return True
        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return False
