from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from app.domains.assessment_scoring.full_question_bank_v1 import (
    BOUNDARY_IDS,
    FULL_QUESTION_BANK_V1,
    FULL_SIGNAL_BANDS,
    FULL_V1_ADAPTIVE_BLEND,
    FULL_V1_ADAPTIVE_DELTA_CAP,
    FULL_V1_BLOCK_WEIGHTS,
)
from app.domains.assessment_scoring.profile_scoring_service import DIMENSIONS


@dataclass
class BoundaryScore:
    boundary_id: str
    lean: str
    margin: float
    stability: str


class FullScoringBlueprintV1:
    def __init__(self) -> None:
        self._meta_by_id = {item["question_id"]: item for item in FULL_QUESTION_BANK_V1}
        self._dimension_index = self._build_dimension_index()

    @staticmethod
    def _band_midpoint(band: str) -> float:
        low, high = FULL_SIGNAL_BANDS[band]
        return (low + high) / 2.0

    def _build_dimension_index(self) -> Dict[str, List[Dict[str, Any]]]:
        index = {dim: [] for dim in DIMENSIONS}
        for meta in FULL_QUESTION_BANK_V1:
            pd = meta["primary_dimension"]
            if pd in index:
                index[pd].append({"question_id": meta["question_id"], "is_primary": True, "block": meta["block"], "is_core": meta["is_core"]})
            for sd in meta["secondary_dimensions"]:
                if sd in index:
                    index[sd].append({"question_id": meta["question_id"], "is_primary": False, "block": meta["block"], "is_core": meta["is_core"]})
        return index

    def extract_signals(self, questions: List[Any], answers_json: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        question_map = {q.question_id: q for q in questions}
        out: dict[str, list[dict[str, Any]]] = {dim: [] for dim in DIMENSIONS}

        for question_id, answer in answers_json.items():
            q = question_map.get(question_id)
            meta = self._meta_by_id.get(question_id)
            if not q or not meta:
                continue

            qtype = str(meta["question_type"])
            extracted = self._extract_by_type(qtype, q, answer, meta)
            for dim, signal in extracted.items():
                if dim in out:
                    out[dim].append(signal)

        return out

    def _extract_by_type(self, qtype: str, question: Any, answer: Dict[str, Any], meta: Any) -> Dict[str, Dict[str, Any]]:
        primary = str(meta["primary_dimension"])
        secondary = [str(item) for item in meta["secondary_dimensions"]]

        if qtype == "likert_5":
            value_map = {1: 0.0, 2: 25.0, 3: 50.0, 4: 75.0, 5: 100.0}
            raw = answer.get("value")
            mapped = value_map.get(int(raw), 50.0) if isinstance(raw, (int, float)) else 50.0
            result = {
                primary: {
                    "value": mapped,
                    "weight": 1.0,
                    "block": meta["block"],
                    "is_core": meta["is_core"],
                    "source": qtype,
                }
            }
            for dim in secondary:
                result[dim] = {
                    "value": mapped,
                    "weight": 0.55,
                    "block": meta["block"],
                    "is_core": meta["is_core"],
                    "source": qtype,
                }
            return result

        if qtype in {"single_select_4", "situational_single", "mini_task"}:
            key = answer.get("key")
            selected = None
            for option in (question.options_json or []):
                if option.get("key") == key:
                    selected = option
                    break
            option_weights = (selected or {}).get("weights_by_dimension") or {}
            base_weight = 1.25 if qtype == "situational_single" else (1.3 if qtype == "mini_task" else 1.0)

            result: dict[str, dict[str, Any]] = {}
            dims = [primary, *secondary]
            for dim in dims:
                coeff = float(option_weights.get(dim, 0.0))
                if coeff >= 0.75:
                    value = self._band_midpoint("strong")
                elif coeff >= 0.45:
                    value = self._band_midpoint("medium")
                elif coeff > 0:
                    value = self._band_midpoint("light")
                else:
                    value = self._band_midpoint("negative")

                weight = base_weight if dim == primary else base_weight * 0.7
                if coeff == 0:
                    weight *= 0.35
                result[dim] = {
                    "value": value,
                    "weight": weight,
                    "block": meta["block"],
                    "is_core": meta["is_core"],
                    "source": qtype,
                }
            return result

        if qtype == "multi_select_2":
            keys = answer.get("keys") or []
            selected = [opt for opt in (question.options_json or []) if opt.get("key") in keys]
            dims = [primary, *secondary]
            result: dict[str, dict[str, Any]] = {}
            for dim in dims:
                coeffs = [float((opt.get("weights_by_dimension") or {}).get(dim, 0.0)) for opt in selected]
                avg = (sum(coeffs) / len(coeffs)) if coeffs else 0.0
                if avg >= 0.75:
                    value = self._band_midpoint("strong")
                elif avg >= 0.45:
                    value = self._band_midpoint("medium")
                elif avg > 0:
                    value = self._band_midpoint("light")
                else:
                    value = self._band_midpoint("negative")
                mixed = len(set(round(c, 2) for c in coeffs)) > 1 if coeffs else False
                weight = 1.1 if not mixed else 0.85
                if dim != primary:
                    weight *= 0.7
                result[dim] = {
                    "value": value,
                    "weight": weight,
                    "block": meta["block"],
                    "is_core": meta["is_core"],
                    "source": qtype,
                    "mixed_evidence": mixed,
                }
            return result

        return {
            primary: {
                "value": 50.0,
                "weight": 0.8,
                "block": meta["block"],
                "is_core": meta["is_core"],
                "source": "fallback",
            }
        }

    def compute_dimension_scores(
        self,
        signals: Dict[str, List[Dict[str, Any]]],
        block_weight_overrides: Optional[Dict[str, float]] = None,
        adaptive_blend_override: Optional[float] = None,
        adaptive_delta_cap_override: Optional[float] = None,
    ) -> Dict[str, Any]:
        output: dict[str, Any] = {}
        macro_block_weights = block_weight_overrides or FULL_V1_BLOCK_WEIGHTS
        adaptive_blend = FULL_V1_ADAPTIVE_BLEND if adaptive_blend_override is None else float(adaptive_blend_override)
        adaptive_delta_cap = FULL_V1_ADAPTIVE_DELTA_CAP if adaptive_delta_cap_override is None else float(adaptive_delta_cap_override)

        for dim in DIMENSIONS:
            evidence = signals.get(dim, [])
            if not evidence:
                output[dim] = {
                    "score": 50.0,
                    "core_score": 50.0,
                    "adaptive_delta": 0.0,
                    "evidence_count": 0,
                    "used_fallback": True,
                    "block_scores": {},
                }
                continue

            block_scores: dict[str, float] = {}
            block_weights: dict[str, float] = {}
            core_values: List[Tuple[float, float]] = []
            adaptive_values: List[Tuple[float, float]] = []

            for item in evidence:
                block = str(item.get("block") or "B1")
                value = float(item.get("value", 50.0))
                weight = float(item.get("weight", 1.0))
                block_scores[block] = block_scores.get(block, 0.0) + value * weight
                block_weights[block] = block_weights.get(block, 0.0) + weight

                if bool(item.get("is_core", True)):
                    core_values.append((value, weight))
                else:
                    adaptive_values.append((value, weight))

            normalized_block = {}
            for block, total in block_scores.items():
                bw = block_weights.get(block, 1.0)
                normalized_block[block] = total / bw if bw else 50.0

            core_aggregate = 50.0
            if core_values:
                numerator = sum(v * w for v, w in core_values)
                denominator = sum(w for _, w in core_values)
                core_aggregate = numerator / denominator if denominator else 50.0

            adaptive_aggregate = core_aggregate
            if adaptive_values:
                numerator = sum(v * w for v, w in adaptive_values)
                denominator = sum(w for _, w in adaptive_values)
                adaptive_aggregate = numerator / denominator if denominator else core_aggregate

            adaptive_delta = adaptive_aggregate - core_aggregate
            adaptive_delta = max(-adaptive_delta_cap, min(adaptive_delta_cap, adaptive_delta))
            final_score = (1.0 - adaptive_blend) * core_aggregate + adaptive_blend * (core_aggregate + adaptive_delta)

            # block macro-weight reconciliation
            macro_numerator = 0.0
            macro_weight = 0.0
            for block, bscore in normalized_block.items():
                if block in macro_block_weights:
                    w = float(macro_block_weights[block])
                    macro_numerator += bscore * w
                    macro_weight += w
            if macro_weight > 0:
                final_score = 0.6 * final_score + 0.4 * (macro_numerator / macro_weight)

            output[dim] = {
                "score": round(max(0.0, min(100.0, final_score)), 2),
                "core_score": round(core_aggregate, 2),
                "adaptive_delta": round(adaptive_delta, 2),
                "evidence_count": len(evidence),
                "used_fallback": False,
                "block_scores": {k: round(v, 2) for k, v in normalized_block.items()},
            }

        return output

    def compute_boundary_scores(
        self,
        dimension_scores: Dict[str, Any],
        answers_json: Dict[str, Any],
        boundary_weight_overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, BoundaryScore]:
        dim = {k: float(v.get("score", 50.0)) for k, v in dimension_scores.items()}
        overrides = boundary_weight_overrides or {}

        def _stability(margin: float) -> str:
            if margin >= 18:
                return "high"
            if margin >= 10:
                return "medium"
            return "low"

        out: dict[str, BoundaryScore] = {}

        hm_weights = overrides.get("helping_vs_marketing") or {}
        hm_helping_w = float(hm_weights.get("helping", 1.0))
        hm_verbal_w = float(hm_weights.get("verbal", 1.0))
        hm_social_w = float(hm_weights.get("social", 1.0))
        hm_creative_w = float(hm_weights.get("creative", 1.0))
        hm_a = (dim.get("helping", 50) * hm_helping_w + dim.get("verbal", 50) * hm_verbal_w) / (hm_helping_w + hm_verbal_w)
        hm_b = (dim.get("social", 50) * hm_social_w + dim.get("creative", 50) * hm_creative_w) / (hm_social_w + hm_creative_w)
        hm_margin = abs(hm_a - hm_b)
        out["helping_vs_marketing"] = BoundaryScore("helping_vs_marketing", "helping" if hm_a >= hm_b else "marketing", hm_margin, _stability(hm_margin))

        p = dim.get("practical", 50)
        t = dim.get("technical", 50)
        s = dim.get("structured", 50)
        pts_sorted = sorted([("practical", p), ("technical", t), ("structured", s)], key=lambda x: x[1], reverse=True)
        pts_margin = pts_sorted[0][1] - pts_sorted[1][1]
        out["practical_vs_technical_vs_structured"] = BoundaryScore(
            "practical_vs_technical_vs_structured", pts_sorted[0][0], pts_margin, _stability(pts_margin)
        )

        es_weights = overrides.get("engineering_vs_science") or {}
        eng_weights = es_weights.get("engineering") or {}
        sci_weights = es_weights.get("science") or {}
        eng_pw = float(eng_weights.get("practical", 0.45))
        eng_tw = float(eng_weights.get("technical", 0.4))
        eng_dw = float(eng_weights.get("detail", 0.15))
        sci_ew = float(sci_weights.get("exploratory", 0.45))
        sci_aw = float(sci_weights.get("analytical", 0.35))
        sci_qw = float(sci_weights.get("quantitative", 0.2))
        eng = (dim.get("practical", 50) * eng_pw + dim.get("technical", 50) * eng_tw + dim.get("detail", 50) * eng_dw)
        sci = (dim.get("exploratory", 50) * sci_ew + dim.get("analytical", 50) * sci_aw + dim.get("quantitative", 50) * sci_qw)
        es_margin = abs(eng - sci)
        out["engineering_vs_science"] = BoundaryScore("engineering_vs_science", "engineering" if eng >= sci else "science", es_margin, _stability(es_margin))

        finance = (dim.get("quantitative", 50) * 0.45 + dim.get("detail", 50) * 0.3 + dim.get("structured", 50) * 0.25)
        ita = (dim.get("technical", 50) * 0.45 + dim.get("analytical", 50) * 0.35 + dim.get("structured", 50) * 0.2)
        fi_margin = abs(finance - ita)
        out["finance_vs_it_analytics"] = BoundaryScore("finance_vs_it_analytics", "finance" if finance >= ita else "it_analytics", fi_margin, _stability(fi_margin))

        law = (dim.get("verbal", 50) * 0.5 + dim.get("structured", 50) * 0.3 + dim.get("analytical", 50) * 0.2)
        public = (dim.get("structured", 50) * 0.5 + dim.get("helping", 50) * 0.3 + dim.get("social", 50) * 0.2)
        politics = (dim.get("leadership", 50) * 0.45 + dim.get("social", 50) * 0.35 + dim.get("verbal", 50) * 0.2)
        security = (dim.get("structured", 50) * 0.4 + dim.get("practical", 50) * 0.35 + dim.get("leadership", 50) * 0.25)
        group = sorted(
            [("law", law), ("public_service", public), ("politics", politics), ("security", security)],
            key=lambda x: x[1],
            reverse=True,
        )
        lpps_margin = group[0][1] - group[1][1]
        out["law_vs_public_vs_politics_vs_security"] = BoundaryScore(
            "law_vs_public_vs_politics_vs_security", group[0][0], lpps_margin, _stability(lpps_margin)
        )

        creative = (dim.get("creative", 50) * 0.5 + dim.get("verbal", 50) * 0.25 + dim.get("social", 50) * 0.25)
        acad = (dim.get("exploratory", 50) * 0.5 + dim.get("analytical", 50) * 0.3 + dim.get("quantitative", 50) * 0.2)
        cea_margin = abs(creative - acad)
        out["creative_vs_exploratory_academic"] = BoundaryScore(
            "creative_vs_exploratory_academic", "creative" if creative >= acad else "exploratory_academic", cea_margin, _stability(cea_margin)
        )

        return out

    def compute_full_confidence(
        self,
        dimension_scores: Dict[str, Any],
        boundary_scores: Dict[str, BoundaryScore],
        recommendations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        evidence_count = sum(int(item.get("evidence_count", 0)) for item in dimension_scores.values())
        avg_evidence = evidence_count / float(len(DIMENSIONS)) if DIMENSIONS else 0.0
        coverage_score = min(1.0, avg_evidence / 6.0)

        margins = [score.margin for score in boundary_scores.values()]
        boundary_sep = sum(margins) / float(len(margins)) if margins else 0.0
        boundary_component = min(1.0, boundary_sep / 20.0)

        ambiguity_penalty = 0.0
        if len(recommendations) >= 3:
            top = recommendations[:3]
            gap_1 = float(top[0].get("match_score", 0)) - float(top[1].get("match_score", 0))
            gap_2 = float(top[1].get("match_score", 0)) - float(top[2].get("match_score", 0))
            if gap_1 < 3:
                ambiguity_penalty += 0.12
            if gap_2 < 3:
                ambiguity_penalty += 0.08

        fallback_penalty = 0.0
        top5 = recommendations[:5]
        science_count = sum(1 for item in top5 if str(item.get("cluster", "")).lower().startswith("наука"))
        if top5:
            science_ratio = science_count / float(len(top5))
            if science_ratio > 0.4:
                fallback_penalty += 0.15

        base = 0.45 * coverage_score + 0.35 * boundary_component + 0.20
        score = max(0.0, min(1.0, base - ambiguity_penalty - fallback_penalty))
        score100 = round(score * 100.0, 2)

        if score100 >= 80.0:
            level = "high"
        elif score100 >= 52.0:
            level = "medium"
        else:
            level = "low"

        notes = []
        if ambiguity_penalty > 0:
            notes.append("Высокая близость альтернатив в топе")
        if fallback_penalty > 0:
            notes.append("Риск fallback в абстрактные кластеры")
        low_boundaries = [k for k, v in boundary_scores.items() if v.stability == "low"]
        if low_boundaries:
            notes.append("Низкая разделимость по части граничных модулей")

        return {
            "score": score100,
            "level": level,
            "notes": notes,
            "coverage_score": round(coverage_score, 4),
            "boundary_component": round(boundary_component, 4),
            "ambiguity_penalty": round(ambiguity_penalty, 4),
            "fallback_penalty": round(fallback_penalty, 4),
        }

    def validation_hooks(self, dimension_scores: Dict[str, Any], boundary_scores: Dict[str, BoundaryScore]) -> Dict[str, Any]:
        return {
            "dimension_coverage_ratio": round(
                sum(1 for item in dimension_scores.values() if not item.get("used_fallback", False)) / float(len(DIMENSIONS)),
                4,
            ),
            "boundary_low_stability_count": sum(1 for item in boundary_scores.values() if item.stability == "low"),
            "boundary_margins": {key: round(value.margin, 2) for key, value in boundary_scores.items()},
            "adaptive_questions_defined": sum(len(v) for v in BOUNDARY_IDS.values()),
            "question_bank_size": len(FULL_QUESTION_BANK_V1),
        }
