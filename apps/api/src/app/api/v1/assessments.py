from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_optional_user
from app.db.session import get_db_session
from app.domains.assessment_catalog.repository import AssessmentCatalogRepository
from app.domains.assessment_results.repository import AssessmentResultRepository
from app.domains.assessment_results.result_policy import (
    diversification_fill_strategy,
    recommendation_target_count,
)
from app.domains.assessment_results.service import AssessmentResultService, PayloadAssemblyError
from app.domains.assessment_scoring.consistency_service import ConsistencyService
from app.domains.assessment_scoring.profession_match_service import ProfessionMatchService
from app.domains.assessment_scoring.profile_scoring_service import ProfileScoringService
from app.domains.assessment_sessions.repository import AssessmentSessionRepository
from app.domains.assessment_sessions.service import AssessmentSessionService
from app.domains.profession_catalog.repository import ProfessionCatalogRepository
from app.domains.profession_matrix.repository import ProfessionMatrixRepository
from app.domains.question_bank.repository import QuestionBankRepository
from app.domains.question_bank.selection_service import DeepQuestionSetNotReadyError
from app.schemas.assessment_engine import (
    CompleteAssessmentResponse,
    StartAssessmentV2Response,
    SubmitAssessmentAnswerRequest,
    SubmitAssessmentAnswerResponse,
)
from app.schemas.assessment_history import (
    AssessmentHistoryResponse,
    AssessmentResultDetailResponse,
)
from app.schemas.assessment_result_models import ExpressResultResponse, FullResultResponse
from app.schemas.test_session import StartAssessmentRequest
from app.models.user import User

router = APIRouter()


class CtaClickedEventRequest(BaseModel):
    result_id: str
    result_type: str
    target_action: str
    target_url_present: bool
    surface: str


def _is_flag_enabled(flag_name: str, default: bool = True) -> bool:
    import os

    raw = os.getenv(flag_name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _emit_event(name: str, **payload) -> None:
    # Minimal telemetry for iteration 1, non-blocking.
    print({"event": name, **payload})


def _flag_snapshot() -> dict[str, bool]:
    return {
        "results_v2_enabled": _is_flag_enabled("FEATURE_RESULTS_V2_ENABLED", True),
        "results_v2_express_endpoint": _is_flag_enabled("FEATURE_RESULTS_V2_EXPRESS_ENDPOINT", True),
        "results_v2_full_endpoint": _is_flag_enabled("FEATURE_RESULTS_V2_FULL_ENDPOINT", True),
        "results_v2_dashboard_history_renderer": _is_flag_enabled("FEATURE_RESULTS_V2_DASHBOARD_HISTORY_RENDERER", True),
        "results_v2_cta_actions": _is_flag_enabled("FEATURE_RESULTS_V2_CTA_ACTIONS", True),
    }


@router.post("/start", response_model=StartAssessmentV2Response)
async def start(
    payload: StartAssessmentRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_user),
) -> StartAssessmentV2Response:
    assessment_slug = payload.assessment_slug or "express_v1"
    experiment_mode = payload.experiment_mode or "baseline"
    session_service = AssessmentSessionService(
        catalog_repository=AssessmentCatalogRepository(db),
        question_repository=QuestionBankRepository(db),
        session_repository=AssessmentSessionRepository(db),
    )
    bound_user_id = str(current_user.id) if current_user else None
    try:
        session, catalog = await session_service.start(
            assessment_slug=assessment_slug,
            user_id=bound_user_id,
            experiment_mode=experiment_mode,
        )
    except DeepQuestionSetNotReadyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    if not session or not catalog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment version not found")
    await db.commit()
    return StartAssessmentV2Response(
        session_id=str(session.id),
        assessment_slug=assessment_slug,
        status=session.status,
        total_questions=len(session.question_set_json),
        recommendation_target_count=recommendation_target_count(assessment_slug),
    )


@router.get("/{session_id}/questions")
async def get_questions(
    session_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    session_repo = AssessmentSessionRepository(db)
    session = await session_repo.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    question_repo = QuestionBankRepository(db)
    questions = await question_repo.list_by_question_ids(
        session.assessment_slug, list(session.question_set_json or [])
    )
    questions.sort(key=lambda q: (q.order_hint or 0, q.question_id))
    return {
        "session_id": session_id,
        "total_questions": len(questions),
        "questions": [
            {
                "question_id": q.question_id,
                "block": q.block,
                "question_type": q.question_type,
                "text": q.text,
                "options": q.options_json or [],
                "is_required": q.is_required,
            }
            for q in questions
        ],
    }


@router.post("/{session_id}/answer", response_model=SubmitAssessmentAnswerResponse)
async def submit_answer(
    session_id: str,
    payload: SubmitAssessmentAnswerRequest,
    db: AsyncSession = Depends(get_db_session),
) -> SubmitAssessmentAnswerResponse:
    session_repo = AssessmentSessionRepository(db)
    session_service = AssessmentSessionService(
        catalog_repository=AssessmentCatalogRepository(db),
        question_repository=QuestionBankRepository(db),
        session_repository=session_repo,
    )
    session = await session_service.submit_answer(session_id, payload.question_id, payload.answer)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session or question not found")
    await db.commit()
    answered_count = len(session.answers_json or {})
    return SubmitAssessmentAnswerResponse(
        session_id=str(session.id),
        status=session.status,
        answered_questions=answered_count,
        total_questions=len(session.question_set_json or []),
    )


@router.post("/{session_id}/complete", response_model=CompleteAssessmentResponse)
async def complete_assessment(
    session_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> CompleteAssessmentResponse:
    session_repo = AssessmentSessionRepository(db)
    session = await session_repo.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    result_service = AssessmentResultService(AssessmentResultRepository(db))
    existing = await result_service.get_existing_for_session(session_id)
    if existing:
        return CompleteAssessmentResponse(
            session_id=session_id,
            result_id=str(existing.id),
            assessment_slug=session.assessment_slug,
            recommendation_target_count=recommendation_target_count(session.assessment_slug),
            diversification_shortage_fill_strategy=diversification_fill_strategy(),
        )

    question_repo = QuestionBankRepository(db)
    questions = await question_repo.list_by_question_ids(session.assessment_slug, list(session.question_set_json or []))

    catalog_repo = AssessmentCatalogRepository(db)
    catalog = await catalog_repo.get_by_slug(session.assessment_slug)
    if not catalog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment catalog not found")

    scoring_config = dict(catalog.scoring_config_json or {})
    scoring_config.setdefault("assessment_slug", session.assessment_slug)
    scoring = ProfileScoringService().compute(
        questions=questions,
        answers_json=dict(session.answers_json or {}),
        scoring_config_json=scoring_config,
    )
    matrix_version_slug = (catalog.question_mix_config_json or {}).get("matrix_version_slug", "matrix_v1")
    matrix_rows = await ProfessionMatrixRepository(db).list_by_version_slug(matrix_version_slug)
    profession_ids = [item.profession_id for item in matrix_rows]
    professions = await ProfessionCatalogRepository(db).list_by_ids(profession_ids)
    profession_by_id = {item.id: item for item in professions}

    recommendations = ProfessionMatchService().rank(
        profile_scores=scoring["profile_scores"],
        matrix_rows=matrix_rows,
        profession_by_id=profession_by_id,
        target_count=recommendation_target_count(session.assessment_slug),
        boundary_scores=scoring.get("boundary_scores"),
    )

    consistency_output = ConsistencyService().compute(
        answers_json=dict(session.answers_json or {}),
        dimension_evidence=scoring["dimension_evidence"],
        total_questions=len(session.question_set_json or []),
        fallback_dimensions=scoring["fallback_dimensions"],
        recommendations=recommendations,
        profile_scores=scoring["profile_scores"],
        boundary_scores=scoring.get("boundary_scores"),
    )

    _, _payload = await result_service.create_result(
        session_id=session_id,
        assessment_slug=session.assessment_slug,
        scoring_output=scoring,
        recommendations=recommendations,
        consistency_output=consistency_output,
    )
    await session_repo.mark_completed(
        session,
        consistency_score=consistency_output["consistency_score"],
        confidence_score=consistency_output["confidence_score"],
    )
    await db.commit()

    saved = await result_service.get_existing_for_session(session_id)
    if not saved:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Result persistence failed")
    return CompleteAssessmentResponse(
        session_id=session_id,
        result_id=str(saved.id),
        assessment_slug=session.assessment_slug,
        recommendation_target_count=recommendation_target_count(session.assessment_slug),
        diversification_shortage_fill_strategy=diversification_fill_strategy(),
    )


@router.get("/results/history", response_model=AssessmentHistoryResponse)
async def get_results_history(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> AssessmentHistoryResponse:
    service = AssessmentResultService(AssessmentResultRepository(db))
    items = await service.list_user_history(str(current_user.id))
    return AssessmentHistoryResponse(items=items)


@router.get("/results/{result_id}", response_model=AssessmentResultDetailResponse)
async def get_result(
    result_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_user),
) -> AssessmentResultDetailResponse:
    result_payload = await AssessmentResultService(AssessmentResultRepository(db)).get_result_payload(
        result_id,
        user_id=str(current_user.id) if current_user else None,
    )
    if not result_payload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")

    return AssessmentResultDetailResponse(
        result_id=result_payload["result_id"],
        assessment_slug=result_payload["assessment_slug"],
        completed_at=result_payload.get("completed_at"),
        profile_summary=result_payload["profile_summary"],
        top_strengths=result_payload["top_strengths"],
        work_style=result_payload["work_style"],
        recommendations=result_payload["recommendations"],
        next_steps=result_payload["next_steps"],
        confidence=result_payload["confidence"],
        dimension_evidence=result_payload["dimension_evidence"],
    )


@router.get("/results/{result_id}/express", response_model=ExpressResultResponse)
async def get_result_express(
    result_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_user),
) -> ExpressResultResponse:
    flags = _flag_snapshot()
    if not flags["results_v2_enabled"] or not flags["results_v2_express_endpoint"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result type endpoint disabled")

    service = AssessmentResultService(AssessmentResultRepository(db))
    result_payload = await service.get_result_payload(
        result_id,
        user_id=str(current_user.id) if current_user else None,
    )
    if not result_payload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")

    if result_payload.get("assessment_slug") == "deep_v1":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Express result path is disabled for deep_v1; use /full",
        )

    try:
        express_payload, fallback_used = service.build_express_payload(result_payload)
    except PayloadAssemblyError as exc:
        _emit_event(
            "payload_generation_fail",
            result_id=result_id,
            result_type="express",
            reason=exc.reason,
        )
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": exc.reason, "message": str(exc)})
    except Exception as exc:
        _emit_event(
            "payload_generation_fail",
            result_id=result_id,
            result_type="express",
            reason="serializer_failure",
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "serializer_failure", "message": str(exc)},
        )

    _emit_event("result_type_served", result_id=result_id, result_type="express")
    _emit_event("payload_generation_success", result_id=result_id, result_type="express")
    if fallback_used:
        _emit_event("express_example_fallback_used", result_id=result_id)
    _emit_event("cta_shown", result_id=result_id, result_type="express")
    return ExpressResultResponse(**express_payload)


@router.post("/results/{result_id}/cta-clicked", status_code=status.HTTP_200_OK)
async def track_cta_clicked(
    result_id: str,
    payload: CtaClickedEventRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_user),
) -> dict[str, Any]:
    # validate ownership via existing result policy
    service = AssessmentResultService(AssessmentResultRepository(db))
    result_payload = await service.get_result_payload(
        result_id,
        user_id=str(current_user.id) if current_user else None,
    )
    if not result_payload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")

    _emit_event(
        "cta_clicked",
        result_id=result_id,
        result_type=payload.result_type,
        target_action=payload.target_action,
        target_url_present=payload.target_url_present,
        surface=payload.surface,
    )
    return {"status": "ok"}


@router.get("/results/{result_id}/full", response_model=FullResultResponse)
async def get_result_full(
    result_id: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_user),
) -> FullResultResponse:
    flags = _flag_snapshot()
    if not flags["results_v2_enabled"] or not flags["results_v2_full_endpoint"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result type endpoint disabled")

    service = AssessmentResultService(AssessmentResultRepository(db))
    result_payload = await service.get_result_payload(
        result_id,
        user_id=str(current_user.id) if current_user else None,
    )
    if not result_payload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")

    try:
        full_payload = service.build_full_payload(result_payload)
    except PayloadAssemblyError as exc:
        _emit_event(
            "payload_generation_fail",
            result_id=result_id,
            result_type="full",
            reason=exc.reason,
        )
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": exc.reason, "message": str(exc)})
    except Exception as exc:
        _emit_event(
            "payload_generation_fail",
            result_id=result_id,
            result_type="full",
            reason="serializer_failure",
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "serializer_failure", "message": str(exc)},
        )

    _emit_event("result_type_served", result_id=result_id, result_type="full")
    _emit_event("payload_generation_success", result_id=result_id, result_type="full")
    return FullResultResponse(**full_payload)
