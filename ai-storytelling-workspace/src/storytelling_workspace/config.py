"""
Application configuration settings.

Loads configuration from environment variables with sensible defaults.
"""

import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "AI Storytelling Workspace"
    VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"
    
    # MySQL Database
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "user")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "storytelling_workspace")
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str | None = os.getenv("REDIS_PASSWORD")
    
    # AI Providers
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # AI Models
    MISTRAL_TEXT_MODEL: str = os.getenv("MISTRAL_TEXT_MODEL", "mistral-large-latest")
    MISTRAL_IMAGE_MODEL: str = os.getenv("MISTRAL_IMAGE_MODEL", "pixtral-large-latest")
    OPENAI_TEXT_MODEL: str = os.getenv("OPENAI_TEXT_MODEL", "gpt-4o")
    OPENAI_IMAGE_MODEL: str = os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "1"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "1"))
    
    # Caching
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "86400"))  # 24 hours
    
    # Storage
    STORAGE_PATH: Path = Path(os.getenv("STORAGE_PATH", "./storage"))
    IMAGES_PATH: Path = STORAGE_PATH / "images"
    EXPORTS_PATH: Path = STORAGE_PATH / "exports"
    
    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_WORKERS: int = int(os.getenv("API_WORKERS", "4"))
    
    # CORS
    CORS_ORIGINS: list[str] = [
        origin.strip() 
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:3001,http://localhost:8000,http://localhost:8001"
        ).split(",")
    ]
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv(
        "CELERY_BROKER_URL",
        f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    )
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND",
        f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    )
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "json"  # json or text
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()


# Ensure storage directories exist (only if writable)
try:
    settings.STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    settings.IMAGES_PATH.mkdir(parents=True, exist_ok=True)
    settings.EXPORTS_PATH.mkdir(parents=True, exist_ok=True)
except (PermissionError, OSError) as e:
    # Skip directory creation if not writable (e.g., in Docker build)
    import logging
    logging.warning(f"Could not create storage directories: {e}")
