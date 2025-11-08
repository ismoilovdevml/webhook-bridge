"""Encryption utilities for sensitive data."""

from cryptography.fernet import Fernet
from ..config import settings
from typing import Optional
import base64


class EncryptionService:
    """Service for encrypting and decrypting sensitive data."""

    def __init__(self):
        if not settings.ENCRYPTION_KEY:
            raise ValueError("ENCRYPTION_KEY not set in environment")

        # Ensure key is properly formatted
        key = settings.ENCRYPTION_KEY
        if len(key) != 44:  # Fernet keys are 44 characters
            # Pad or derive key to proper length
            key = base64.urlsafe_b64encode(key.encode().ljust(32)[:32])
        else:
            key = key.encode()

        self.cipher = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext string."""
        if not plaintext:
            return ""
        encrypted_bytes = self.cipher.encrypt(plaintext.encode())
        return encrypted_bytes.decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext string."""
        if not ciphertext:
            return ""
        decrypted_bytes = self.cipher.decrypt(ciphertext.encode())
        return decrypted_bytes.decode()

    def encrypt_optional(self, plaintext: Optional[str]) -> Optional[str]:
        """Encrypt optional string."""
        return self.encrypt(plaintext) if plaintext else None

    def decrypt_optional(self, ciphertext: Optional[str]) -> Optional[str]:
        """Decrypt optional string."""
        return self.decrypt(ciphertext) if ciphertext else None


# Global encryption service instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """Get or create encryption service singleton."""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


# Convenience functions
def encrypt_field(plaintext: Optional[str]) -> Optional[str]:
    """Encrypt a field value."""
    if not plaintext:
        return plaintext
    return get_encryption_service().encrypt(plaintext)


def decrypt_field(ciphertext: Optional[str]) -> Optional[str]:
    """Decrypt a field value."""
    if not ciphertext:
        return ciphertext
    return get_encryption_service().decrypt(ciphertext)
