from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from functools import lru_cache

class Settings(BaseSettings):
    # Core Infrastructure
    DATABASE_URL: str
    REDIS_URL: str
    MINIO_URL: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    SECRET_KEY: str
    DB_PASS: str
    
    # Service URLs (Docker internal names; may be overridden)
    OLLAMA_URL: str
    API_BASE_URL: str
    FRONTEND_URL: str
    LITELLM_URL: Optional[str] = None
    QDRANT_URL: Optional[str] = None
    
    # Feature Flags
    USE_QDRANT: bool = False
    COOP_SIMULATION_MODE: bool = False
    ENVIRONMENT: str = "local"
    
    # Stage 2 Features
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_ADMIN_CHAT_ID: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # Observability
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @model_validator(mode='after')
    def validate_production(self) -> 'Settings':
        """Ensure required variables are set in production environment."""
        if self.ENVIRONMENT == "production":
            required = [
                'OLLAMA_URL', 'API_BASE_URL', 'FRONTEND_URL',
                'DATABASE_URL', 'REDIS_URL', 'MINIO_URL',
                'MINIO_ROOT_USER', 'MINIO_ROOT_PASSWORD',
                'SECRET_KEY', 'DB_PASS'
            ]
            missing = [f for f in required if not getattr(self, f, None)]
            if missing:
                raise ValueError(
                    f"Missing required environment variables for production: {', '.join(missing)}"
                )
        return self

@lru_cache
def get_settings() -> Settings:
    return Settings()
