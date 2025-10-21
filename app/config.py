from __future__ import annotations

import base64
import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings, Field


DATA_ROOT = Path("data")
SESSIONS_DIR = DATA_ROOT / "sessions"
GROUPS_DIR = DATA_ROOT / "groups"
MEMBERS_DIR = DATA_ROOT / "members"
PREPARED_DIR = DATA_ROOT / "prepared"
KEY_FILE = DATA_ROOT / ".fernet.key"


class Settings(BaseSettings):
    """Application configuration derived from environment variables."""

    database_url: str = Field(default=f"sqlite:///{(DATA_ROOT / 'socialpro.db').as_posix()}")
    encryption_key: str | None = None
    telethon_sessions_dir: Path = Field(default=SESSIONS_DIR)
    data_root: Path = Field(default=DATA_ROOT)

    class Config:
        env_file = ".env"
        env_prefix = "SOCIALPRO_"

    def get_encryption_key(self) -> bytes:
        """Load an encryption key from settings or a managed key file."""
        if self.encryption_key:
            return base64.urlsafe_b64decode(self.encryption_key)
        if KEY_FILE.exists():
            return base64.urlsafe_b64decode(KEY_FILE.read_text().strip())
        key = base64.urlsafe_b64encode(os.urandom(32))
        KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        KEY_FILE.write_text(key.decode())
        return base64.urlsafe_b64decode(key)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_root.mkdir(parents=True, exist_ok=True)
    settings.telethon_sessions_dir.mkdir(parents=True, exist_ok=True)
    GROUPS_DIR.mkdir(parents=True, exist_ok=True)
    MEMBERS_DIR.mkdir(parents=True, exist_ok=True)
    PREPARED_DIR.mkdir(parents=True, exist_ok=True)
    return settings


__all__ = ["Settings", "get_settings", "DATA_ROOT", "GROUPS_DIR", "MEMBERS_DIR", "PREPARED_DIR", "SESSIONS_DIR"]
