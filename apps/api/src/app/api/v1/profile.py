from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, get_session
from app.repositories.user_repository import UserRepository
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter()


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(payload: ProfileCreate, session=Depends(get_session)) -> ProfileResponse:
    repo = UserRepository(session)
    user = await repo.find_by_id(payload.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    service = ProfileService(session)
    profile = await service.create(payload)
    await session.commit()
    return ProfileResponse.from_orm(profile)


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    session=Depends(get_session),
    current_user=Depends(get_current_user),
) -> ProfileResponse:
    service = ProfileService(session)
    profile = await service.get_for_user(current_user.id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return ProfileResponse.from_orm(profile)


@router.put("/me", response_model=ProfileResponse)
async def upsert_my_profile(
    payload: ProfileUpdate,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
) -> ProfileResponse:
    service = ProfileService(session)
    profile = await service.upsert_for_user(current_user.id, payload)
    await session.commit()
    return ProfileResponse.from_orm(profile)
