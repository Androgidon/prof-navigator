import logging
from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.dependencies import get_session
from app.core.settings import get_settings
from app.repositories.profession_repository import ProfessionRepository
from app.schemas.profession import ProfessionListItemResponse, ProfessionResponse, RelatedProfessionResponse

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


def _safe_list(raw) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [str(item).strip() for item in raw if str(item).strip()]


def _fallback_what_specialist_does(summary: str) -> str:
    if summary.strip():
        return summary.strip()
    return "Описание задач специалиста пока дополняется."


def _fallback_who_suits(cluster: str) -> list[str]:
    if not cluster.strip():
        return ["Тем, кто хочет развиваться в этой сфере и пробовать практические задачи."]
    return [f"Тем, кому интересна сфера «{cluster}» и прикладные задачи в этом направлении."]


@router.get("", response_model=list[ProfessionListItemResponse])
@router.get("/", response_model=list[ProfessionListItemResponse], include_in_schema=False)
async def list_professions(session=Depends(get_session)) -> Union[list[ProfessionListItemResponse], JSONResponse]:
    repo = ProfessionRepository(session)
    try:
        logger.info("GET /professions endpoint entered")

        if settings.professions_diag_ping:
            logger.warning("PROFESSIONS_DIAG_PING enabled, returning diagnostic response")
            return []

        logger.info("GET /professions before repo.list_active")
        professions = await repo.list_active()
        logger.info("GET /professions after repo.list_active")
        logger.info("GET /professions result length", extra={"records_count": len(professions)})

        response_items: list[ProfessionListItemResponse] = []
        logger.info("GET /professions serialization loop start")
        for profession in professions:
            try:
                response_items.append(
                    ProfessionListItemResponse(
                        slug=(profession.slug or "").strip(),
                        title=(profession.title or "").strip(),
                        cluster=(profession.cluster or "").strip(),
                        summary=(profession.summary or "").strip(),
                        status=(profession.status or "").strip() or "active",
                    )
                )
            except Exception:
                logger.exception(
                    "Skipping invalid profession row during response serialization",
                    extra={
                        "profession_id": str(getattr(profession, "id", "")),
                        "profession_slug": str(getattr(profession, "slug", "")),
                    },
                )

        logger.info("GET /professions serialization loop end")
        logger.info("GET /professions completed", extra={"response_count": len(response_items)})
        return response_items
    except Exception as exc:
        logger.exception("GET /professions failed")
        return JSONResponse(status_code=500, content={"detail": str(exc), "error_type": exc.__class__.__name__})


@router.get("/pure-ping")
async def pure_ping() -> dict[str, bool]:
    logger.info("GET /professions/pure-ping entered")
    return {"ok": True}


@router.get("/dep-ping")
async def dep_ping(session=Depends(get_session)) -> dict[str, bool]:
    logger.info("GET /professions/dep-ping entered", extra={"session_type": type(session).__name__})
    return {"ok": True}


@router.get("/ping-db")
async def ping_db(session=Depends(get_session)) -> dict[str, str]:
    logger.info("GET /professions/ping-db entered")
    result = await session.execute(text("SELECT 1"))
    value = result.scalar_one()
    logger.info("GET /professions/ping-db completed", extra={"result": value})
    return {"status": "ok"}


@router.get("/{slug}", response_model=ProfessionResponse)
async def get_profession(slug: str, session=Depends(get_session)) -> ProfessionResponse:
    repo = ProfessionRepository(session)
    profession = await repo.get_active_by_slug(slug)
    if profession is None:
        raise HTTPException(status_code=404, detail="Профессия не найдена")

    matrix = await repo.get_matrix(profession.id)
    important_subjects = _safe_list(matrix.important_subjects if matrix else [])
    how_to_start = _safe_list(matrix.first_steps_template if matrix else [])
    related = await repo.list_related_by_cluster(profession.cluster, profession.slug)

    return ProfessionResponse(
        slug=profession.slug,
        title=profession.title,
        cluster=profession.cluster,
        summary=profession.summary,
        status=profession.status,
        what_specialist_does=_fallback_what_specialist_does(profession.summary),
        who_suits=_fallback_who_suits(profession.cluster),
        important_subjects=important_subjects,
        required_skills=[],
        how_to_start=how_to_start,
        related_professions=[
            RelatedProfessionResponse(slug=item.slug, title=item.title, cluster=item.cluster)
            for item in related
        ],
    )
