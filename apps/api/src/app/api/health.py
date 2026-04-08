from fastapi import APIRouter, Depends

from app.core.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "/readiness",
    response_model=HealthResponse,
    tags=["health"],
)
async def readiness(settings=Depends(get_settings)) -> HealthResponse:
    return HealthResponse(status="ok", type="readiness", env=settings.environment)


@router.get(
    "/liveness",
    response_model=HealthResponse,
    tags=["health"],
)
async def liveness() -> HealthResponse:
    return HealthResponse(status="ok", type="liveness")
