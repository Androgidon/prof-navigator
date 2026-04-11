from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.models.base import metadata as models_metadata

settings = get_settings()

metadata = models_metadata

engine = create_async_engine(settings.database_url, future=True, poolclass=NullPool)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
