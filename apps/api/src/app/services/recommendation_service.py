from typing import Iterable

from app.models.profession import Profession


class RecommendationService:
    @staticmethod
    def score_profession(user_vector: dict, profession: Profession) -> int:
        return 50

    def recommend(self, user_vector: dict, professions: Iterable[Profession]) -> list[Profession]:
        ranked = sorted(professions, key=self.score_profession.__get__(self, RecommendationService))
        return list(ranked)[:15]
