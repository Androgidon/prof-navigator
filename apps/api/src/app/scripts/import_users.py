import argparse
import asyncio
import json
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import and_, cast, func, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import async_session
from app.models.assessment_result import AssessmentResult
from app.models.assessment_session import AssessmentSession
from app.models.profession import Profession
from app.models.profile import UserProfile
from app.models.user import User
from app.models.user_favorite import UserFavorite
from app.services.auth_service import AuthService


@dataclass
class ImportArgs:
    input: Path
    mode: str
    password_mode: str
    include_assessments: bool
    default_password: Optional[str]
    allow_password_update: bool


def normalize_email(value: str) -> str:
    return value.strip().lower()


def parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def parse_args() -> ImportArgs:
    parser = argparse.ArgumentParser(description="Import users with profile/favorites")
    parser.add_argument("--input", type=Path, required=True, help="Path to import JSON")
    parser.add_argument("--mode", choices=["create", "update", "upsert"], default="upsert")
    parser.add_argument(
        "--password-mode",
        choices=["import-hash", "skip", "reset-required"],
        default="skip",
        help="Password handling policy",
    )
    parser.add_argument("--default-password", type=str, default=None, help="Used for create when password-mode=skip")
    parser.add_argument("--allow-password-update", action="store_true", help="Allow updating password for existing users")
    parser.add_argument("--include-assessments", action="store_true", help="Import assessment_sessions/results if present")
    args = parser.parse_args()
    return ImportArgs(
        input=args.input,
        mode=args.mode,
        password_mode=args.password_mode,
        include_assessments=args.include_assessments,
        default_password=args.default_password,
        allow_password_update=args.allow_password_update,
    )


def resolve_password_hash(
    account: dict[str, Any],
    password_mode: str,
    default_password: Optional[str],
    is_new_user: bool,
    allow_password_update: bool,
) -> Optional[str]:
    imported_hash = account.get("hashed_password")

    if password_mode == "import-hash":
        if not imported_hash:
            if is_new_user:
                raise ValueError("hashed_password is required for create with password-mode=import-hash")
            return None
        if is_new_user or allow_password_update:
            return str(imported_hash)
        return None

    if password_mode == "skip":
        if not is_new_user:
            return None
        if not default_password:
            raise ValueError("default_password is required for create with password-mode=skip")
        return AuthService.hash_password(default_password)

    if password_mode == "reset-required":
        if is_new_user:
            return AuthService.hash_password(secrets.token_urlsafe(32))
        if allow_password_update:
            return AuthService.hash_password(secrets.token_urlsafe(32))
        return None

    raise ValueError(f"Unsupported password mode: {password_mode}")


async def upsert_profile(session: AsyncSession, user: User, profile_data: Optional[dict[str, Any]]) -> str:
    if profile_data is None:
        return "skipped"

    result = await session.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalars().first()

    if profile is None:
        profile = UserProfile(user_id=user.id)
        session.add(profile)
        action = "created"
    else:
        action = "updated"

    profile.full_name = profile_data.get("full_name")
    profile.birth_date = profile_data.get("birth_date")
    profile.country = profile_data.get("country")
    profile.region = profile_data.get("region")
    profile.city = profile_data.get("city")
    profile.language = profile_data.get("language")
    profile.grades = profile_data.get("grades")
    profile.interests = profile_data.get("interests")
    await session.flush()
    return action


async def upsert_favorites(session: AsyncSession, user: User, favorites_data: list[dict[str, Any]]) -> dict[str, int]:
    created = 0
    skipped = 0

    for item in favorites_data:
        profession_slug = (item.get("profession_slug") or "").strip()
        note = item.get("note")

        if not profession_slug:
            skipped += 1
            continue

        profession_result = await session.execute(select(Profession).where(Profession.slug == profession_slug))
        profession = profession_result.scalars().first()
        if profession is None:
            skipped += 1
            continue

        existing_result = await session.execute(
            select(UserFavorite).where(
                and_(
                    UserFavorite.user_id == user.id,
                    UserFavorite.profession_id == profession.id,
                )
            )
        )
        existing = existing_result.scalars().first()
        if existing is not None:
            if note is not None and existing.note != note:
                existing.note = note
            skipped += 1
            continue

        session.add(UserFavorite(user_id=user.id, profession_id=profession.id, note=note))
        created += 1

    await session.flush()
    return {"created": created, "skipped": skipped}


async def import_assessments(session: AsyncSession, user: User, assessments_data: dict[str, Any]) -> dict[str, int]:
    sessions_data = list(assessments_data.get("sessions") or [])
    results_data = list(assessments_data.get("results") or [])

    created_sessions = 0
    updated_sessions = 0
    created_results = 0
    updated_results = 0

    source_to_target_session: dict[str, str] = {}

    for item in sessions_data:
        assessment_slug = item.get("assessment_slug")
        if not assessment_slug:
            continue
        started_at = parse_dt(item.get("started_at"))
        completed_at = parse_dt(item.get("completed_at"))
        status = item.get("status") or "started"

        result = await session.execute(
            select(AssessmentSession).where(
                AssessmentSession.user_id == user.id,
                AssessmentSession.assessment_slug == assessment_slug,
                AssessmentSession.started_at == started_at,
                AssessmentSession.completed_at == completed_at,
            )
        )
        existing = result.scalars().first()

        if existing is None:
            existing = AssessmentSession(
                user_id=user.id,
                assessment_slug=assessment_slug,
            )
            session.add(existing)
            created_sessions += 1
        else:
            updated_sessions += 1

        existing.status = status
        existing.expires_at = parse_dt(item.get("expires_at"))
        existing.current_question_index = int(item.get("current_question_index") or 0)
        existing.question_set_json = item.get("question_set_json") or []
        existing.answers_json = item.get("answers_json") or {}
        existing.progress_pct = int(item.get("progress_pct") or 0)
        existing.consistency_score = item.get("consistency_score")
        existing.confidence_score = item.get("confidence_score")
        existing.metadata_json = item.get("metadata_json") or {}
        existing.started_at = started_at
        existing.completed_at = completed_at

        await session.flush()
        source_id = item.get("source_session_id")
        if source_id:
            source_to_target_session[str(source_id)] = str(existing.id)

    for item in results_data:
        source_session_id = str(item.get("source_session_id") or "")
        target_session_id = source_to_target_session.get(source_session_id)
        if not target_session_id:
            continue

        result = await session.execute(
            select(AssessmentResult).where(
                AssessmentResult.session_id == cast(target_session_id, UUID(as_uuid=True))
            )
        )
        existing = result.scalars().first()

        if existing is None:
            existing = AssessmentResult(
                session_id=uuid.UUID(target_session_id),
                assessment_slug=item.get("assessment_slug") or "",
            )
            session.add(existing)
            created_results += 1
        else:
            updated_results += 1

        existing.assessment_slug = item.get("assessment_slug") or existing.assessment_slug
        existing.profile_scores_json = item.get("profile_scores_json") or {}
        existing.profile_summary_json = item.get("profile_summary_json") or {}
        existing.top_strengths_json = item.get("top_strengths_json") or []
        existing.work_style_json = item.get("work_style_json") or {}
        existing.recommendations_json = item.get("recommendations_json") or []
        existing.next_steps_json = item.get("next_steps_json") or {}
        existing.confidence_json = item.get("confidence_json") or {}
        existing.scoring_breakdown_json = item.get("scoring_breakdown_json") or {}

    await session.flush()
    return {
        "created_sessions": created_sessions,
        "updated_sessions": updated_sessions,
        "created_results": created_results,
        "updated_results": updated_results,
    }


async def process_user(
    session: AsyncSession,
    user_data: dict[str, Any],
    args: ImportArgs,
) -> dict[str, Any]:
    account = dict(user_data.get("account") or {})
    email_raw = account.get("email")
    if not email_raw:
        raise ValueError("account.email is required")

    email = normalize_email(str(email_raw))

    user_result = await session.execute(select(User).where(func.lower(User.email) == email))
    existing_user = user_result.scalars().first()

    if existing_user is None and args.mode == "update":
        return {"status": "skipped", "reason": "user_not_found", "email": email}

    if existing_user is not None and args.mode == "create":
        return {"status": "skipped", "reason": "user_already_exists", "email": email}

    is_new_user = existing_user is None

    if is_new_user:
        password_hash = resolve_password_hash(
            account=account,
            password_mode=args.password_mode,
            default_password=args.default_password,
            is_new_user=True,
            allow_password_update=args.allow_password_update,
        )
        user = User(
            email=email,
            hashed_password=password_hash or AuthService.hash_password(secrets.token_urlsafe(32)),
            role=account.get("role") or "student",
            is_active=bool(account.get("is_active", True)),
        )
        session.add(user)
        await session.flush()
        user_action = "created"
    else:
        user = existing_user
        user.role = account.get("role") or user.role
        user.is_active = bool(account.get("is_active", user.is_active))

        password_hash = resolve_password_hash(
            account=account,
            password_mode=args.password_mode,
            default_password=args.default_password,
            is_new_user=False,
            allow_password_update=args.allow_password_update,
        )
        if password_hash:
            user.hashed_password = password_hash

        await session.flush()
        user_action = "updated"

    profile_action = await upsert_profile(session=session, user=user, profile_data=user_data.get("profile"))
    favorites_stats = await upsert_favorites(session=session, user=user, favorites_data=list(user_data.get("favorites") or []))

    assessments_stats = None
    if args.include_assessments:
        assessments_stats = await import_assessments(session=session, user=user, assessments_data=dict(user_data.get("assessments") or {}))

    return {
        "status": "ok",
        "email": email,
        "user_action": user_action,
        "profile_action": profile_action,
        "favorites": favorites_stats,
        "assessments": assessments_stats,
    }


async def run(args: ImportArgs) -> None:
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    users_data = list(raw.get("users") or [])

    report: dict[str, Any] = {
        "total": len(users_data),
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "failed": 0,
        "items": [],
    }

    for item in users_data:
        try:
            async with async_session() as session:
                async with session.begin():
                    result = await process_user(session=session, user_data=item, args=args)

            status = result.get("status")
            if status == "ok":
                if result.get("user_action") == "created":
                    report["created"] += 1
                else:
                    report["updated"] += 1
            elif status == "skipped":
                report["skipped"] += 1
            else:
                report["failed"] += 1

            report["items"].append(result)
        except Exception as exc:
            report["failed"] += 1
            report["items"].append(
                {
                    "status": "failed",
                    "email": ((item.get("account") or {}).get("email")),
                    "error": str(exc),
                    "error_type": exc.__class__.__name__,
                }
            )

    print(json.dumps(report, ensure_ascii=False, indent=2))


def main() -> None:
    asyncio.run(run(parse_args()))


if __name__ == "__main__":
    main()
