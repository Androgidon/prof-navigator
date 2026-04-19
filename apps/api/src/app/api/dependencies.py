import logging
from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import async_session
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    logger.info("get_session start")
    session: Optional[AsyncSession] = None
    try:
        async with async_session() as session:
            logger.info("session created", extra={"session_id": id(session)})
            logger.info("yield session", extra={"session_id": id(session)})
            yield session
    except Exception:
        logger.exception("get_session failed")
        raise
    finally:
        logger.info("session closed", extra={"session_id": id(session) if session is not None else None})


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    payload = AuthService.token_payload(credentials.credentials)
    user_id = payload.get("sub") if payload else None
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    user = await UserRepository(session).find_by_id(str(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> Optional[User]:
    if not credentials:
        return None

    payload = AuthService.token_payload(credentials.credentials)
    user_id = payload.get("sub") if payload else None
    if not user_id:
        return None

    return await UserRepository(session).find_by_id(str(user_id))


async def require_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return current_user
