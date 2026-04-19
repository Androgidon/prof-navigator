from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.models.base import metadata as models_metadata

settings = get_settings()

metadata = models_metadata

engine = create_async_engine(settings.database_url, future=True, poolclass=NullPool)
async_session = async_sessionmaker(engine, expire_on_commit=False)
