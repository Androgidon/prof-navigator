from __future__ import annotations

from typing import Any, Optional


class ConsistencyService:
    def compute(
        self,
        answers_json: dict[str, Any],
        dimension_evidence: dict[str, Any],
        total_questions: int,
        fallback_dimensions: int,
        recommendations: Optional[list[dict[str, Any]]] = None,
        profile_scores: Optional[dict[str, int]] = None,
    ) -> dict[str, Any]:
        answered = len(answers_json)
        coverage = (answered / total_questions) if total_questions else 0.0
        evidence_dimensions = sum(1 for item in dimension_evidence.values() if item["evidence_count"] > 0)
        dimension_coverage = evidence_dimensions / 12.0

        answer_values = []
        for payload in answers_json.values():
            value = payload.get("value") if isinstance(payload, dict) else None
            if isinstance(value, (int, float)):
                answer_values.append(float(value))
        monotone_penalty = 0.0
        if len(answer_values) >= 3 and len(set(int(v) for v in answer_values)) == 1:
            monotone_penalty = 0.15

        consistency = 45.0 + coverage * 22.0 + dimension_coverage * 13.0 - monotone_penalty * 100.0
        consistency = max(35.0, min(82.0, consistency))

        fallback_ratio = fallback_dimensions / 12.0
        confidence_score = (coverage * 35.0) + (consistency / 100.0 * 20.0) + (dimension_coverage * 45.0)
        confidence_score -= fallback_ratio * 30.0
        confidence_score = max(0.0, min(95.0, confidence_score))

        if coverage < 0.75:
            confidence_score = min(confidence_score, 72.0)
        if dimension_coverage < 0.55:
            confidence_score = min(confidence_score, 68.0)

        top_gap_penalty = 0.0
        ambiguity_penalty = 0.0
        coherence_penalty = 0.0
        admissibility_penalty = 0.0
        abstract_fallback_penalty = 0.0
        if recommendations and len(recommendations) >= 2:
            top_gap = float(recommendations[0]["match_score"] - recommendations[1]["match_score"])
            if top_gap < 4:
                top_gap_penalty = 12.0
            elif top_gap < 7:
                top_gap_penalty = 7.0

            close_scores = [item for item in recommendations[:5] if (recommendations[0]["match_score"] - item["match_score"]) <= 3]
            close_clusters = {item["cluster"] for item in close_scores}
            if len(close_scores) >= 4 and len(close_clusters) >= 3:
                ambiguity_penalty = 10.0
            elif len(close_scores) >= 3 and len(close_clusters) >= 2:
                ambiguity_penalty = 6.0

            top5 = recommendations[:5]
            cluster_counts = {}
            for item in top5:
                cluster_counts[item["cluster"]] = cluster_counts.get(item["cluster"], 0) + 1
            dominant_cluster = max(cluster_counts.values()) if cluster_counts else 0
            coherence_factor = dominant_cluster / float(len(top5)) if top5 else 0.0
            if coherence_factor < 0.4:
                coherence_penalty = 8.0
            elif coherence_factor < 0.55:
                coherence_penalty = 4.0

            eligible = sum(1 for item in top5 if item.get("eligible_for_top", False))
            legitimacy = eligible / float(len(top5)) if top5 else 0.0
            if legitimacy < 0.4:
                admissibility_penalty = 10.0
            elif legitimacy < 0.6:
                admissibility_penalty = 5.0

            abstract_clusters = {"Наука, исследования, экология", "Бизнес, управление, продажи"}
            abstract_count = sum(1 for item in top5 if item["cluster"] in abstract_clusters)
            abstract_ratio = abstract_count / float(len(top5)) if top5 else 0.0
            if abstract_ratio > 0.6:
                abstract_fallback_penalty = 10.0
            elif abstract_ratio > 0.4:
                abstract_fallback_penalty = 5.0

        peakiness_penalty = 0.0
        if profile_scores:
            vals = list(profile_scores.values())
            spread = max(vals) - min(vals)
            if spread < 18:
                peakiness_penalty = 10.0
            elif spread < 25:
                peakiness_penalty = 6.0

        confidence_score -= (
            top_gap_penalty
            + ambiguity_penalty
            + peakiness_penalty
            + coherence_penalty
            + admissibility_penalty
            + abstract_fallback_penalty
        )
        confidence_score = max(0.0, min(95.0, confidence_score))

        if confidence_score >= 78.0:
            level = "high"
        elif confidence_score >= 52.0:
            level = "medium"
        else:
            level = "low"

        return {
            "consistency_score": round(consistency, 2),
            "confidence_score": round(confidence_score, 2),
            "confidence_level": level,
            "coverage": round(coverage, 4),
            "dimension_coverage": round(dimension_coverage, 4),
            "fallback_ratio": round(fallback_ratio, 4),
            "top_gap_penalty": round(top_gap_penalty, 2),
            "ambiguity_penalty": round(ambiguity_penalty, 2),
            "peakiness_penalty": round(peakiness_penalty, 2),
            "cluster_coherence_penalty": round(coherence_penalty, 2),
            "admissibility_legitimacy_penalty": round(admissibility_penalty, 2),
            "abstract_fallback_penalty": round(abstract_fallback_penalty, 2),
        }
