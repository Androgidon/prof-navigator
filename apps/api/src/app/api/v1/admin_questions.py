from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session, require_admin_user
from app.repositories.admin_assessment_repository import AdminAssessmentRepository
from app.repositories.admin_question_repository import AdminQuestionRepository
from app.schemas.admin_question import (
    CloneQuestionRequest,
    PreviewSignalRequest,
    PreviewSignalResponse,
    QuestionCreateRequest,
    QuestionDetailResponse,
    QuestionListItemResponse,
    QuestionPatchRequest,
    QuestionReorderRequest,
    QuestionReorderResponse,
)
from app.services.admin_question_preview_service import AdminQuestionPreviewService

router = APIRouter(prefix="/questions", dependencies=[Depends(require_admin_user)])


def _serialize_list_item(entity) -> QuestionListItemResponse:
    return QuestionListItemResponse(
        id=str(entity.id),
        assessment_version_slug=entity.assessment_version_slug,
        question_id=entity.question_id,
        block=entity.block,
        subblock=entity.subblock,
        question_type=entity.question_type,
        text=entity.text,
        primary_dimension=entity.primary_dimension,
        secondary_dimensions=list(entity.secondary_dimensions or []),
        order_hint=entity.order_hint,
        status=entity.status,
    )


def _serialize_detail(entity) -> QuestionDetailResponse:
    return QuestionDetailResponse(
        **_serialize_list_item(entity).model_dump(),
        options_json=list(entity.options_json or []),
        weights_by_dimension_json=dict(entity.weights_by_dimension_json or {}),
        consistency_pair_id=entity.consistency_pair_id,
        difficulty=entity.difficulty,
        is_required=entity.is_required,
        question_purpose=entity.question_purpose,
        notes=entity.notes,
    )


def _raise_requires_clone() -> None:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"code": "requires_clone", "message": "Active assessment requires clone before editing questions"},
    )


def _validate_question_payload(question_type: str, options_json, weights_by_dimension_json):
    required_options_types = {"forced_choice", "situational", "single_select", "multi_select", "multi_select_or_ranking"}
    if question_type in required_options_types and (not options_json or len(options_json) == 0):
        raise HTTPException(status_code=422, detail={"code": "validation_error", "message": "options_json is required for question type"})
    if not isinstance(weights_by_dimension_json, dict):
        raise HTTPException(status_code=422, detail={"code": "validation_error", "message": "weights_by_dimension_json must be object"})


@router.get("", response_model=list[QuestionListItemResponse])
async def list_questions(
    assessment_slug: Optional[str] = None,
    block: Optional[str] = None,
    question_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    q: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session),
) -> list[QuestionListItemResponse]:
    repo = AdminQuestionRepository(session)
    items = await repo.list_questions(
        assessment_slug=assessment_slug,
        block=block,
        question_type=question_type,
        status=status_filter,
        query=q,
    )
    return [_serialize_list_item(item) for item in items]


@router.get("/{assessment_slug}/{question_id}", response_model=QuestionDetailResponse)
async def get_question(
    assessment_slug: str,
    question_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionDetailResponse:
    repo = AdminQuestionRepository(session)
    entity = await repo.get(assessment_slug=assessment_slug, question_id=question_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Question not found")
    return _serialize_detail(entity)


@router.post("", response_model=QuestionDetailResponse, status_code=201)
async def create_question(payload: QuestionCreateRequest, session: AsyncSession = Depends(get_db_session)) -> QuestionDetailResponse:
    assessment_repo = AdminAssessmentRepository(session)
    question_repo = AdminQuestionRepository(session)

    assessment = await assessment_repo.get_by_slug(payload.assessment_version_slug)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    if assessment.is_active:
        _raise_requires_clone()

    options_json = payload.options_json or []
    _validate_question_payload(payload.question_type, options_json, payload.weights_by_dimension_json)

    order_hint = payload.order_hint
    if order_hint is None:
        max_order = await question_repo.get_max_order_hint(payload.assessment_version_slug, payload.block)
        order_hint = max_order + 1

    entity_payload = {
        "question_id": payload.question_id,
        "assessment_version_slug": payload.assessment_version_slug,
        "block": payload.block,
        "subblock": payload.subblock,
        "question_type": payload.question_type,
        "text": payload.text,
        "options_json": options_json,
        "primary_dimension": payload.primary_dimension,
        "secondary_dimensions": payload.secondary_dimensions,
        "weights_by_dimension_json": payload.weights_by_dimension_json,
        "consistency_pair_id": payload.consistency_pair_id,
        "difficulty": payload.difficulty,
        "is_required": payload.is_required,
        "order_hint": order_hint,
        "status": payload.status,
        "question_purpose": payload.question_purpose,
        "notes": payload.notes,
    }

    try:
        entity = await question_repo.create(entity_payload)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail={"code": "conflict_existing_question", "message": "Question already exists for assessment slug"})

    return _serialize_detail(entity)


@router.patch("/{assessment_slug}/{question_id}", response_model=QuestionDetailResponse)
async def patch_question(
    assessment_slug: str,
    question_id: str,
    payload: QuestionPatchRequest,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionDetailResponse:
    assessment_repo = AdminAssessmentRepository(session)
    question_repo = AdminQuestionRepository(session)

    assessment = await assessment_repo.get_by_slug(assessment_slug)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    if assessment.is_active:
        _raise_requires_clone()

    entity = await question_repo.get(assessment_slug, question_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Question not found")

    patch = payload.model_dump(exclude_unset=True)
    merged_question_type = patch.get("question_type", entity.question_type)
    merged_options = patch.get("options_json", entity.options_json)
    merged_weights = patch.get("weights_by_dimension_json", entity.weights_by_dimension_json)
    _validate_question_payload(merged_question_type, merged_options, merged_weights)

    for key, value in patch.items():
        setattr(entity, key, value)

    await session.commit()
    await session.refresh(entity)
    return _serialize_detail(entity)


@router.post("/{assessment_slug}/{question_id}/clone", response_model=QuestionDetailResponse)
async def clone_question(
    assessment_slug: str,
    question_id: str,
    payload: CloneQuestionRequest,
    session: AsyncSession = Depends(get_db_session),
) -> QuestionDetailResponse:
    assessment_repo = AdminAssessmentRepository(session)
    question_repo = AdminQuestionRepository(session)

    source = await question_repo.get(assessment_slug, question_id)
    if not source:
        raise HTTPException(status_code=404, detail="Question not found")

    target_assessment = await assessment_repo.get_by_slug(payload.target_assessment_version_slug)
    if not target_assessment:
        raise HTTPException(status_code=404, detail="Target assessment not found")
    if target_assessment.is_active:
        _raise_requires_clone()

    existing = await question_repo.get(payload.target_assessment_version_slug, question_id)
    if existing:
        raise HTTPException(status_code=409, detail={"code": "conflict_existing_question", "message": "Question already exists in target assessment"})

    clone = await question_repo.create_clone(source, payload.target_assessment_version_slug)
    await session.commit()
    return _serialize_detail(clone)


@router.put("/reorder", response_model=QuestionReorderResponse)
async def reorder_questions(payload: QuestionReorderRequest, session: AsyncSession = Depends(get_db_session)) -> QuestionReorderResponse:
    assessment_repo = AdminAssessmentRepository(session)
    question_repo = AdminQuestionRepository(session)

    assessment = await assessment_repo.get_by_slug(payload.assessment_version_slug)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    if assessment.is_active:
        _raise_requires_clone()

    questions = await question_repo.list_by_assessment_block(payload.assessment_version_slug, payload.block)
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for assessment/block")

    by_id = {q.question_id: q for q in questions}

    if payload.items:
        seen = set()
        for item in payload.items:
            if item.question_id in seen:
                raise HTTPException(status_code=422, detail={"code": "validation_error", "message": "Duplicate question id in reorder payload"})
            seen.add(item.question_id)
            if item.question_id not in by_id:
                raise HTTPException(status_code=422, detail={"code": "validation_error", "message": "Unknown question id in reorder payload"})
            by_id[item.question_id].order_hint = item.order_hint
    else:
        ordered_ids = payload.ordered_question_ids or []
        if len(set(ordered_ids)) != len(ordered_ids):
            raise HTTPException(status_code=422, detail={"code": "validation_error", "message": "Duplicate question id in ordered list"})
        expected_ids = set(by_id.keys())
        provided_ids = set(ordered_ids)
        if expected_ids != provided_ids:
            raise HTTPException(status_code=422, detail={"code": "validation_error", "message": "ordered_question_ids must include all and only current block questions"})
        for idx, qid in enumerate(ordered_ids, start=1):
            by_id[qid].order_hint = idx

    await session.commit()
    return QuestionReorderResponse(
        assessment_version_slug=payload.assessment_version_slug,
        block=payload.block,
        updated=len(by_id),
    )


@router.post("/preview-signal", response_model=PreviewSignalResponse)
async def preview_signal(payload: PreviewSignalRequest) -> PreviewSignalResponse:
    service = AdminQuestionPreviewService()
    signals = service.build_signals(
        question_type=payload.question_type,
        options_json=payload.options_json,
        weights_by_dimension_json=payload.weights_by_dimension_json,
        answer=payload.answer,
    )
    notes = []
    if not signals:
        notes.append("No dimension signals extracted from provided sample answer")
    return PreviewSignalResponse(signals=signals, notes=notes)
