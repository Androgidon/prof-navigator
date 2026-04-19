import argparse
import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.base import async_session
from app.models.assessment_result import AssessmentResult
from app.models.assessment_session import AssessmentSession
from app.models.user import User
from app.models.user_favorite import UserFavorite


EXPORT_VERSION = "1.0"


@dataclass
class ExportArgs:
    output: Path
    email: Optional[str]
    include_assessments: bool


def normalize_email(value: str) -> str:
    return value.strip().lower()


def parse_args() -> ExportArgs:
    parser = argparse.ArgumentParser(description="Export users with profile/favorites")
    parser.add_argument("--output", type=Path, required=True, help="Path to output JSON file")
    parser.add_argument("--email", type=str, default=None, help="Export only one user by email")
    parser.add_argument("--include-assessments", action="store_true", help="Include assessment_sessions/results")
    args = parser.parse_args()
    email = normalize_email(args.email) if args.email else None
    return ExportArgs(output=args.output, email=email, include_assessments=args.include_assessments)


def serialize_user_account(user: User) -> dict[str, Any]:
    return {
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "hashed_password": user.hashed_password,
    }


def serialize_user_profile(user: User) -> Optional[dict[str, Any]]:
    profile = user.profile
    if profile is None:
        return None
    return {
        "full_name": profile.full_name,
        "birth_date": profile.birth_date,
        "country": profile.country,
        "region": profile.region,
        "city": profile.city,
        "language": profile.language,
        "grades": profile.grades,
        "interests": profile.interests,
    }


def serialize_favorites(favorites: list[UserFavorite]) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for favorite in favorites:
        profession = favorite.profession
        payload.append(
            {
                "profession_slug": profession.slug if profession else None,
                "note": favorite.note,
            }
        )
    return payload


def serialize_assessment_session(item: AssessmentSession) -> dict[str, Any]:
    return {
        "source_session_id": str(item.id),
        "assessment_slug": item.assessment_slug,
        "status": item.status,
        "started_at": item.started_at.isoformat() if item.started_at else None,
        "completed_at": item.completed_at.isoformat() if item.completed_at else None,
        "expires_at": item.expires_at.isoformat() if item.expires_at else None,
        "current_question_index": item.current_question_index,
        "question_set_json": item.question_set_json,
        "answers_json": item.answers_json,
        "progress_pct": item.progress_pct,
        "consistency_score": item.consistency_score,
        "confidence_score": item.confidence_score,
        "metadata_json": item.metadata_json,
    }


def serialize_assessment_result(item: AssessmentResult) -> dict[str, Any]:
    return {
        "source_result_id": str(item.id),
        "source_session_id": str(item.session_id),
        "assessment_slug": item.assessment_slug,
        "profile_scores_json": item.profile_scores_json,
        "profile_summary_json": item.profile_summary_json,
        "top_strengths_json": item.top_strengths_json,
        "work_style_json": item.work_style_json,
        "recommendations_json": item.recommendations_json,
        "next_steps_json": item.next_steps_json,
        "confidence_json": item.confidence_json,
        "scoring_breakdown_json": item.scoring_breakdown_json,
    }


async def load_assessments_for_user(session: AsyncSession, user_id: UUID) -> dict[str, Any]:
    sessions_result = await session.execute(
        select(AssessmentSession)
        .where(AssessmentSession.user_id == user_id)
        .order_by(AssessmentSession.created_at.asc())
    )
    sessions = list(sessions_result.scalars().all())
    session_ids = [item.id for item in sessions]

    results: list[AssessmentResult] = []
    if session_ids:
        results_result = await session.execute(
            select(AssessmentResult)
            .where(AssessmentResult.session_id.in_(session_ids))
            .order_by(AssessmentResult.created_at.asc())
        )
        results = list(results_result.scalars().all())

    return {
        "sessions": [serialize_assessment_session(item) for item in sessions],
        "results": [serialize_assessment_result(item) for item in results],
    }


async def run(args: ExportArgs) -> None:
    async with async_session() as session:
        query = (
            select(User)
            .options(selectinload(User.profile))
            .order_by(User.created_at.asc())
        )
        if args.email:
            query = query.where(func.lower(User.email) == args.email)

        users_result = await session.execute(query)
        users = list(users_result.scalars().all())

        payload_users: list[dict[str, Any]] = []

        for user in users:
            favorites_result = await session.execute(
                select(UserFavorite)
                .options(selectinload(UserFavorite.profession))
                .where(UserFavorite.user_id == user.id)
                .order_by(UserFavorite.created_at.asc())
            )
            favorites = list(favorites_result.scalars().all())

            user_payload: dict[str, Any] = {
                "account": serialize_user_account(user),
                "profile": serialize_user_profile(user),
                "favorites": serialize_favorites(favorites),
            }

            if args.include_assessments:
                user_payload["assessments"] = await load_assessments_for_user(session=session, user_id=user.id)

            payload_users.append(user_payload)

    output = {
        "version": EXPORT_VERSION,
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "include_assessments": args.include_assessments,
        "users": payload_users,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exported users: {len(payload_users)}")
    print(f"Output: {args.output}")


def main() -> None:
    asyncio.run(run(parse_args()))


if __name__ == "__main__":
    main()
