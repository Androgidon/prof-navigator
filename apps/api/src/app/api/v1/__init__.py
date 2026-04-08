from fastapi import APIRouter

from app.api.v1 import assessments, auth, profile, recommendations

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(profile.router, prefix="/profile", tags=["profile"])
router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
