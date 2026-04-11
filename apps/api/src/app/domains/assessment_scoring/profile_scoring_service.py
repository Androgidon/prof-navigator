from __future__ import annotations

from typing import Any, Dict, List, Tuple

DIMENSIONS = [
    "analytical",
    "technical",
    "creative",
    "social",
    "helping",
    "leadership",
    "structured",
    "exploratory",
    "detail",
    "verbal",
    "quantitative",
    "practical",
]

BUCKET_ALIASES = {
    "interests_and_task_preferences": "self_report",
    "deep_interests": "self_report",
    "subjects_profile": "subjects_hobbies",
    "subject_profile": "subjects_hobbies",
    "hobbies_and_activities": "subjects_hobbies",
    "hobbies_and_real_activities": "subjects_hobbies",
    "work_style_and_environment": "self_report",
    "behavioral_situations": "situational",
    "mini_cognitive_tasks": "tasks_calibration",
}

DEFAULT_BUCKET_WEIGHTS = {
    "self_report": 0.4,
    "situational": 0.2,
    "subjects_hobbies": 0.2,
    "tasks_calibration": 0.2,
}


class ProfileScoringService:
    def compute(
        self,
        questions: list,
        answers_json: dict[str, Any],
        scoring_config_json: dict[str, Any],
    ) -> dict[str, Any]:
        question_map = {q.question_id: q for q in questions}

        # Collect (value, relevance_weight) pairs per bucket per dimension
        bucket_dim_signals: Dict[str, Dict[str, List[Tuple[float, float]]]] = {
            bucket: {dim: [] for dim in DIMENSIONS} for bucket in DEFAULT_BUCKET_WEIGHTS
        }
        dimension_evidence_counts = {dim: 0 for dim in DIMENSIONS}

        for question_id, answer_payload in answers_json.items():
            question = question_map.get(question_id)
            if not question:
                continue
            bucket = BUCKET_ALIASES.get(question.block, "self_report")
            extracted = self._extract_dimension_signals(question, answer_payload)
            for dim, (value, relevance) in extracted.items():
                bucket_dim_signals[bucket][dim].append((value, relevance))
                dimension_evidence_counts[dim] += 1

        bucket_weights = dict(DEFAULT_BUCKET_WEIGHTS)
        for key, val in (scoring_config_json.get("sources") or {}).items():
            if key in bucket_weights and isinstance(val, (int, float)):
                bucket_weights[key] = float(val)

        profile_scores: dict[str, int] = {}
        dimension_evidence: dict[str, Any] = {}
        fallback_dimensions = 0

        for dim in DIMENSIONS:
            weighted_sum = 0.0
            used_weight = 0.0
            bucket_breakdown = {}
            for bucket, bw in bucket_weights.items():
                signals = bucket_dim_signals[bucket][dim]
                if not signals:
                    continue
                # Weighted average by relevance within bucket
                total_rel = sum(rel for _, rel in signals)
                if total_rel == 0:
                    continue
                avg_value = sum(val * rel for val, rel in signals) / total_rel
                bucket_breakdown[bucket] = round(avg_value, 2)
                weighted_sum += avg_value * bw
                used_weight += bw
            if used_weight == 0:
                score = 50
                fallback_dimensions += 1
            else:
                score = int(round(weighted_sum / used_weight))
            score = max(0, min(100, score))
            profile_scores[dim] = score
            dimension_evidence[dim] = {
                "score": score,
                "evidence_count": dimension_evidence_counts[dim],
                "bucket_breakdown": bucket_breakdown,
                "used_fallback": dimension_evidence_counts[dim] == 0,
            }

        starter_dataset_limited = len(question_map) < 20
        profile_summary = self._build_profile_summary(profile_scores, starter_dataset_limited)

        return {
            "profile_scores": profile_scores,
            "dimension_evidence": dimension_evidence,
            "fallback_dimensions": fallback_dimensions,
            "starter_dataset_limited": starter_dataset_limited,
            "profile_summary": profile_summary,
        }

    def _extract_dimension_signals(
        self, question: Any, answer_payload: dict[str, Any]
    ) -> dict[str, Tuple[float, float]]:
        """Returns {dimension: (score_0_100, relevance_weight)}."""
        options = question.options_json or []
        q_weights = dict(question.weights_by_dimension_json or {})

        if question.question_type == "likert":
            value = float(answer_payload.get("value", 50))
            return self._signals_from_likert(value, q_weights)

        if question.question_type in {"forced_choice", "situational", "single_select"}:
            selected_key = answer_payload.get("key")
            return self._signals_from_choice(options, selected_key, q_weights)

        if question.question_type == "multi_select":
            keys = answer_payload.get("keys") or []
            return self._signals_from_multi_select(options, keys, q_weights)

        if question.question_type == "mini_task":
            selected_key = answer_payload.get("key")
            if selected_key is not None:
                return self._signals_from_choice(options, selected_key, q_weights)
            value = float(answer_payload.get("value", 50))
            return self._signals_from_likert(value, q_weights)

        value = float(answer_payload.get("value", 50))
        return self._signals_from_likert(value, q_weights)

    @staticmethod
    def _signals_from_likert(value: float, q_weights: dict[str, Any]) -> dict[str, Tuple[float, float]]:
        """Likert: the raw value IS the score; the question weight is relevance."""
        out: dict[str, Tuple[float, float]] = {}
        for dim, w in q_weights.items():
            if not isinstance(w, (int, float)):
                continue
            relevance = float(w)
            score = max(0.0, min(100.0, value))
            out[dim] = (score, relevance)
        return out

    @staticmethod
    def _signals_from_choice(
        options: list[dict[str, Any]],
        selected_key: Any,
        q_weights: dict[str, Any],
    ) -> dict[str, Tuple[float, float]]:
        """Choice: selected option's dimension weights determine the signal direction.
        Each option weight encodes 'how strongly this option signals this dimension'.
        We convert to a score: high option weight = high score, low/missing = low score.
        """
        selected_option = None
        for option in options:
            if option.get("key") == selected_key:
                selected_option = option
                break
        if not selected_option:
            out: dict[str, Tuple[float, float]] = {}
            for dim, w in q_weights.items():
                if isinstance(w, (int, float)):
                    out[dim] = (50.0, float(w))
            return out

        option_weights = selected_option.get("weights_by_dimension") or {}

        # Collect dimensions mentioned across ALL options (question scope)
        all_dims: set[str] = set()
        for opt in options:
            for d in (opt.get("weights_by_dimension") or {}):
                all_dims.add(d)

        out = {}
        for dim in all_dims:
            sel_val = float(option_weights.get(dim, 0.0))
            if sel_val > 0:
                # Selected option positively signals this dimension
                score = max(0.0, min(100.0, 15.0 + sel_val * 70.0))
            else:
                # User chose an option that does NOT signal this dimension,
                # but other options did — this is a mild negative signal
                score = 30.0
            relevance = float(q_weights.get(dim, 0.3))
            # Lower relevance for negative signals so they don't dominate
            if sel_val == 0:
                relevance *= 0.25
            out[dim] = (score, relevance)
        return out

    @staticmethod
    def _signals_from_multi_select(
        options: list[dict[str, Any]],
        keys: list[str],
        q_weights: dict[str, Any],
    ) -> dict[str, Tuple[float, float]]:
        """Multi-select: aggregate signals from selected options."""
        selected = [opt for opt in options if opt.get("key") in keys]
        if not selected:
            out: dict[str, Tuple[float, float]] = {}
            for dim, w in q_weights.items():
                if isinstance(w, (int, float)):
                    out[dim] = (50.0, float(w))
            return out

        # Collect dimensions from all options (question scope)
        all_dims: set[str] = set()
        for opt in options:
            for d in (opt.get("weights_by_dimension") or {}):
                all_dims.add(d)

        # Aggregate selected options
        dim_vals: dict[str, list[float]] = {}
        for opt in selected:
            for d in all_dims:
                v = float((opt.get("weights_by_dimension") or {}).get(d, 0.0))
                dim_vals.setdefault(d, []).append(v)

        out = {}
        for dim, vals in dim_vals.items():
            avg_sel = sum(vals) / len(vals) if vals else 0.0
            if avg_sel > 0:
                score = max(0.0, min(100.0, 15.0 + avg_sel * 70.0))
                relevance = float(q_weights.get(dim, 0.3))
            else:
                score = 30.0
                relevance = float(q_weights.get(dim, 0.3)) * 0.25
            out[dim] = (score, relevance)
        return out

    @staticmethod
    def _build_profile_summary(profile_scores: dict[str, int], starter_dataset_limited: bool) -> dict[str, Any]:
        sorted_dims = sorted(profile_scores.items(), key=lambda item: (-item[1], item[0]))
        top_dims = [name for name, _ in sorted_dims[:3]]
        summary = {
            "top_dimensions": top_dims,
            "label": "preliminary" if starter_dataset_limited else "stable",
            "starter_dataset_limited": starter_dataset_limited,
            "message": "Preliminary profile based on starter dataset; confidence is limited."
            if starter_dataset_limited
            else "Profile computed from available assessment evidence.",
        }
        return summary
