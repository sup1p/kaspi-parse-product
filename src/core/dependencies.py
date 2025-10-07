"""
Dependency injection module for FastAPI.
Provides HTTP client instances for API endpoints.
"""
from src.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Используем URL как есть, теперь он содержит psycopg2
engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
