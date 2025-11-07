"""Tests for notification providers."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.providers.telegram import TelegramProvider
from app.providers.slack import SlackProvider
from app.providers.mattermost import MattermostProvider
from app.providers.discord import DiscordProvider
from app.providers.email import EmailProvider
from app.utils.exceptions import ProviderError, ConfigurationError


class TestTelegramProvider:
    """Tests for Telegram provider."""

    def test_validate_config_success(self):
        """Test config validation with valid config."""
        config = {"bot_token": "123456:ABC-DEF", "chat_id": "-100123456789"}
        provider = TelegramProvider(config)
        assert provider.bot_token == "123456:ABC-DEF"
        assert provider.chat_id == "-100123456789"

    def test_validate_config_missing_bot_token(self):
        """Test config validation fails without bot_token."""
        config = {"chat_id": "-100123456789"}
        with pytest.raises(ConfigurationError, match="bot_token"):
            TelegramProvider(config)

    def test_validate_config_missing_chat_id(self):
        """Test config validation fails without chat_id."""
        config = {"bot_token": "123456:ABC-DEF"}
        with pytest.raises(ConfigurationError, match="chat_id"):
            TelegramProvider(config)

    @pytest.mark.asyncio
    async def test_send_success(self):
        """Test successful message sending."""
        config = {"bot_token": "123456:ABC-DEF", "chat_id": "-100123456789"}
        provider = TelegramProvider(config)

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"ok": True})

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            result = await provider.send("<b>Test message</b>")

        assert result is True
        mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_with_thread_id(self):
        """Test sending to thread/forum."""
        config = {
            "bot_token": "123456:ABC-DEF",
            "chat_id": "-100123456789",
            "thread_id": 123,
        }
        provider = TelegramProvider(config)

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"ok": True})

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            result = await provider.send("Test message")
            call_args = mock_post.call_args
            assert call_args[1]["json"]["message_thread_id"] == 123

        assert result is True

    @pytest.mark.asyncio
    async def test_send_failure(self):
        """Test failed message sending."""
        config = {"bot_token": "123456:ABC-DEF", "chat_id": "-100123456789"}
        provider = TelegramProvider(config)

        mock_response = MagicMock()
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value="Bad Request")

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            with pytest.raises(ProviderError, match="Telegram API error"):
                await provider.send("Test message")

    @pytest.mark.asyncio
    async def test_test_connection_success(self):
        """Test successful connection test."""
        config = {"bot_token": "123456:ABC-DEF", "chat_id": "-100123456789"}
        provider = TelegramProvider(config)

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"ok": True, "result": {"username": "test_bot"}}
        )

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            result = await provider.test_connection()

        assert result is True

    @pytest.mark.asyncio
    async def test_test_connection_failure(self):
        """Test failed connection test."""
        config = {"bot_token": "invalid_token", "chat_id": "-100123456789"}
        provider = TelegramProvider(config)

        mock_response = MagicMock()
        mock_response.status = 401

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            result = await provider.test_connection()

        assert result is False


class TestSlackProvider:
    """Tests for Slack provider."""

    def test_validate_config_success(self):
        """Test config validation with valid config."""
        config = {"webhook_url": "https://hooks.slack.com/services/xxx/yyy/zzz"}
        provider = SlackProvider(config)
        assert provider.webhook_url == "https://hooks.slack.com/services/xxx/yyy/zzz"

    def test_validate_config_missing_webhook_url(self):
        """Test config validation fails without webhook_url."""
        config = {}
        with pytest.raises(ConfigurationError, match="webhook_url"):
            SlackProvider(config)

    @pytest.mark.asyncio
    async def test_send_success(self):
        """Test successful message sending."""
        config = {"webhook_url": "https://hooks.slack.com/services/xxx/yyy/zzz"}
        provider = SlackProvider(config)

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="ok")

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            result = await provider.send({"text": "Test message"})

        assert result is True

    @pytest.mark.asyncio
    async def test_send_failure(self):
        """Test failed message sending."""
        config = {"webhook_url": "https://hooks.slack.com/services/xxx/yyy/zzz"}
        provider = SlackProvider(config)

        mock_response = MagicMock()
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value="invalid_token")

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            with pytest.raises(ProviderError, match="Slack API error"):
                await provider.send({"text": "Test message"})

    @pytest.mark.asyncio
    async def test_test_connection_success(self):
        """Test successful connection test."""
        config = {"webhook_url": "https://hooks.slack.com/services/xxx/yyy/zzz"}
        provider = SlackProvider(config)

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="ok")

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            result = await provider.test_connection()

        assert result is True


class TestMattermostProvider:
    """Tests for Mattermost provider."""

    def test_validate_config_success(self):
        """Test config validation with valid config."""
        config = {"webhook_url": "https://mattermost.example.com/hooks/xxx"}
        provider = MattermostProvider(config)
        assert provider.webhook_url == "https://mattermost.example.com/hooks/xxx"

    @pytest.mark.asyncio
    async def test_send_success(self):
        """Test successful message sending."""
        config = {"webhook_url": "https://mattermost.example.com/hooks/xxx"}
        provider = MattermostProvider(config)

        mock_response = MagicMock()
        mock_response.status = 200

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            result = await provider.send("Test message")

        assert result is True

    @pytest.mark.asyncio
    async def test_send_with_channel(self):
        """Test sending to specific channel."""
        config = {
            "webhook_url": "https://mattermost.example.com/hooks/xxx",
            "channel": "devops",
        }
        provider = MattermostProvider(config)

        mock_response = MagicMock()
        mock_response.status = 200

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            result = await provider.send("Test message")
            call_args = mock_post.call_args
            assert call_args[1]["json"]["channel"] == "devops"

        assert result is True


class TestDiscordProvider:
    """Tests for Discord provider."""

    def test_validate_config_success(self):
        """Test config validation with valid config."""
        config = {"webhook_url": "https://discord.com/api/webhooks/123/xxx"}
        provider = DiscordProvider(config)
        assert provider.webhook_url == "https://discord.com/api/webhooks/123/xxx"

    @pytest.mark.asyncio
    async def test_send_success(self):
        """Test successful message sending."""
        config = {"webhook_url": "https://discord.com/api/webhooks/123/xxx"}
        provider = DiscordProvider(config)

        mock_response = MagicMock()
        mock_response.status = 204

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            result = await provider.send("Test message")

        assert result is True

    @pytest.mark.asyncio
    async def test_send_creates_embed(self):
        """Test that send creates rich embed."""
        config = {"webhook_url": "https://discord.com/api/webhooks/123/xxx"}
        provider = DiscordProvider(config)

        mock_response = MagicMock()
        mock_response.status = 200

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            await provider.send("Test **message**")
            call_args = mock_post.call_args
            # Check that embed is created
            assert "embeds" in call_args[1]["json"]
            assert len(call_args[1]["json"]["embeds"]) == 1

    def test_get_embed_color(self):
        """Test embed color selection."""
        config = {"webhook_url": "https://discord.com/api/webhooks/123/xxx"}
        provider = DiscordProvider(config)

        # Test different status colors
        assert provider._get_embed_color("success") == 0x10B981  # Green
        assert provider._get_embed_color("failed") == 0xEF4444  # Red
        assert provider._get_embed_color("pending") == 0xF59E0B  # Yellow
        assert provider._get_embed_color("unknown") == 0x3B82F6  # Blue


class TestEmailProvider:
    """Tests for Email provider."""

    def test_validate_config_success(self):
        """Test config validation with valid config."""
        config = {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_user": "test@example.com",
            "smtp_password": "password",
            "from_email": "test@example.com",
            "to_emails": "dev@example.com",
        }
        provider = EmailProvider(config)
        assert provider.smtp_host == "smtp.gmail.com"
        assert provider.smtp_port == 587

    def test_validate_config_missing_fields(self):
        """Test config validation fails with missing fields."""
        config = {"smtp_host": "smtp.gmail.com"}
        with pytest.raises(ConfigurationError):
            EmailProvider(config)

    @pytest.mark.asyncio
    async def test_send_success(self):
        """Test successful email sending."""
        config = {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_user": "test@example.com",
            "smtp_password": "password",
            "from_email": "test@example.com",
            "to_emails": "dev@example.com",
        }
        provider = EmailProvider(config)

        mock_smtp = MagicMock()

        with patch("smtplib.SMTP") as mock_smtp_class:
            mock_smtp_class.return_value.__enter__.return_value = mock_smtp
            result = await provider.send("Test email body")

        assert result is True
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once()
        mock_smtp.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_multiple_recipients(self):
        """Test sending to multiple recipients."""
        config = {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_user": "test@example.com",
            "smtp_password": "password",
            "from_email": "test@example.com",
            "to_emails": "dev1@example.com,dev2@example.com",
        }
        provider = EmailProvider(config)

        assert len(provider.to_emails) == 2
        assert "dev1@example.com" in provider.to_emails
        assert "dev2@example.com" in provider.to_emails

    @pytest.mark.asyncio
    async def test_test_connection_success(self):
        """Test successful connection test."""
        config = {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_user": "test@example.com",
            "smtp_password": "password",
            "from_email": "test@example.com",
            "to_emails": "dev@example.com",
        }
        provider = EmailProvider(config)

        mock_smtp = MagicMock()

        with patch("smtplib.SMTP") as mock_smtp_class:
            mock_smtp_class.return_value.__enter__.return_value = mock_smtp
            result = await provider.test_connection()

        assert result is True
