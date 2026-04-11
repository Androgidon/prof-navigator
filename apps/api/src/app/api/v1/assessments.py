from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_optional_user
from app.db.session import get_db_session
from app.domains.assessment_catalog.repository import AssessmentCatalogRepository
from app.domains.assessment_results.repository import AssessmentResultRepository
from app.domains.assessment_results.result_policy import (
    diversification_fill_strategy,
    recommendation_target_count,
)
from app.domains.assessment_results.service import AssessmentResultService
from app.domains.assessment_scoring.consistency_service import ConsistencyService
from app.domains.assessment_scoring.profession_match_service import ProfessionMatchService
from app.domains.assessment_scoring.profile_scoring_service import ProfileScoringService
from app.domains.assessment_sessions.repository import AssessmentSessionRepository
from app.domains.assessment_sessions.service import AssessmentSessionService
from app.domains.profession_catalog.repository import ProfessionCatalogRepository
from app.domains.profession_matrix.repository import ProfessionMatrixRepository
from app.domains.question_bank.repository import QuestionBankRepository
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
from app.schemas.test_session import StartAssessmentRequest
from app.models.user import User

router = APIRouter()


@router.post("/start", response_model=StartAssessmentV2Response)
async def start(
    payload: StartAssessmentRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_user),
) -> StartAssessmentV2Response:
    assessment_slug = payload.assessment_slug or "express_v1"
    session_service = AssessmentSessionService(
        catalog_repository=AssessmentCatalogRepository(db),
        question_repository=QuestionBankRepository(db),
        session_repository=AssessmentSessionRepository(db),
    )
    bound_user_id = str(current_user.id) if current_user else None
    session, catalog = await session_service.start(assessment_slug=assessment_slug, user_id=bound_user_id)
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

    scoring = ProfileScoringService().compute(
        questions=questions,
        answers_json=dict(session.answers_json or {}),
        scoring_config_json=dict(catalog.scoring_config_json or {}),
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
    )

    consistency_output = ConsistencyService().compute(
        answers_json=dict(session.answers_json or {}),
        dimension_evidence=scoring["dimension_evidence"],
        total_questions=len(session.question_set_json or []),
        fallback_dimensions=scoring["fallback_dimensions"],
        recommendations=recommendations,
        profile_scores=scoring["profile_scores"],
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
