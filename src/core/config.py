from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Application
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    JSON_LOGS: bool = True
    
    # Kaspi parsing
    USER_AGENT: str
    REQUEST_TIMEOUT: int
    MAX_RETRIES: int

    # Export directories
    EXPORT_DIR: Path
    LOGS_DIR: Path
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()

# Create directories if they don't exist
settings.EXPORT_DIR.mkdir(exist_ok=True)
settings.LOGS_DIR.mkdir(exist_ok=True)