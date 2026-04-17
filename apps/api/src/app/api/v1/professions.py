import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_session
from app.repositories.profession_repository import ProfessionRepository
from app.schemas.profession import ProfessionListItemResponse, ProfessionResponse, RelatedProfessionResponse

router = APIRouter()
logger = logging.getLogger(__name__)


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
async def list_professions(session=Depends(get_session)) -> list[ProfessionListItemResponse]:
    repo = ProfessionRepository(session)
    try:
        logger.info("GET /professions started")
        professions = await repo.list_active()
        logger.info("GET /professions fetched records", extra={"records_count": len(professions)})

        response_items: list[ProfessionListItemResponse] = []
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

        logger.info("GET /professions completed", extra={"response_count": len(response_items)})
        return response_items
    except Exception:
        logger.exception("Failed to load professions")
        raise


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
