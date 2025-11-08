"""Tests for encryption utilities."""

import pytest
from app.utils.encryption import (
    EncryptionService,
    encrypt_field,
    decrypt_field,
    get_encryption_service,
)


class TestEncryptionService:
    """Test encryption service functionality."""

    def test_encrypt_decrypt_string(self):
        """Test basic encrypt and decrypt."""
        service = get_encryption_service()
        plaintext = "my_secret_token_123"

        encrypted = service.encrypt(plaintext)
        assert encrypted != plaintext
        assert len(encrypted) > 0

        decrypted = service.decrypt(encrypted)
        assert decrypted == plaintext

    def test_encrypt_empty_string(self):
        """Test encrypting empty string."""
        service = get_encryption_service()
        encrypted = service.encrypt("")
        assert encrypted == ""

    def test_decrypt_empty_string(self):
        """Test decrypting empty string."""
        service = get_encryption_service()
        decrypted = service.decrypt("")
        assert decrypted == ""

    def test_encrypt_optional_none(self):
        """Test encrypting None value."""
        service = get_encryption_service()
        encrypted = service.encrypt_optional(None)
        assert encrypted is None

    def test_decrypt_optional_none(self):
        """Test decrypting None value."""
        service = get_encryption_service()
        decrypted = service.decrypt_optional(None)
        assert decrypted is None

    def test_encrypt_field_utility(self):
        """Test encrypt_field utility function."""
        plaintext = "test_password"
        encrypted = encrypt_field(plaintext)
        assert encrypted != plaintext

        decrypted = decrypt_field(encrypted)
        assert decrypted == plaintext

    def test_encrypt_field_none(self):
        """Test encrypt_field with None."""
        result = encrypt_field(None)
        assert result is None

    def test_singleton_service(self):
        """Test that encryption service is singleton."""
        service1 = get_encryption_service()
        service2 = get_encryption_service()
        assert service1 is service2

    def test_encrypt_decrypt_unicode(self):
        """Test encrypting Unicode strings."""
        service = get_encryption_service()
        plaintext = "Hello 世界 🌍"

        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)
        assert decrypted == plaintext

    def test_encrypt_decrypt_long_string(self):
        """Test encrypting long strings."""
        service = get_encryption_service()
        plaintext = "a" * 10000

        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)
        assert decrypted == plaintext
