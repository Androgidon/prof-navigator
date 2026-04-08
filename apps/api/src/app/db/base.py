from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
