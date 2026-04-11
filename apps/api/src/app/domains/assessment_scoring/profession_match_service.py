from __future__ import annotations

from collections import Counter
from typing import Any

BONUS_CAP = 5.0
ABSTRACT_CLUSTERS = {
    "Наука, исследования, экология",
    "Бизнес, управление, продажи",
}

CLUSTER_ADMISSIBILITY_RULES = {
    "IT и цифровые технологии": ["technical", "analytical", "detail"],
    "Инженерия, производство, строительство": ["technical", "practical", "detail"],
    "Финансы, аналитика, право": ["analytical", "quantitative", "detail"],
    "Образование, психология, помощь людям": ["helping", "social", "verbal"],
    "Дизайн, креатив, медиа": ["creative", "exploratory", "verbal"],
    "Наука, исследования, экология": ["analytical", "quantitative", "exploratory"],
    "Маркетинг, коммуникации, контент": ["verbal", "creative", "social"],
    "Бизнес, управление, продажи": ["leadership", "social", "structured"],
    "Логистика, операции, сервис, гос/соцсфера": ["structured", "practical", "detail"],
}


class ProfessionMatchService:
    def rank(
        self,
        profile_scores: dict[str, int],
        matrix_rows: list,
        profession_by_id: dict,
        target_count: int,
    ) -> list[dict[str, Any]]:
        recommendations = []
        strengths = {name for name, _ in sorted(profile_scores.items(), key=lambda x: (-x[1], x[0]))[:3]}

        for matrix in matrix_rows:
            profession = profession_by_id.get(matrix.profession_id)
            if not profession:
                continue
            base_score = self._base_similarity(profile_scores, matrix)
            penalty = self._critical_penalty(profile_scores, matrix)
            bonus = self._small_bonus(strengths, matrix)
            strong_fit_bonus = self._strong_fit_bonus(profile_scores, matrix)
            fallback_penalty = self._generic_fallback_penalty(profile_scores, matrix)
            admissibility = self._admissibility(profile_scores, matrix, profession.cluster)
            admissibility_penalty = 0.0 if admissibility["eligible"] else 11.0
            admissibility_bonus = 2.5 if admissibility["strong"] else 0.0

            final_score = max(
                0.0,
                min(
                    100.0,
                    base_score
                    - penalty
                    - fallback_penalty
                    - admissibility_penalty
                    + bonus
                    + strong_fit_bonus
                    + admissibility_bonus,
                ),
            )
            recommendations.append(
                {
                    "slug": profession.slug,
                    "title": profession.title,
                    "cluster": profession.cluster,
                    "summary": profession.summary,
                    "match_score": int(round(final_score)),
                    "important_subjects": list(matrix.important_subjects or []),
                    "first_steps": list(matrix.first_steps_template or []),
                    "why_fit": matrix.why_fit_template,
                    "eligible_for_top": admissibility["eligible"],
                    "admissibility_score": round(admissibility["score"], 3),
                    "_score": final_score,
                }
            )

        recommendations.sort(key=lambda item: (-item["_score"], item["slug"]))
        recommendations = self._prefer_applied_on_close_scores(recommendations)

        top = recommendations[:target_count]
        cluster_counts = Counter(item["cluster"] for item in top)
        eligible_count = sum(1 for item in top if item["eligible_for_top"])

        for item in top:
            item["cluster_rank_density"] = cluster_counts[item["cluster"]] / float(target_count)
            item["admissibility_legitimacy"] = round(eligible_count / float(target_count), 3)
            item.pop("_score", None)
        return top

    @staticmethod
    def _base_similarity(profile_scores: dict[str, int], matrix: Any) -> float:
        weights = matrix.dimension_weights_json or {}
        targets = matrix.target_profile_json or {}
        total_weight = 0.0
        weighted_score = 0.0
        for dim, target in targets.items():
            if dim not in profile_scores:
                continue
            weight = float(weights.get(dim, 1.0))
            similarity = 100.0 - abs(float(profile_scores[dim]) - float(target))
            weighted_score += max(0.0, similarity) * weight
            total_weight += weight
        if total_weight == 0:
            return 0.0
        return weighted_score / total_weight

    @staticmethod
    def _critical_penalty(profile_scores: dict[str, int], matrix: Any) -> float:
        penalty = 0.0
        targets = matrix.target_profile_json or {}
        for dim in matrix.critical_dimensions or []:
            profile = float(profile_scores.get(dim, 50))
            target = float(targets.get(dim, 50))
            gap = target - profile
            if gap > 10:
                penalty += min(12.0, gap * 0.3)
        return penalty

    @staticmethod
    def _small_bonus(strengths: set[str], matrix: Any) -> float:
        if not strengths:
            return 0.0
        critical = set(matrix.critical_dimensions or [])
        overlap = len(strengths.intersection(critical))
        bonus = min(BONUS_CAP, overlap * 1.5)
        return min(BONUS_CAP, bonus)

    @staticmethod
    def _strong_fit_bonus(profile_scores: dict[str, int], matrix: Any) -> float:
        top_dims = [k for k, _ in sorted(profile_scores.items(), key=lambda item: (-item[1], item[0]))[:3]]
        critical = list(matrix.critical_dimensions or [])
        targets = matrix.target_profile_json or {}
        hit = 0
        for dim in top_dims:
            if dim in critical and profile_scores.get(dim, 0) >= float(targets.get(dim, 60)) - 8:
                hit += 1
        if hit >= 3:
            return 6.0
        if hit == 2:
            return 3.5
        if hit == 1:
            return 1.0
        return 0.0

    @staticmethod
    def _generic_fallback_penalty(profile_scores: dict[str, int], matrix: Any) -> float:
        critical = list(matrix.critical_dimensions or [])
        if not critical:
            return 0.0
        top_dims = {k for k, _ in sorted(profile_scores.items(), key=lambda item: (-item[1], item[0]))[:3]}
        critical_hits = len(top_dims.intersection(critical))
        if critical_hits >= 2:
            return 0.0

        targets = matrix.target_profile_json or {}
        avg_gap = 0.0
        for dim in critical:
            avg_gap += max(0.0, float(targets.get(dim, 50)) - float(profile_scores.get(dim, 50)))
        avg_gap = avg_gap / float(len(critical))

        if critical_hits == 0 and avg_gap > 12:
            return min(8.0, 3.0 + avg_gap * 0.2)
        if critical_hits == 1 and avg_gap > 10:
            return min(5.5, 1.5 + avg_gap * 0.15)
        return 0.0

    @staticmethod
    def _admissibility(profile_scores: dict[str, int], matrix: Any, cluster: str) -> dict[str, Any]:
        top_dims = [k for k, _ in sorted(profile_scores.items(), key=lambda item: (-item[1], item[0]))[:3]]
        top_set = set(top_dims)
        critical = list(matrix.critical_dimensions or [])
        critical_set = set(critical)
        targets = matrix.target_profile_json or {}

        top_overlap = len(top_set.intersection(critical_set))
        critical_fit = 0
        for dim in critical:
            if profile_scores.get(dim, 50) >= float(targets.get(dim, 60)) - 10:
                critical_fit += 1
        critical_ratio = (critical_fit / float(len(critical))) if critical else 0.0

        rule_dims = CLUSTER_ADMISSIBILITY_RULES.get(cluster, [])
        rule_hits = sum(1 for dim in rule_dims if profile_scores.get(dim, 0) >= 66)
        rule_ok = rule_hits >= 2

        strong = top_overlap >= 2 and critical_ratio >= 0.67
        eligible = strong or critical_ratio >= 0.67 or rule_ok
        score = (top_overlap / 3.0) * 0.45 + critical_ratio * 0.4 + (0.15 if rule_ok else 0.0)

        return {
            "eligible": eligible,
            "strong": strong,
            "score": max(0.0, min(1.0, score)),
        }

    @staticmethod
    def _prefer_applied_on_close_scores(recommendations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        adjusted = []
        for item in recommendations:
            score = float(item["_score"])
            if item["cluster"] in ABSTRACT_CLUSTERS:
                score -= 1.5
            adjusted.append({**item, "_score": score})

        adjusted.sort(key=lambda item: (-item["_score"], item["slug"]))

        for i in range(len(adjusted) - 1):
            curr = adjusted[i]
            nxt = adjusted[i + 1]
            if curr["cluster"] in ABSTRACT_CLUSTERS and nxt["cluster"] not in ABSTRACT_CLUSTERS:
                if abs(curr["_score"] - nxt["_score"]) <= 2.5 and nxt.get("eligible_for_top"):
                    adjusted[i], adjusted[i + 1] = adjusted[i + 1], adjusted[i]

        adjusted.sort(key=lambda item: (-item["_score"], item["slug"]))
        return adjusted
