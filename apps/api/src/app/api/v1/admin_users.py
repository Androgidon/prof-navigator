from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import require_admin_user
from app.db.session import get_db_session
from app.models.assessment_result import AssessmentResult
from app.models.assessment_session import AssessmentSession
from app.models.email_verification_code import EmailVerificationCode
from app.models.recommendation import Recommendation
from app.models.refresh_token import RefreshToken
from app.models.subject_grade import SubjectGrade
from app.models.test_response import TestResponse
from app.models.test_session import TestSession
from app.models.user_favorite import UserFavorite
from app.models.profile import UserProfile
from app.repositories.user_repository import UserRepository

router = APIRouter(dependencies=[Depends(require_admin_user)])


def _serialize_user(user) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.get("", status_code=status.HTTP_200_OK)
async def list_users(session: AsyncSession = Depends(get_db_session)) -> dict:
    repo = UserRepository(session)
    users = await repo.list_users()
    return {"users": [_serialize_user(user) for user in users]}


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_detail(user_id: str, session: AsyncSession = Depends(get_db_session)) -> dict:
    repo = UserRepository(session)
    user = await repo.find_by_id_with_profile(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    recommendations = []
    if user.profile:
        rec_result = await session.execute(
            select(Recommendation)
            .where(Recommendation.user_profile_id == user.profile.id)
            .options(selectinload(Recommendation.profession))
        )
        recommendations = rec_result.scalars().all()

    fav_result = await session.execute(
        select(UserFavorite)
        .where(UserFavorite.user_id == user.id)
        .options(selectinload(UserFavorite.profession))
    )
    favorites = fav_result.scalars().all()

    profile_payload = None
    if user.profile:
        profile_payload = {
            "full_name": user.profile.full_name,
            "birth_date": user.profile.birth_date,
            "country": user.profile.country,
            "region": user.profile.region,
            "city": user.profile.city,
            "language": user.profile.language,
            "grades": user.profile.grades,
            "interests": user.profile.interests,
            "created_at": user.profile.created_at.isoformat() if user.profile.created_at else None,
        }

    return {
        "account": _serialize_user(user),
        "profile": profile_payload,
        "recommendations": [
            {
                "id": str(rec.id),
                "score": rec.score,
                "rank": rec.rank,
                "profession_id": str(rec.profession_id),
                "profession_title": rec.profession.title_ru if rec.profession else None,
                "created_at": rec.created_at.isoformat() if rec.created_at else None,
            }
            for rec in recommendations
        ],
        "favorites": [
            {
                "id": str(fav.id),
                "profession_id": str(fav.profession_id),
                "profession_title": fav.profession.title_ru if fav.profession else None,
                "note": fav.note,
                "created_at": fav.created_at.isoformat() if fav.created_at else None,
            }
            for fav in favorites
        ],
    }


@router.post("/{user_id}/deactivate", status_code=status.HTTP_200_OK)
async def deactivate_user(
    user_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    repo = UserRepository(session)
    user = await repo.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await repo.set_active(user, False)
    await session.commit()
    return {"status": "deactivated", "user": _serialize_user(user)}


@router.post("/{user_id}/activate", status_code=status.HTTP_200_OK)
async def activate_user(
    user_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    repo = UserRepository(session)
    user = await repo.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await repo.set_active(user, True)
    await session.commit()
    return {"status": "active", "user": _serialize_user(user)}


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def hard_delete_user(
    user_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_admin=Depends(require_admin_user),
) -> dict:
    repo = UserRepository(session)
    user = await repo.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if str(current_admin.id) == str(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя удалить текущего админа")

    profile_id_result = await session.execute(select(UserProfile.id).where(UserProfile.user_id == user.id))
    profile_id = profile_id_result.scalar_one_or_none()

    # test sessions + responses
    test_sessions_result = await session.execute(select(TestSession.id).where(TestSession.user_id == user.id))
    test_session_ids = [row[0] for row in test_sessions_result.all()]
    if test_session_ids:
        await session.execute(delete(TestResponse).where(TestResponse.session_id.in_(test_session_ids)))
        await session.execute(delete(TestSession).where(TestSession.id.in_(test_session_ids)))

    # recommendations + subject grades linked via user profile
    if profile_id:
        await session.execute(delete(Recommendation).where(Recommendation.user_profile_id == profile_id))
        await session.execute(delete(SubjectGrade).where(SubjectGrade.profile_id == profile_id))

    # favorites, refresh tokens, verification codes
    await session.execute(delete(UserFavorite).where(UserFavorite.user_id == user.id))
    await session.execute(delete(RefreshToken).where(RefreshToken.user_id == user.id))
    await session.execute(delete(EmailVerificationCode).where(EmailVerificationCode.user_id == user.id))

    # assessment chain
    assessment_session_ids_result = await session.execute(
        select(AssessmentSession.id).where(AssessmentSession.user_id == user.id)
    )
    assessment_session_ids = [row[0] for row in assessment_session_ids_result.all()]
    if assessment_session_ids:
        await session.execute(delete(AssessmentResult).where(AssessmentResult.session_id.in_(assessment_session_ids)))
        await session.execute(delete(AssessmentSession).where(AssessmentSession.id.in_(assessment_session_ids)))

    if profile_id:
        await session.execute(delete(UserProfile).where(UserProfile.id == profile_id))

    await session.execute(delete(AssessmentSession).where(AssessmentSession.user_id == user.id))
    await session.execute(delete(UserProfile).where(UserProfile.user_id == user.id))
    await session.execute(delete(UserFavorite).where(UserFavorite.user_id == user.id))
    await session.execute(delete(RefreshToken).where(RefreshToken.user_id == user.id))
    await session.execute(delete(EmailVerificationCode).where(EmailVerificationCode.user_id == user.id))
    await session.execute(delete(TestSession).where(TestSession.user_id == user.id))

    await session.delete(user)
    await session.commit()

    return {"status": "deleted", "user_id": user_id}
