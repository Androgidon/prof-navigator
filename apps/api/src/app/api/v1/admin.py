from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.api.v1 import admin_assessments, admin_matrix, admin_professions, admin_questions
from app.schemas.admin_common import AdminMeResponse

router = APIRouter(prefix="/admin")


@router.get("/me", response_model=AdminMeResponse)
async def me(current_user=Depends(get_current_user)) -> AdminMeResponse:
    return AdminMeResponse(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
    )


router.include_router(admin_assessments.router)
router.include_router(admin_questions.router)
router.include_router(admin_professions.router)
router.include_router(admin_matrix.router)
