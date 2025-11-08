"""Tests for Provider model encryption functionality."""

import pytest
from app.models.provider import Provider
from app.utils.encryption import get_encryption_service


class TestProviderEncryption:
    """Test Provider model encryption methods."""

    def test_encrypt_config_telegram(self):
        """Test encrypting Telegram provider config."""
        config = {
            "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            "chat_id": "-100123456789",
        }

        encrypted_config = Provider.encrypt_config("telegram", config)

        # bot_token should be encrypted
        assert encrypted_config["bot_token"] != config["bot_token"]
        assert len(encrypted_config["bot_token"]) > 0

        # chat_id should not be encrypted
        assert encrypted_config["chat_id"] == config["chat_id"]

    def test_encrypt_config_slack(self):
        """Test encrypting Slack provider config."""
        config = {"webhook_url": "https://hooks.slack.com/services/T00/B00/XXX"}

        encrypted_config = Provider.encrypt_config("slack", config)

        # webhook_url should be encrypted
        assert encrypted_config["webhook_url"] != config["webhook_url"]

    def test_encrypt_config_discord(self):
        """Test encrypting Discord provider config."""
        config = {
            "webhook_url": "https://discord.com/api/webhooks/123/abc",
            "username": "MyBot",
        }

        encrypted_config = Provider.encrypt_config("discord", config)

        # webhook_url should be encrypted
        assert encrypted_config["webhook_url"] != config["webhook_url"]

        # username should not be encrypted
        assert encrypted_config["username"] == config["username"]

    def test_encrypt_config_email(self):
        """Test encrypting Email provider config."""
        config = {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_user": "user@example.com",
            "smtp_password": "secret_password_123",
            "from_address": "noreply@example.com",
            "to_addresses": ["admin@example.com"],
        }

        encrypted_config = Provider.encrypt_config("email", config)

        # smtp_password should be encrypted
        assert encrypted_config["smtp_password"] != config["smtp_password"]

        # Other fields should not be encrypted
        assert encrypted_config["smtp_host"] == config["smtp_host"]
        assert encrypted_config["smtp_user"] == config["smtp_user"]

    def test_encrypt_config_unknown_provider(self):
        """Test encrypting config for unknown provider type."""
        config = {"key": "value", "secret": "data"}

        encrypted_config = Provider.encrypt_config("unknown", config)

        # Should return config unchanged for unknown types
        assert encrypted_config == config

    def test_encrypt_config_empty(self):
        """Test encrypting empty config."""
        config = {}

        encrypted_config = Provider.encrypt_config("telegram", config)

        assert encrypted_config == {}

    def test_encrypt_config_missing_sensitive_field(self):
        """Test encrypting config when sensitive field is missing."""
        config = {"chat_id": "-100123456789"}  # No bot_token

        encrypted_config = Provider.encrypt_config("telegram", config)

        # Should not fail, just skip encryption
        assert encrypted_config == config

    def test_encrypt_config_none_value(self):
        """Test encrypting config with None value in sensitive field."""
        config = {"bot_token": None, "chat_id": "123"}

        encrypted_config = Provider.encrypt_config("telegram", config)

        # None should remain None
        assert encrypted_config["bot_token"] is None
        assert encrypted_config["chat_id"] == "123"

    def test_encrypt_config_empty_string(self):
        """Test encrypting config with empty string in sensitive field."""
        config = {"bot_token": "", "chat_id": "123"}

        encrypted_config = Provider.encrypt_config("telegram", config)

        # Empty string should remain empty
        assert encrypted_config["bot_token"] == ""
        assert encrypted_config["chat_id"] == "123"

    def test_get_decrypted_config_telegram(self):
        """Test decrypting Telegram provider config."""
        original_config = {
            "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            "chat_id": "-100123456789",
        }

        # Create provider with encrypted config
        encrypted_config = Provider.encrypt_config("telegram", original_config)
        provider = Provider(
            name="Test Telegram",
            type="telegram",
            config=encrypted_config,
        )

        # Get decrypted config
        decrypted_config = provider.get_decrypted_config()

        # Should match original
        assert decrypted_config["bot_token"] == original_config["bot_token"]
        assert decrypted_config["chat_id"] == original_config["chat_id"]

    def test_get_decrypted_config_email(self):
        """Test decrypting Email provider config."""
        original_config = {
            "smtp_host": "smtp.gmail.com",
            "smtp_password": "secret_password_123",
            "smtp_user": "user@example.com",
        }

        encrypted_config = Provider.encrypt_config("email", original_config)
        provider = Provider(
            name="Test Email", type="email", config=encrypted_config
        )

        decrypted_config = provider.get_decrypted_config()

        assert (
            decrypted_config["smtp_password"]
            == original_config["smtp_password"]
        )
        assert decrypted_config["smtp_host"] == original_config["smtp_host"]

    def test_get_decrypted_config_no_config(self):
        """Test decrypting when provider has no config."""
        provider = Provider(name="Test", type="telegram", config=None)

        decrypted_config = provider.get_decrypted_config()

        # Should return empty dict
        assert decrypted_config == {}

    def test_get_decrypted_config_handles_invalid_encryption(self):
        """Test decryption gracefully handles invalid encrypted data."""
        provider = Provider(
            name="Test",
            type="telegram",
            config={"bot_token": "invalid_encrypted_data", "chat_id": "123"},
        )

        # Should not raise exception, just leave invalid data as-is
        decrypted_config = provider.get_decrypted_config()

        # Invalid encrypted data remains unchanged
        assert decrypted_config["bot_token"] == "invalid_encrypted_data"
        assert decrypted_config["chat_id"] == "123"

    def test_encrypt_decrypt_roundtrip(self):
        """Test that encrypt -> decrypt returns original data."""
        original_config = {
            "bot_token": "my_secret_token_12345",
            "chat_id": "-100123456789",
            "extra": "data",
        }

        # Encrypt
        encrypted_config = Provider.encrypt_config("telegram", original_config)

        # Create provider
        provider = Provider(
            name="Test", type="telegram", config=encrypted_config
        )

        # Decrypt
        decrypted_config = provider.get_decrypted_config()

        # Should match original
        assert decrypted_config == original_config

    def test_sensitive_fields_definition(self):
        """Test that SENSITIVE_FIELDS is correctly defined."""
        # Check that SENSITIVE_FIELDS exists
        assert hasattr(Provider, "SENSITIVE_FIELDS")

        # Check expected providers
        assert "telegram" in Provider.SENSITIVE_FIELDS
        assert "slack" in Provider.SENSITIVE_FIELDS
        assert "discord" in Provider.SENSITIVE_FIELDS
        assert "email" in Provider.SENSITIVE_FIELDS
        assert "mattermost" in Provider.SENSITIVE_FIELDS

        # Check expected fields
        assert "bot_token" in Provider.SENSITIVE_FIELDS["telegram"]
        assert "webhook_url" in Provider.SENSITIVE_FIELDS["slack"]
        assert "smtp_password" in Provider.SENSITIVE_FIELDS["email"]

    def test_encrypt_config_multiple_sensitive_fields(self):
        """Test provider with multiple sensitive fields."""
        # Hypothetical provider with multiple secrets
        Provider.SENSITIVE_FIELDS["test_provider"] = ["secret1", "secret2"]

        config = {
            "secret1": "value1",
            "secret2": "value2",
            "public": "value3",
        }

        encrypted_config = Provider.encrypt_config("test_provider", config)

        # Both secrets should be encrypted
        assert encrypted_config["secret1"] != config["secret1"]
        assert encrypted_config["secret2"] != config["secret2"]

        # Public field should not be encrypted
        assert encrypted_config["public"] == config["public"]

        # Cleanup
        del Provider.SENSITIVE_FIELDS["test_provider"]

    def test_provider_config_immutability(self):
        """Test that encryption doesn't modify original config dict."""
        original_config = {
            "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            "chat_id": "-100123456789",
        }

        original_bot_token = original_config["bot_token"]

        # Encrypt
        encrypted_config = Provider.encrypt_config("telegram", original_config)

        # Original should be unchanged
        assert original_config["bot_token"] == original_bot_token
        assert original_config != encrypted_config
