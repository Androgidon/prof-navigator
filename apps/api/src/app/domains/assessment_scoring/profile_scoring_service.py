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

from app.domains.assessment_scoring.full_scoring_blueprint_v1 import FullScoringBlueprintV1

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

DEEP_V1_RUNTIME_BUCKET_WEIGHTS = {
    "self_report": 0.24,
    "situational": 0.30,
    "subjects_hobbies": 0.24,
    "tasks_calibration": 0.22,
}

DEEP_V1_RUNTIME_BLOCK_WEIGHTS = {
    "interests_and_task_preferences": 0.22,
    "subjects_profile": 0.09,
    "subject_profile": 0.09,
    "hobbies_and_activities": 0.09,
    "hobbies_and_real_activities": 0.09,
    "work_style_and_environment": 0.10,
    "behavioral_situations": 0.30,
    "mini_cognitive_tasks": 0.20,
    "consistency_crosscheck": 0.18,
}

DEEP_V1_QUESTION_TYPE_ALIASES = {
    "likert": "likert_5",
    "forced_choice": "single_select_4",
    "single_select": "single_select_4",
    "situational": "situational_single",
    "mini_task": "mini_task",
    "multi_select": "multi_select_2",
}


class ProfileScoringService:
    def compute(
        self,
        questions: list,
        answers_json: dict[str, Any],
        scoring_config_json: dict[str, Any],
    ) -> dict[str, Any]:
        assessment_slug = str(scoring_config_json.get("assessment_slug") or "")
        if assessment_slug == "deep_v1" and len(questions) >= 40:
            return self._compute_full_v1(questions=questions, answers_json=answers_json)

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

    def _compute_full_v1(self, questions: list, answers_json: dict[str, Any]) -> dict[str, Any]:
        blueprint = FullScoringBlueprintV1()
        normalized_questions = [self._normalize_deep_v1_question_payload(question) for question in questions]
        signals = blueprint.extract_signals(normalized_questions, answers_json)
        dimension_scores = blueprint.compute_dimension_scores(
            signals,
            block_weight_overrides={**DEEP_V1_RUNTIME_BLOCK_WEIGHTS, "M7": 0.14, "M8": 0.14},
            adaptive_blend_override=0.24,
            adaptive_delta_cap_override=16.0,
        )

        profile_scores = {
            dim: int(round(float(data.get("score", 50.0))))
            for dim, data in dimension_scores.items()
        }
        boundary_scores = blueprint.compute_boundary_scores(
            dimension_scores,
            answers_json,
            boundary_weight_overrides={
                "helping_vs_marketing": {"helping": 1.15, "verbal": 1.0, "social": 0.65, "creative": 1.2},
                "engineering_vs_science": {
                    "engineering": {"practical": 0.52, "technical": 0.30, "detail": 0.18},
                    "science": {"exploratory": 0.40, "analytical": 0.38, "quantitative": 0.22},
                },
            },
        )
        validation_hooks = blueprint.validation_hooks(dimension_scores, boundary_scores)
        validation_hooks["runtime_question_types"] = self._runtime_question_type_counts(questions)
        validation_hooks["runtime_blocks"] = self._runtime_block_counts(questions)
        fallback_dimensions = sum(1 for item in dimension_scores.values() if item.get("used_fallback", False))

        profile_summary = {
            "top_dimensions": [k for k, _ in sorted(profile_scores.items(), key=lambda item: (-item[1], item[0]))[:3]],
            "label": "stable",
            "starter_dataset_limited": False,
            "message": "Deep v1 profile computed from runtime-normalized evidence.",
            "boundary_scores": {
                key: {
                    "lean": value.lean,
                    "margin": round(value.margin, 2),
                    "stability": value.stability,
                }
                for key, value in boundary_scores.items()
            },
        }

        return {
            "profile_scores": profile_scores,
            "dimension_evidence": dimension_scores,
            "fallback_dimensions": fallback_dimensions,
            "starter_dataset_limited": False,
            "profile_summary": profile_summary,
            "boundary_scores": {
                key: {
                    "lean": value.lean,
                    "margin": round(value.margin, 2),
                    "stability": value.stability,
                }
                for key, value in boundary_scores.items()
            },
            "validation_hooks": validation_hooks,
        }

    @staticmethod
    def _normalize_deep_v1_question_payload(question: Any) -> Any:
        normalized_type = DEEP_V1_QUESTION_TYPE_ALIASES.get(
            str(getattr(question, "question_type", "") or ""),
            str(getattr(question, "question_type", "") or ""),
        )
        return type("DeepV1Question", (), {
            "question_id": getattr(question, "question_id", None),
            "block": getattr(question, "block", ""),
            "question_type": normalized_type,
            "options_json": getattr(question, "options_json", []) or [],
        })

    @staticmethod
    def _runtime_question_type_counts(questions: list[Any]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for question in questions:
            runtime_type = str(getattr(question, "question_type", "") or "")
            mapped = DEEP_V1_QUESTION_TYPE_ALIASES.get(runtime_type, runtime_type)
            key = f"{runtime_type}->{mapped}" if runtime_type != mapped else runtime_type
            counts[key] = counts.get(key, 0) + 1
        return counts

    @staticmethod
    def _runtime_block_counts(questions: list[Any]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for question in questions:
            block = str(getattr(question, "block", "") or "unknown")
            counts[block] = counts.get(block, 0) + 1
        return counts

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
