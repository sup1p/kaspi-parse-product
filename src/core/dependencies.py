"""
Dependency injection module for FastAPI.
Provides HTTP client instances for API endpoints.
"""
from fastapi.security import OAuth2PasswordBearer
from src.core.settings import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

engine = create_async_engine(settings.database_url, future=True, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
        
