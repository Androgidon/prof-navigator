from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel


class RecommendationRequest(BaseModel):
    user_id: str
    vector: Dict[str, float]
    interests: List[str]


class RecommendationResponse(BaseModel):
    profession: str
    slug: str
    score: int
    rank: int
    explanation: List[str]


class RecommendationBulkResponse(BaseModel):
    recommendations: List[RecommendationResponse]
