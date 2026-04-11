from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session, require_admin_user
from app.models.profession_matrix import ProfessionMatrix
from app.repositories.admin_profession_catalog_repository import AdminProfessionCatalogRepository
from app.repositories.admin_profession_matrix_repository import AdminProfessionMatrixRepository
from app.schemas.admin_profession import (
    ProfessionCreateRequest,
    ProfessionDetailResponse,
    ProfessionListItemResponse,
    ProfessionPatchRequest,
)

router = APIRouter(prefix="/professions", dependencies=[Depends(require_admin_user)])


def _safe_list(raw):
    if not isinstance(raw, list):
        return []
    return [str(item).strip() for item in raw if str(item).strip()]


def _completeness(summary: str, first_steps: list[str], subjects: list[str]) -> int:
    score = 0
    if summary.strip():
        score += 40
    if first_steps:
        score += 30
    if subjects:
        score += 30
    return score


@router.get("", response_model=list[ProfessionListItemResponse])
async def list_professions(
    q: Optional[str] = None,
    cluster: Optional[str] = None,
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session),
):
    repo = AdminProfessionCatalogRepository(session)
    matrix_repo = AdminProfessionMatrixRepository(session)
    entities = await repo.list_all(query=q, cluster=cluster, status=status)

    rows: list[ProfessionListItemResponse] = []
    for entity in entities:
        pair = await matrix_repo.get_with_profession("matrix_v1", entity.slug)
        first_steps = _safe_list(pair[0].first_steps_template if pair else [])
        subjects = _safe_list(pair[0].important_subjects if pair else [])
        rows.append(
            ProfessionListItemResponse(
                id=str(entity.id),
                external_id=entity.external_id,
                slug=entity.slug,
                title=entity.title,
                cluster=entity.cluster,
                summary=entity.summary,
                status=entity.status,
                first_steps_short=first_steps,
                important_subjects_short=subjects,
                completeness_score=_completeness(entity.summary, first_steps, subjects),
            )
        )
    return rows


@router.get("/{slug}", response_model=ProfessionDetailResponse)
async def get_profession(slug: str, session: AsyncSession = Depends(get_db_session)):
    repo = AdminProfessionCatalogRepository(session)
    matrix_repo = AdminProfessionMatrixRepository(session)
    entity = await repo.get_by_slug(slug)
    if not entity:
        raise HTTPException(status_code=404, detail="Profession not found")

    pair = await matrix_repo.get_with_profession("matrix_v1", entity.slug)
    matrix = pair[0] if pair else None
    first_steps = _safe_list(matrix.first_steps_template if matrix else [])
    subjects = _safe_list(matrix.important_subjects if matrix else [])

    return ProfessionDetailResponse(
        id=str(entity.id),
        external_id=entity.external_id,
        slug=entity.slug,
        title=entity.title,
        cluster=entity.cluster,
        summary=entity.summary,
        status=entity.status,
        first_steps_short=first_steps,
        important_subjects_short=subjects,
        matrix_version_slug=matrix.version_slug if matrix else "matrix_v1",
        completeness_score=_completeness(entity.summary, first_steps, subjects),
    )


@router.post("", response_model=ProfessionDetailResponse, status_code=201)
async def create_profession(payload: ProfessionCreateRequest, session: AsyncSession = Depends(get_db_session)):
    repo = AdminProfessionCatalogRepository(session)
    matrix_repo = AdminProfessionMatrixRepository(session)

    entity_payload = {
        "external_id": payload.external_id,
        "slug": payload.slug,
        "title": payload.title,
        "cluster": payload.cluster,
        "summary": payload.summary,
        "status": payload.status,
    }

    try:
        created = await repo.create(entity_payload)
        matrix = ProfessionMatrix(
            profession_id=created.id,
            version_slug=payload.matrix_version_slug,
            target_profile_json={dim: 50 for dim in ["analytical", "technical", "creative", "social", "helping", "leadership", "structured", "exploratory", "detail", "verbal", "quantitative", "practical"]},
            dimension_weights_json={dim: 1.0 for dim in ["analytical", "technical", "creative", "social", "helping", "leadership", "structured", "exploratory", "detail", "verbal", "quantitative", "practical"]},
            critical_dimensions=[],
            important_subjects=_safe_list(payload.important_subjects_short),
            hobby_signals=[],
            preferred_environments=[],
            why_fit_template="Заполните объяснение соответствия.",
            first_steps_template=_safe_list(payload.first_steps_short),
            notes=None,
            matrix_version=1,
        )
        session.add(matrix)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail={"code": "profession_conflict", "message": "Slug or external_id already exists"})

    first_steps = _safe_list(payload.first_steps_short)
    subjects = _safe_list(payload.important_subjects_short)

    return ProfessionDetailResponse(
        id=str(created.id),
        external_id=created.external_id,
        slug=created.slug,
        title=created.title,
        cluster=created.cluster,
        summary=created.summary,
        status=created.status,
        first_steps_short=first_steps,
        important_subjects_short=subjects,
        matrix_version_slug=payload.matrix_version_slug,
        completeness_score=_completeness(created.summary, first_steps, subjects),
    )


@router.patch("/{slug}", response_model=ProfessionDetailResponse)
async def patch_profession(
    slug: str,
    payload: ProfessionPatchRequest,
    session: AsyncSession = Depends(get_db_session),
):
    repo = AdminProfessionCatalogRepository(session)
    matrix_repo = AdminProfessionMatrixRepository(session)

    entity = await repo.get_by_slug(slug)
    if not entity:
        raise HTTPException(status_code=404, detail="Profession not found")

    patch = payload.model_dump(exclude_unset=True)

    list_keys = {"first_steps_short", "important_subjects_short"}
    for key in list_keys:
        if key in patch and (not isinstance(patch[key], list) or any(not isinstance(x, str) for x in patch[key])):
            raise HTTPException(status_code=422, detail={"code": "validation_error", "message": f"{key} must be a list of strings"})

    for key in ["title", "cluster", "summary", "status"]:
        if key in patch:
            setattr(entity, key, patch[key])

    version_slug = patch.get("matrix_version_slug", "matrix_v1")
    matrix_pair = await matrix_repo.get_with_profession(version_slug, entity.slug)
    matrix = matrix_pair[0] if matrix_pair else None
    if matrix:
        if "first_steps_short" in patch:
            matrix.first_steps_template = _safe_list(patch["first_steps_short"])
        if "important_subjects_short" in patch:
            matrix.important_subjects = _safe_list(patch["important_subjects_short"])

    await session.commit()

    first_steps = _safe_list(matrix.first_steps_template if matrix else [])
    subjects = _safe_list(matrix.important_subjects if matrix else [])

    return ProfessionDetailResponse(
        id=str(entity.id),
        external_id=entity.external_id,
        slug=entity.slug,
        title=entity.title,
        cluster=entity.cluster,
        summary=entity.summary,
        status=entity.status,
        first_steps_short=first_steps,
        important_subjects_short=subjects,
        matrix_version_slug=version_slug,
        completeness_score=_completeness(entity.summary, first_steps, subjects),
    )
