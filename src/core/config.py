from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    postgres_user: str
    postgres_password: str
    postgres_db: str
    db_host: str
    db_port: int
    database_url: str
    
    # Redis
    # REDIS_URL: str
    
    # # Celery
    # CELERY_BROKER_URL: str
    # CELERY_RESULT_BACKEND: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
    )


# Global settings instance
settings = Settings()