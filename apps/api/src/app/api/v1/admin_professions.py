from __future__ import annotations

from typing import Optional
import csv
import io
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
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
    ProfessionListPageResponse,
    ProfessionPatchRequest,
)

EXPORT_COLUMNS = [
    "slug",
    "title",
    "cluster",
    "family",
    "status",
    "summary",
    "what_specialist_does",
    "who_it_suits",
    "school_subjects",
    "required_skills",
    "how_to_start",
    "trajectory_notes",
    "content_status",
    "content_level",
    "express_example_eligible",
    "full_rank_eligible",
    "updated_at",
]

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


def _json_cell(value) -> str:
    if isinstance(value, list):
        return json.dumps(_safe_list(value), ensure_ascii=False)
    return json.dumps([], ensure_ascii=False)


def _bool_text(value: bool) -> str:
    return "true" if bool(value) else "false"


def _derive_family(cluster: str) -> str:
    return (cluster or "").strip()


def _derive_content_status(status: str) -> str:
    normalized = (status or "").strip().lower()
    if normalized in {"active", "published", "ready"}:
        return "ready"
    if normalized in {"draft", "archived"}:
        return normalized
    return ""


def _matches_extra_filters(entity, family: Optional[str], content_status: Optional[str]) -> bool:
    if family and _derive_family(entity.cluster) != family:
        return False
    if content_status and _derive_content_status(entity.status) != content_status:
        return False
    return True


@router.get("", response_model=ProfessionListPageResponse)
async def list_professions(
    q: Optional[str] = None,
    search: Optional[str] = None,
    cluster: Optional[str] = None,
    status: Optional[str] = None,
    family: Optional[str] = None,
    content_status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    session: AsyncSession = Depends(get_db_session),
):
    safe_page = max(1, page)
    safe_page_size = max(1, min(page_size, 200))

    repo = AdminProfessionCatalogRepository(session)
    matrix_repo = AdminProfessionMatrixRepository(session)

    if family or content_status:
        all_entities = await repo.list_all(query=q, search=search, cluster=cluster, status=status)
        filtered_entities = [
            entity
            for entity in all_entities
            if _matches_extra_filters(entity, family=family, content_status=content_status)
        ]
        total = len(filtered_entities)
        start = (safe_page - 1) * safe_page_size
        entities = filtered_entities[start : start + safe_page_size]
    else:
        entities, total = await repo.list_paginated(
            page=safe_page,
            page_size=safe_page_size,
            query=q,
            search=search,
            cluster=cluster,
            status=status,
        )

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

    total_pages = max(1, (total + safe_page_size - 1) // safe_page_size)
    return ProfessionListPageResponse(
        items=rows,
        total=total,
        page=safe_page,
        page_size=safe_page_size,
        total_pages=total_pages,
    )


@router.get("/export")
async def export_professions_csv(
    q: Optional[str] = None,
    search: Optional[str] = None,
    cluster: Optional[str] = None,
    family: Optional[str] = None,
    status: Optional[str] = None,
    content_status: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session),
):
    repo = AdminProfessionCatalogRepository(session)
    matrix_repo = AdminProfessionMatrixRepository(session)
    entities = await repo.list_all(query=q, search=search, cluster=cluster, status=status)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=EXPORT_COLUMNS)
    writer.writeheader()

    for entity in entities:
        if not _matches_extra_filters(entity, family=family, content_status=content_status):
            continue

        pair = await matrix_repo.get_with_profession("matrix_v1", entity.slug)
        matrix = pair[0] if pair else None
        family_value = _derive_family(entity.cluster)
        content_status_value = _derive_content_status(entity.status)

        row = {
            "slug": entity.slug,
            "title": entity.title,
            "cluster": entity.cluster,
            "family": family_value,
            "status": entity.status,
            "summary": entity.summary,
            "what_specialist_does": entity.summary,
            "who_it_suits": _json_cell([]),
            "school_subjects": _json_cell(matrix.important_subjects if matrix else []),
            "required_skills": _json_cell([]),
            "how_to_start": _json_cell(matrix.first_steps_template if matrix else []),
            "trajectory_notes": _json_cell([]),
            "content_status": content_status_value,
            "content_level": "",
            "express_example_eligible": _bool_text(True),
            "full_rank_eligible": _bool_text(True),
            "updated_at": entity.updated_at.isoformat() if entity.updated_at else "",
        }
        writer.writerow(row)

    csv_bytes = output.getvalue().encode("utf-8")
    output.close()

    return StreamingResponse(
        iter([csv_bytes]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="professions_export.csv"'},
    )


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
