import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import async_session
from app.models.interest import Interest
from app.models.profession_industry import ProfessionIndustry
from app.models.profession import Profession
from app.models.subject import Subject


async def seed() -> None:
    async with async_session() as session:
        await _ensure_subjects(session)
        await _ensure_interests(session)
        industry = await _get_or_create_industry(session)
        await _ensure_profession(session, industry)
        await session.commit()


async def _ensure_subjects(session: AsyncSession) -> None:
    payload = [
        {"name": "Математика", "slug": "math"},
        {"name": "Физика", "slug": "physics"},
        {"name": "Биология", "slug": "biology"},
    ]
    for entry in payload:
        existing = await session.scalar(select(Subject).filter_by(slug=entry["slug"]))
        if existing:
            continue
        session.add(Subject(**entry))


async def _ensure_interests(session: AsyncSession) -> None:
    payload = [
        {"name": "IT", "slug": "it"},
        {"name": "Науки", "slug": "science"},
        {"name": "Арт", "slug": "art"},
    ]
    for entry in payload:
        existing = await session.scalar(select(Interest).filter_by(slug=entry["slug"]))
        if existing:
            continue
        session.add(Interest(**entry))


async def _get_or_create_industry(session: AsyncSession) -> ProfessionIndustry:
    existing = await session.scalar(
        select(ProfessionIndustry).filter_by(name_ru="IT")
    )
    if existing:
        return existing
    industry = ProfessionIndustry(
        name_ru="IT",
        name_uz="IT",
        icon="code",
        color="#7C3AED",
    )
    session.add(industry)
    return industry


async def _ensure_profession(session: AsyncSession, industry: ProfessionIndustry) -> None:
    existing = await session.scalar(select(Profession).filter_by(slug="data-analyst"))
    if existing:
        return
    profession = Profession(
        slug="data-analyst",
        title_ru="Data analyst",
        title_uz="Data analyst",
        description="Работа с данными",
        profession_vector={"analytical": 0.9, "creative": 0.4},
        start_now_steps=["Изучить Python", "Построить портфолио"],
        important_subjects=["math", "informatics"],
        industry=industry,
    )
    session.add(profession)


def main() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    main()
