from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session, require_admin_user
from app.models.user import User
from app.repositories.admin_assessment_repository import AdminAssessmentRepository
from app.repositories.admin_question_repository import AdminQuestionRepository
from app.schemas.admin_assessment import (
    AssessmentDetailResponse,
    AssessmentListItemResponse,
    AssessmentPatchRequest,
    CloneAssessmentRequest,
    CloneAssessmentResponse,
)

router = APIRouter(prefix="/assessments", dependencies=[Depends(require_admin_user)])


def _requires_clone_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"code": "requires_clone", "message": "Active assessment requires clone before editing"},
    )


def _serialize_list_item(entity) -> AssessmentListItemResponse:
    return AssessmentListItemResponse(
        id=str(entity.id),
        slug=entity.slug,
        title=entity.title,
        description=entity.description,
        target_items_count=entity.target_items_count,
        min_items_count=entity.min_items_count,
        max_items_count=entity.max_items_count,
        expected_duration_min=entity.expected_duration_min,
        is_active=entity.is_active,
        version=entity.version,
    )


def _serialize_detail(entity) -> AssessmentDetailResponse:
    return AssessmentDetailResponse(
        **_serialize_list_item(entity).model_dump(),
        scoring_config_json=dict(entity.scoring_config_json or {}),
        question_mix_config_json=dict(entity.question_mix_config_json or {}),
    )


def _build_clone_slug(slug: str) -> str:
    stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{slug}_draft_{stamp}"


@router.get("", response_model=list[AssessmentListItemResponse])
async def list_assessments(session: AsyncSession = Depends(get_db_session)) -> list[AssessmentListItemResponse]:
    repo = AdminAssessmentRepository(session)
    items = await repo.list_all()
    return [_serialize_list_item(item) for item in items]


@router.get("/{slug}", response_model=AssessmentDetailResponse)
async def get_assessment(slug: str, session: AsyncSession = Depends(get_db_session)) -> AssessmentDetailResponse:
    repo = AdminAssessmentRepository(session)
    entity = await repo.get_by_slug(slug)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return _serialize_detail(entity)


@router.patch("/{slug}", response_model=AssessmentDetailResponse)
async def patch_assessment(
    slug: str,
    payload: AssessmentPatchRequest,
    session: AsyncSession = Depends(get_db_session),
) -> AssessmentDetailResponse:
    repo = AdminAssessmentRepository(session)
    entity = await repo.get_by_slug(slug)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    patch = payload.model_dump(exclude_unset=True)
    protected_fields = {
        "target_items_count",
        "min_items_count",
        "max_items_count",
        "expected_duration_min",
        "is_active",
        "scoring_config_json",
        "question_mix_config_json",
    }
    if entity.is_active and any(field in patch for field in protected_fields):
        raise _requires_clone_error()

    for key, value in patch.items():
        setattr(entity, key, value)

    await session.commit()
    await session.refresh(entity)
    return _serialize_detail(entity)


@router.post("/{slug}/clone", response_model=CloneAssessmentResponse)
async def clone_assessment(
    slug: str,
    payload: CloneAssessmentRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_admin_user),
) -> CloneAssessmentResponse:
    repo = AdminAssessmentRepository(session)
    question_repo = AdminQuestionRepository(session)

    source = await repo.get_by_slug(slug)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    new_slug = payload.new_slug or _build_clone_slug(source.slug)
    existing = await repo.get_by_slug(new_slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "slug_conflict", "message": "Draft slug already exists"},
        )

    clone = await repo.create_clone(source, new_slug)

    source_questions = await question_repo.list_questions(assessment_slug=source.slug)
    for question in source_questions:
        await question_repo.create_clone(question, target_assessment_slug=clone.slug)

    await session.commit()
    return CloneAssessmentResponse(source_slug=slug, draft_slug=clone.slug)
