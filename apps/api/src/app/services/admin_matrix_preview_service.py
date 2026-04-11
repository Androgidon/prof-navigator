from __future__ import annotations

from app.domains.assessment_scoring.profession_match_service import ProfessionMatchService
from app.schemas.admin_matrix import MatrixPreviewResponse


class _MatrixProxy:
    def __init__(self, target_profile_json, dimension_weights_json, critical_dimensions):
        self.target_profile_json = target_profile_json
        self.dimension_weights_json = dimension_weights_json
        self.critical_dimensions = critical_dimensions


class AdminMatrixPreviewService:
    def preview(
        self,
        profile_scores,
        target_profile_json,
        dimension_weights_json,
        critical_dimensions,
        cluster,
    ) -> MatrixPreviewResponse:
        svc = ProfessionMatchService()
        matrix = _MatrixProxy(target_profile_json, dimension_weights_json, critical_dimensions)

        base_similarity = svc._base_similarity(profile_scores, matrix)
        critical_penalty = svc._critical_penalty(profile_scores, matrix)
        strong_fit_bonus = svc._strong_fit_bonus(profile_scores, matrix)
        admissibility = svc._admissibility(profile_scores, matrix, cluster or "")

        admissibility_effect = (2.5 if admissibility["strong"] else 0.0) - (0.0 if admissibility["eligible"] else 11.0)
        final_score = max(0.0, min(100.0, base_similarity - critical_penalty + strong_fit_bonus + admissibility_effect))

        return MatrixPreviewResponse(
            base_similarity=round(base_similarity, 3),
            critical_penalty=round(critical_penalty, 3),
            strong_fit_effect=round(strong_fit_bonus, 3),
            admissibility_effect=round(admissibility_effect, 3),
            admissible=bool(admissibility["eligible"]),
            final_score=round(final_score, 3),
        )
