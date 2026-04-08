import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import async_session
from app.models.interest import Interest
from app.models.profession_industry import ProfessionIndustry
from app.models.profession import Profession
from app.models.subject import Subject


async def seed() -> None:
    async with async_session() as session:
        subjects = [
            Subject(name="Математика", slug="math"),
            Subject(name="Физика", slug="physics"),
            Subject(name="Биология", slug="biology"),
        ]
        interests = [
            Interest(name="IT", slug="it"),
            Interest(name="Науки", slug="science"),
            Interest(name="Арт", slug="art"),
        ]
        industry = ProfessionIndustry(name_ru="IT", name_uz="IT", icon="code", color="#7C3AED")
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
        session.add_all(subjects + interests + [industry, profession])
        await session.commit()


def main() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    main()
