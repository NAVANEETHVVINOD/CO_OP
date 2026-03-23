from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    QDRANT_URL: str
    LITELLM_URL: Optional[str] = None
    SECRET_KEY: str
    DB_PASS: str
    MINIO_URL: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    ENVIRONMENT: str = "local"

    # --- Stage 2 ---
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_ADMIN_CHAT_ID: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
