from __future__ import annotations

from typing import Any, Optional, Optional

from app.domains.assessment_results.repository import AssessmentResultRepository
from app.domains.result_explanations.service import ResultExplanationService


TEST_TITLES = {
    "express_v1": "Express тест",
    "deep_v1": "Deep тест",
    "full_v1": "Full тест",
}

_NICHE_KEYWORDS = (
    "track",
    "prosecut",
    "oncolog",
    "notary",
    "investigat",
    "customs",
    "border",
)


class PayloadAssemblyError(Exception):
    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


class AssessmentResultService:
    def __init__(self, repository: AssessmentResultRepository) -> None:
        self.repository = repository
        self.explanations = ResultExplanationService()

    async def get_existing_for_session(self, session_id: str):
        return await self.repository.get_by_session_id(session_id)

    async def create_result(
        self,
        session_id: str,
        assessment_slug: str,
        scoring_output: dict[str, Any],
        recommendations: list[dict[str, Any]],
        consistency_output: dict[str, Any],
    ):
        starter_dataset_limited = scoring_output["starter_dataset_limited"]
        top_strengths = self.explanations.build_top_strengths(
            scoring_output["profile_scores"], starter_dataset_limited
        )
        work_style = self.explanations.build_work_style(
            scoring_output["profile_scores"], starter_dataset_limited
        )
        next_steps = self.explanations.build_next_steps(starter_dataset_limited)

        payload = {
            "profile_scores": scoring_output["profile_scores"],
            "profile_summary": {
                **scoring_output["profile_summary"],
                "preliminary": starter_dataset_limited,
            },
            "top_strengths": top_strengths,
            "work_style": work_style,
            "recommendations": recommendations,
            "next_steps": next_steps,
            "confidence": {
                "score": consistency_output["confidence_score"],
                "level": consistency_output["confidence_level"],
                "starter_dataset_limited": starter_dataset_limited,
                "limited_reason": "Insufficient breadth of answered starter questions."
                if starter_dataset_limited
                else None,
            },
            "dimension_evidence": scoring_output["dimension_evidence"],
            "boundary_scores": scoring_output.get("boundary_scores") or {},
            "validation_hooks": scoring_output.get("validation_hooks") or {},
        }
        scoring_breakdown = {
            "consistency": consistency_output,
            "fallback_dimensions": scoring_output["fallback_dimensions"],
            "starter_dataset_limited": starter_dataset_limited,
            "boundary_scores": scoring_output.get("boundary_scores") or {},
            "validation_hooks": scoring_output.get("validation_hooks") or {},
        }
        entity = await self.repository.create(
            session_id=session_id,
            assessment_slug=assessment_slug,
            payload=payload,
            scoring_breakdown_json=scoring_breakdown,
        )
        return entity, payload

    async def list_user_history(self, user_id: str):
        rows = await self.repository.list_for_user(user_id)
        items = []
        for index, (result, session) in enumerate(rows):
            recommendations = list(result.recommendations_json or [])
            top_professions = [
                str(item.get("profession") or item.get("title") or item.get("slug") or "")
                for item in recommendations[:3]
                if (item.get("profession") or item.get("title") or item.get("slug"))
            ]
            completed_at = session.completed_at or result.created_at
            items.append(
                {
                    "result_id": str(result.id),
                    "assessment_slug": result.assessment_slug,
                    "test_title": TEST_TITLES.get(result.assessment_slug, result.assessment_slug),
                    "completed_at": completed_at,
                    "top_professions": top_professions,
                    "is_latest": index == 0,
                }
            )
        return items

    async def get_result_payload(self, result_id: str, user_id: Optional[str] = None):
        if user_id:
            row = await self.repository.get_for_user(user_id, result_id)
            if not row:
                return None
            entity, session = row
            completed_at = session.completed_at or entity.created_at
        else:
            row = await self.repository.get_with_session(result_id)
            if not row:
                return None
            entity, session = row
            completed_at = session.completed_at or entity.created_at

        return {
            "result_id": str(entity.id),
            "session_id": str(entity.session_id),
            "assessment_slug": entity.assessment_slug,
            "completed_at": completed_at,
            "status": "completed",
            "profile_scores": entity.profile_scores_json,
            "profile_summary": entity.profile_summary_json,
            "top_strengths": entity.top_strengths_json,
            "work_style": entity.work_style_json,
            "recommendations": entity.recommendations_json,
            "next_steps": entity.next_steps_json,
            "confidence": entity.confidence_json,
            "dimension_evidence": entity.scoring_breakdown_json,
        }

    def _strengths_with_explanations(self, top_strengths: list[dict[str, Any]]) -> list[dict[str, Any]]:
        output = []
        for item in top_strengths[:5]:
            dimension = str(item.get("dimension") or "")
            score = float(item.get("score") or 0)
            explanation = f"Сильная сторона: {dimension}. Помогает в учебных и проектных задачах."
            output.append({"dimension": dimension, "score": score, "explanation": explanation})
        return output

    def _derive_profile_type(self, profile_scores: dict[str, Any]) -> dict[str, Any]:
        sorted_dims = sorted(
            [(str(k), float(v)) for k, v in (profile_scores or {}).items()],
            key=lambda pair: pair[1],
            reverse=True,
        )
        primary = sorted_dims[0][0] if sorted_dims else "balanced"
        secondary = sorted_dims[1][0] if len(sorted_dims) > 1 else None
        return {
            "primary_family": primary,
            "secondary_modifier": secondary,
            "summary": "Профиль построен по сочетанию ваших ведущих учебных и поведенческих сигналов.",
        }

    def _is_broad_role(self, rec: dict[str, Any]) -> bool:
        title = str(rec.get("title") or "").lower()
        slug = str(rec.get("slug") or "").lower()
        return not any(keyword in title or keyword in slug for keyword in _NICHE_KEYWORDS)

    def _direction_affinity_bonus(self, direction: str, top_dims: set[str]) -> float:
        d = direction.lower()
        if "инженерия" in d and ({"technical", "practical"} & top_dims):
            return 6.0
        if "образование" in d and ({"helping", "verbal", "social"} & top_dims):
            return 5.0
        if "маркетинг" in d and ({"creative", "verbal", "social"} & top_dims):
            return 4.0
        if "финансы" in d and ({"quantitative", "analytical", "detail"} & top_dims):
            return 4.0
        if "наука" in d and ({"exploratory", "analytical"} & top_dims):
            return 3.0
        return 0.0

    def _direction_affinity_penalty(self, direction: str, top_dims: set[str]) -> float:
        d = direction.lower()
        if "наука" in d and ("practical" in top_dims or "helping" in top_dims):
            return 5.0
        if "маркетинг" in d and "helping" in top_dims and "creative" not in top_dims:
            return 4.0
        if "бизнес" in d and ("helping" in top_dims or "practical" in top_dims) and "leadership" not in top_dims:
            return 3.0
        return 0.0

    def _aggregate_directions(self, recommendations: list[dict[str, Any]], profile_scores: dict[str, Any]) -> list[dict[str, Any]]:
        # Hard rule against size bias: direction score based on top-k mean only, not item count.
        by_direction: dict[str, list[dict[str, Any]]] = {}
        for rec in recommendations:
            direction = str(rec.get("cluster") or "Другое")
            by_direction.setdefault(direction, []).append(rec)

        sorted_dims = sorted(
            [(str(k), float(v)) for k, v in (profile_scores or {}).items()],
            key=lambda pair: pair[1],
            reverse=True,
        )
        top_dims = {dim for dim, _ in sorted_dims[:3]}

        rows: list[dict[str, Any]] = []
        for direction, items in by_direction.items():
            ranked = sorted(items, key=lambda x: float(x.get("match_score") or x.get("score") or 0), reverse=True)
            top_k = ranked[:2] if len(ranked) >= 2 else ranked
            if not top_k:
                continue
            top_mean = sum(float(x.get("match_score") or x.get("score") or 0) for x in top_k) / len(top_k)
            peak = float(top_k[0].get("match_score") or top_k[0].get("score") or 0)
            base_score = 0.7 * top_mean + 0.3 * peak
            direction_score = (
                base_score
                + self._direction_affinity_bonus(direction, top_dims)
                - self._direction_affinity_penalty(direction, top_dims)
            )
            rows.append(
                {
                    "direction_id": direction.lower().replace(" ", "-").replace(",", ""),
                    "direction_slug": direction.lower().replace(" ", "-").replace(",", ""),
                    "title": direction,
                    "direction_score": round(direction_score, 2),
                    "items": ranked,
                }
            )

        rows.sort(key=lambda x: x["direction_score"], reverse=True)
        return rows

    def _build_examples(self, direction_items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], bool]:
        preferred = [
            item
            for item in direction_items
            if self._is_broad_role(item) and str(item.get("summary") or "").strip()
        ]
        fallback_used = False
        selected = preferred[:5]
        if len(selected) < 3:
            fallback_used = True
            fallback_pool = [item for item in direction_items if self._is_broad_role(item)]
            selected = fallback_pool[:5]

        examples: list[dict[str, Any]] = []
        for rec in selected[:5]:
            examples.append(
                {
                    "profession_id": str(rec.get("slug") or rec.get("title") or "unknown"),
                    "profession_slug": str(rec.get("slug") or "unknown"),
                    "title": str(rec.get("title") or rec.get("profession") or "Профессия"),
                    "family_id": str(rec.get("cluster") or "generic").lower().replace(" ", "-"),
                    "family_title": str(rec.get("cluster") or "Общее направление"),
                    "rationale_tag": "broad_role",
                }
            )
        return examples, fallback_used

    def build_express_payload(self, payload: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        recommendations = list(payload.get("recommendations") or [])
        if not recommendations:
            raise PayloadAssemblyError("schema_data_issue", "Recommendations are required for express payload")

        profile_scores = payload.get("profile_scores") or {}
        directions = self._aggregate_directions(recommendations, profile_scores)
        if not directions:
            raise PayloadAssemblyError("aggregation_failure", "Direction aggregation returned empty set")

        confidence = payload.get("confidence") or {}
        confidence_score = float(confidence.get("score") or 0)
        confidence_level = str(confidence.get("level") or "medium")

        # Confidence recalibration for semantically weak top direction patterns.
        top_direction_title = directions[0]["title"].lower() if directions else ""
        sorted_dims = sorted(
            [(str(k), float(v)) for k, v in profile_scores.items()],
            key=lambda pair: pair[1],
            reverse=True,
        )
        top_dims = {dim for dim, _ in sorted_dims[:3]}
        if "наука" in top_direction_title and ("practical" in top_dims or "helping" in top_dims):
            confidence_score = max(35.0, confidence_score - 20.0)
            confidence_level = "medium" if confidence_level == "high" else confidence_level
        if "маркетинг" in top_direction_title and "helping" in top_dims and "creative" not in top_dims:
            confidence_score = max(40.0, confidence_score - 12.0)
            confidence_level = "medium" if confidence_level == "high" else confidence_level

        top_strengths = self._strengths_with_explanations(list(payload.get("top_strengths") or []))

        top_directions = []
        fallback_used_any = False
        for rank, direction in enumerate(directions[:3], start=1):
            examples, fallback_used = self._build_examples(direction["items"])
            fallback_used_any = fallback_used_any or fallback_used
            top_directions.append(
                {
                    "rank": rank,
                    "direction_id": direction["direction_id"],
                    "direction_slug": direction["direction_slug"],
                    "title": direction["title"],
                    "direction_score": direction["direction_score"],
                    "fit_band": "high" if rank == 1 else "medium",
                    "why_direction": "Направление выбрано по вашим сильным сторонам и согласованным сигналам ответов.",
                    "example_professions": examples,
                }
            )

        cta_type = "open_full_offer"
        if confidence_level in {"medium", "low"}:
            cta_type = "start_full_test"

        express_payload = {
            "result_id": payload["result_id"],
            "assessment_slug": payload["assessment_slug"],
            "payload_version": "express_result_v1",
            "completed_at": payload.get("completed_at"),
            "profile_type": self._derive_profile_type(payload.get("profile_scores") or {}),
            "top_strengths": top_strengths,
            "top_directions": top_directions,
            "next_steps_school_level": list((payload.get("next_steps") or {}).get("actions") or []),
            "confidence": {
                "score": confidence_score,
                "level": confidence_level,
                "user_message": "Результат показывает устойчивые направления. Для точного топа профессий используйте Full тест.",
            },
            "monetization_cta": {
                "target_action": cta_type,
                "target_url": "/full-test",
                "title": "Получить более точный результат",
                "text": "Full тест покажет точный Top-8 профессий, объяснение why-fit и персональные шаги развития.",
            },
        }
        return express_payload, fallback_used_any

    def build_full_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        recommendations = list(payload.get("recommendations") or [])
        if not recommendations:
            raise PayloadAssemblyError("schema_data_issue", "Recommendations are required for full payload")

        profile_scores = payload.get("profile_scores") or {}
        directions = self._aggregate_directions(recommendations, profile_scores)
        if not directions:
            raise PayloadAssemblyError("aggregation_failure", "Direction aggregation returned empty set")

        confidence = payload.get("confidence") or {}
        confidence_score = float(confidence.get("score") or 0)
        confidence_level = str(confidence.get("level") or "medium")

        top_direction_title = directions[0]["title"].lower() if directions else ""
        sorted_dims = sorted(
            [(str(k), float(v)) for k, v in profile_scores.items()],
            key=lambda pair: pair[1],
            reverse=True,
        )
        top_dims = {dim for dim, _ in sorted_dims[:3]}
        if "наука" in top_direction_title and ("practical" in top_dims or "helping" in top_dims):
            confidence_score = max(35.0, confidence_score - 20.0)
            confidence_level = "medium" if confidence_level == "high" else confidence_level
        if "маркетинг" in top_direction_title and "helping" in top_dims and "creative" not in top_dims:
            confidence_score = max(40.0, confidence_score - 12.0)
            confidence_level = "medium" if confidence_level == "high" else confidence_level

        top_professions = []
        ranked = sorted(recommendations, key=lambda x: float(x.get("match_score") or x.get("score") or 0), reverse=True)
        for rank, rec in enumerate(ranked[:8], start=1):
            score = float(rec.get("match_score") or rec.get("score") or 0)
            top_professions.append(
                {
                    "rank": rank,
                    "profession_id": str(rec.get("slug") or rec.get("title") or rank),
                    "profession_slug": str(rec.get("slug") or "unknown"),
                    "title": str(rec.get("title") or rec.get("profession") or "Профессия"),
                    "family_id": str(rec.get("cluster") or "generic").lower().replace(" ", "-"),
                    "family_title": str(rec.get("cluster") or "Общее направление"),
                    "direction_id": str(rec.get("cluster") or "generic").lower().replace(" ", "-"),
                    "direction_title": str(rec.get("cluster") or "Общее направление"),
                    "relevance_score": score,
                    "relevance_level": "high" if score >= 75 else "medium",
                    "why_fit": str(rec.get("why_fit") or "Профессия подходит по сочетанию ваших сильных сторон и стиля работы."),
                    "growth_recommendations": list(rec.get("first_steps") or [])[:4],
                }
            )

        top_directions = [
            {
                "rank": index + 1,
                "direction_id": direction["direction_id"],
                "direction_slug": direction["direction_slug"],
                "title": direction["title"],
                "direction_score": direction["direction_score"],
                "why_direction": "Направление подтверждается суммарным вкладом релевантных профессий.",
            }
            for index, direction in enumerate(directions[:3])
        ]

        alternatives = [
            {
                "pivot_type": "more_communication",
                "title": "Если хочешь больше общения",
                "explanation": "Варианты с высоким акцентом на взаимодействие и коммуникацию.",
                "professions": [
                    {
                        "profession_slug": p["profession_slug"],
                        "title": p["title"],
                        "reason": "Подходит для траектории с активной коммуникацией.",
                    }
                    for p in top_professions[2:4]
                ],
            },
            {
                "pivot_type": "more_practical",
                "title": "Если хочешь больше практики",
                "explanation": "Варианты, где больше прикладных действий и практических задач.",
                "professions": [
                    {
                        "profession_slug": p["profession_slug"],
                        "title": p["title"],
                        "reason": "Подходит для практического формата работы.",
                    }
                    for p in top_professions[4:6]
                ],
            },
            {
                "pivot_type": "more_structured",
                "title": "Если хочешь более структурную траекторию",
                "explanation": "Варианты с четкими процессами и предсказуемой структурой задач.",
                "professions": [
                    {
                        "profession_slug": p["profession_slug"],
                        "title": p["title"],
                        "reason": "Подходит для системного и последовательного стиля.",
                    }
                    for p in top_professions[6:8]
                ],
            },
        ]

        return {
            "result_id": payload["result_id"],
            "assessment_slug": payload["assessment_slug"],
            "payload_version": "full_result_v1",
            "completed_at": payload.get("completed_at"),
            "profile_type": self._derive_profile_type(payload.get("profile_scores") or {}),
            "top_strengths": top_professions and self._strengths_with_explanations(list(payload.get("top_strengths") or [])),
            "top_directions": top_directions,
            "top_professions": top_professions,
            "alternatives": alternatives,
            "development_plan": {
                "days_30": ["Выбрать 1 направление и сделать мини-проект."],
                "days_90": ["Собрать 2-3 учебных кейса в портфолио."],
                "days_180": ["Проверить стажировку/кружок/курс по приоритетной профессии."],
            },
            "overall_confidence": {
                "score": confidence_score,
                "level": confidence_level,
                "notes": [],
            },
        }
