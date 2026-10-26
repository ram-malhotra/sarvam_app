"""Application configuration settings for VoiceMenu AI."""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings loaded from environment variables or .env file."""

    SARVAM_API_KEY: str = ""
    KITCHEN_PIN: str = "1234"
    DATABASE_URL: str = "sqlite:///./voicemenu.db"
    CORS_ORIGINS: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Return CORS origins as a list of trimmed strings.

        Returns:
            List[str]: Clean list of allowed origin URLs.
        """
        if not self.CORS_ORIGINS:
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton instance of application settings.

    Returns:
        Settings: Application settings instance.
    """
    return Settings()
