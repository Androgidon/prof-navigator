from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.core.settings import get_settings
from app.models.profile import UserProfile
from app.models.recommendation import Recommendation
from app.models.refresh_token import RefreshToken
from app.models.test_response import TestResponse
from app.models.test_session import TestSession
from app.models.user import User
from app.models.user_favorite import UserFavorite

router = APIRouter()


class ResetUserRequest(BaseModel):
    email: str


@router.post("/reset-user", status_code=status.HTTP_200_OK)
async def reset_user(payload: ResetUserRequest, session: AsyncSession = Depends(get_session)) -> dict:
    settings = get_settings()
    if settings.environment not in {"local", "dev", "development"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    user_result = await session.execute(select(User).where(User.email == payload.email))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    profile_result = await session.execute(select(UserProfile.id).where(UserProfile.user_id == user.id))
    profile_ids = list(profile_result.scalars().all())

    await session.execute(delete(RefreshToken).where(RefreshToken.user_id == user.id))
    await session.execute(delete(UserFavorite).where(UserFavorite.user_id == user.id))

    test_session_result = await session.execute(select(TestSession.id).where(TestSession.user_id == user.id))
    test_session_ids = list(test_session_result.scalars().all())
    if test_session_ids:
        await session.execute(delete(TestResponse).where(TestResponse.session_id.in_(test_session_ids)))
    await session.execute(delete(TestSession).where(TestSession.user_id == user.id))

    if profile_ids:
        await session.execute(delete(Recommendation).where(Recommendation.user_profile_id.in_(profile_ids)))
    await session.execute(delete(UserProfile).where(UserProfile.user_id == user.id))

    await session.execute(delete(User).where(User.id == user.id))
    await session.commit()

    return {"status": "reset", "email": payload.email}
