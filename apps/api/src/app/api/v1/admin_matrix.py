from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session, require_admin_user
from app.repositories.admin_profession_matrix_repository import AdminProfessionMatrixRepository
from app.schemas.admin_matrix import (
    MatrixCloneResponse,
    MatrixDetailResponse,
    MatrixListItemResponse,
    MatrixPatchRequest,
    MatrixPreviewRequest,
    MatrixPreviewResponse,
    MatrixValidationRequest,
    MatrixValidationResponse,
)
from app.services.admin_matrix_preview_service import AdminMatrixPreviewService
from app.services.admin_matrix_validation_service import AdminMatrixValidationService

router = APIRouter(prefix="/matrix", dependencies=[Depends(require_admin_user)])


def _build_draft_version_slug(version_slug: str) -> str:
    stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{version_slug}_draft_{stamp}"


def _completeness(why_fit_template: str, critical_dimensions: list[str], targets: dict, weights: dict) -> int:
    score = 0
    if why_fit_template.strip():
        score += 25
    if critical_dimensions:
        score += 25
    if len(targets.keys()) == 12:
        score += 25
    if len(weights.keys()) == 12:
        score += 25
    return score


@router.get("", response_model=list[MatrixListItemResponse])
async def list_matrix(
    version_slug: Optional[str] = None,
    profession_q: Optional[str] = None,
    cluster: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session),
):
    repo = AdminProfessionMatrixRepository(session)
    rows = await repo.list_with_professions(version_slug=version_slug, profession_query=profession_q, cluster=cluster)

    result = []
    for matrix, profession in rows:
        score = _completeness(
            matrix.why_fit_template,
            list(matrix.critical_dimensions or []),
            dict(matrix.target_profile_json or {}),
            dict(matrix.dimension_weights_json or {}),
        )
        status = "valid" if score == 100 else ("needs_attention" if score >= 50 else "incomplete")
        result.append(
            MatrixListItemResponse(
                profession_slug=profession.slug,
                profession_title=profession.title,
                cluster=profession.cluster,
                version_slug=matrix.version_slug,
                completeness_score=score,
                validation_status=status,
            )
        )
    return result


@router.get("/{version_slug}/{profession_slug}", response_model=MatrixDetailResponse)
async def get_matrix(version_slug: str, profession_slug: str, session: AsyncSession = Depends(get_db_session)):
    repo = AdminProfessionMatrixRepository(session)
    row = await repo.get_with_profession(version_slug, profession_slug)
    if not row:
        raise HTTPException(status_code=404, detail="Matrix not found")
    matrix, profession = row
    return MatrixDetailResponse(
        profession_slug=profession.slug,
        profession_title=profession.title,
        cluster=profession.cluster,
        version_slug=matrix.version_slug,
        matrix_version=matrix.matrix_version,
        target_profile_json=dict(matrix.target_profile_json or {}),
        dimension_weights_json=dict(matrix.dimension_weights_json or {}),
        critical_dimensions=list(matrix.critical_dimensions or []),
        important_subjects=list(matrix.important_subjects or []),
        hobby_signals=list(matrix.hobby_signals or []),
        preferred_environments=list(matrix.preferred_environments or []),
        why_fit_template=matrix.why_fit_template,
        first_steps_template=list(matrix.first_steps_template or []),
        notes=matrix.notes,
    )


@router.patch("/{version_slug}/{profession_slug}", response_model=MatrixDetailResponse)
async def patch_matrix(
    version_slug: str,
    profession_slug: str,
    payload: MatrixPatchRequest,
    session: AsyncSession = Depends(get_db_session),
):
    repo = AdminProfessionMatrixRepository(session)
    row = await repo.get_with_profession(version_slug, profession_slug)
    if not row:
        raise HTTPException(status_code=404, detail="Matrix not found")
    matrix, profession = row

    if not version_slug.endswith("_draft") and "_draft_" not in version_slug:
        raise HTTPException(status_code=409, detail={"code": "requires_clone", "message": "Active matrix version requires clone before editing"})

    patch = payload.model_dump(exclude_unset=True)

    validation_input = MatrixValidationRequest(
        target_profile_json=patch.get("target_profile_json", matrix.target_profile_json),
        dimension_weights_json=patch.get("dimension_weights_json", matrix.dimension_weights_json),
        critical_dimensions=patch.get("critical_dimensions", matrix.critical_dimensions),
        why_fit_template=patch.get("why_fit_template", matrix.why_fit_template),
    )
    validation = AdminMatrixValidationService().validate(
        target_profile_json=validation_input.target_profile_json,
        dimension_weights_json=validation_input.dimension_weights_json,
        critical_dimensions=validation_input.critical_dimensions,
        why_fit_template=validation_input.why_fit_template,
    )
    if not validation.valid:
        raise HTTPException(status_code=422, detail={"code": "validation_error", "message": "Matrix validation failed", "hard_errors": [issue.model_dump() for issue in validation.hard_errors], "warnings": [issue.model_dump() for issue in validation.warnings]})

    for key, value in patch.items():
        setattr(matrix, key, value)

    await session.commit()
    await session.refresh(matrix)

    return MatrixDetailResponse(
        profession_slug=profession.slug,
        profession_title=profession.title,
        cluster=profession.cluster,
        version_slug=matrix.version_slug,
        matrix_version=matrix.matrix_version,
        target_profile_json=dict(matrix.target_profile_json or {}),
        dimension_weights_json=dict(matrix.dimension_weights_json or {}),
        critical_dimensions=list(matrix.critical_dimensions or []),
        important_subjects=list(matrix.important_subjects or []),
        hobby_signals=list(matrix.hobby_signals or []),
        preferred_environments=list(matrix.preferred_environments or []),
        why_fit_template=matrix.why_fit_template,
        first_steps_template=list(matrix.first_steps_template or []),
        notes=matrix.notes,
    )


@router.post("/{version_slug}/{profession_slug}/clone", response_model=MatrixCloneResponse)
async def clone_matrix(version_slug: str, profession_slug: str, session: AsyncSession = Depends(get_db_session)):
    repo = AdminProfessionMatrixRepository(session)
    row = await repo.get_with_profession(version_slug, profession_slug)
    if not row:
        raise HTTPException(status_code=404, detail="Matrix not found")
    source, profession = row

    draft_version_slug = _build_draft_version_slug(version_slug)
    existing = await repo.get_by_profession_and_version(source.profession_id, draft_version_slug)
    if existing:
        raise HTTPException(status_code=409, detail={"code": "conflict_existing_matrix", "message": "Draft matrix already exists"})

    await repo.create_clone(source, draft_version_slug)
    await session.commit()

    return MatrixCloneResponse(
        source_version_slug=version_slug,
        draft_version_slug=draft_version_slug,
        profession_slug=profession.slug,
    )


@router.post("/preview", response_model=MatrixPreviewResponse)
async def preview_matrix(payload: MatrixPreviewRequest) -> MatrixPreviewResponse:
    return AdminMatrixPreviewService().preview(
        profile_scores=payload.profile_scores,
        target_profile_json=payload.target_profile_json,
        dimension_weights_json=payload.dimension_weights_json,
        critical_dimensions=payload.critical_dimensions,
        cluster=payload.cluster,
    )


@router.post("/validate", response_model=MatrixValidationResponse)
async def validate_matrix(payload: MatrixValidationRequest) -> MatrixValidationResponse:
    return AdminMatrixValidationService().validate(
        target_profile_json=payload.target_profile_json,
        dimension_weights_json=payload.dimension_weights_json,
        critical_dimensions=payload.critical_dimensions,
        why_fit_template=payload.why_fit_template,
    )
