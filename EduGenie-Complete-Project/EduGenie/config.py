from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "EduGenie"
    app_version: str = "1.0.0"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    enable_local_explanation: bool = False
    local_explanation_model: str = "MBZUAI/LaMini-Flan-T5-783M"

    request_timeout_seconds: int = 60
    demo_mode: bool = False

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()