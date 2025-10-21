from __future__ import annotations

from cryptography.fernet import Fernet

from ..config import get_settings


class EncryptionService:
    """Simple wrapper around Fernet encryption for sensitive fields."""

    def __init__(self) -> None:
        self._fernet = Fernet(get_settings().get_encryption_key())

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        return self._fernet.decrypt(value.encode()).decode()


encryption_service = EncryptionService()

__all__ = ["EncryptionService", "encryption_service"]
