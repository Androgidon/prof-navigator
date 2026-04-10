from fastapi import APIRouter

from app.api.v1 import admin_users, assessments, auth, profile, recommendations

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(profile.router, prefix="/profile", tags=["profile"])
router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
router.include_router(admin_users.router, prefix="/admin/users", tags=["admin-users"])
