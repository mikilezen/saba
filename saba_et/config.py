"""Environment-backed application settings."""

from dataclasses import dataclass
import os
import re


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    telegram_api_base: str = "https://api.telegram.org"
    request_timeout_seconds: int = 25

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        if not token:
            raise ValueError("Set TELEGRAM_BOT_TOKEN before starting Saba.")
        if not re.fullmatch(r"[0-9]+:[A-Za-z0-9_-]+", token):
            raise ValueError(
                "TELEGRAM_BOT_TOKEN has an invalid format. Create or copy a fresh token from BotFather."
            )
        return cls(telegram_bot_token=token)
