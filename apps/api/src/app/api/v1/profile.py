from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_session
from app.repositories.user_repository import UserRepository
from app.schemas.profile import ProfileCreate, ProfileResponse
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
    return ProfileResponse.from_orm(profile)
