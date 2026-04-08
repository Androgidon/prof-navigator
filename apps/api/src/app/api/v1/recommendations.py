from fastapi import APIRouter, Depends

from app.api.dependencies import get_session
from app.repositories.profession_repository import ProfessionRepository
from app.schemas.recommendation import RecommendationBulkResponse, RecommendationRequest
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter()


@router.post("/", response_model=RecommendationBulkResponse)
async def recommend(payload: RecommendationRequest, session=Depends(get_session)) -> RecommendationBulkResponse:
    repo = ProfessionRepository(session)
    professions = await repo.list_all()
    engine = RecommendationEngine(professions)
    recommendations = engine.recommend(payload.vector)
    return RecommendationBulkResponse(recommendations=recommendations)
