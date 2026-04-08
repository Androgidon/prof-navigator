from typing import Iterable, List

from app.models.profession import Profession
from app.schemas.recommendation import RecommendationResponse


class RecommendationEngine:
    def __init__(self, professions: Iterable[Profession]) -> None:
        self.professions = list(professions)

    def score(self, vector: dict, profession: Profession) -> int:
        vector_scores = profession.profession_vector or {}
        base = sum(vector.get(k, 0) * vector_scores.get(k, 0) for k in vector_scores)
        return max(0, min(int(base * 100), 100))

    def explain(self, profession: Profession, score: int) -> List[str]:
        return [f"vector match {profession.slug}", "interest alignment"]

    def recommend(self, vector: dict) -> List[RecommendationResponse]:
        scored = sorted(
            self.professions,
            key=lambda profession: self.score(vector, profession),
            reverse=True,
        )
        top = scored[:10]
        return [
            RecommendationResponse(
                profession=str(prof.id),
                slug=prof.slug,
                score=self.score(vector, prof),
                rank=i + 1,
                explanation=self.explain(prof, self.score(vector, prof)),
            )
            for i, prof in enumerate(top)
        ]
