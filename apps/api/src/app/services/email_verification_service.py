from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.models.user import User
from app.repositories.email_verification_code_repository import EmailVerificationCodeRepository
from app.services.email_sender import EmailMessage, EmailSender


class VerificationError(Exception):
    pass


class CodeExpiredError(VerificationError):
    pass


class CodeInvalidError(VerificationError):
    pass


class TooManyAttemptsError(VerificationError):
    pass


class ResendCooldownError(VerificationError):
    pass


@dataclass
class VerificationSettings:
    ttl_minutes: int
    resend_cooldown_seconds: int
    max_attempts: int
    code_length: int
    code_secret: str


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EmailVerificationService:
    def __init__(
        self,
        repository: EmailVerificationCodeRepository,
        sender: EmailSender,
        settings: VerificationSettings,
    ) -> None:
        self._repository = repository
        self._sender = sender
        self._settings = settings

    def _now(self) -> datetime:
        return utc_now()

    def _generate_code(self) -> str:
        upper = 10 ** self._settings.code_length
        lower = 10 ** (self._settings.code_length - 1)
        return str(secrets.randbelow(upper - lower) + lower)

    def _hash_code(self, user_id: uuid.UUID, code: str) -> str:
        source = f"{self._settings.code_secret}:{user_id}:{code}"
        return hashlib.sha256(source.encode("utf-8")).hexdigest()

    async def issue_code(self, user: User, force_resend: bool) -> datetime:
        now = self._now()
        latest = await self._repository.get_latest_active(user.id)

        if force_resend and latest and latest.resend_available_at > now:
            raise ResendCooldownError("Слишком рано запрашивать новый код")

        await self._repository.invalidate_active_codes(user.id, consumed_at=now)

        code = self._generate_code()
        code_hash = self._hash_code(user.id, code)
        expires_at = now + timedelta(minutes=self._settings.ttl_minutes)
        resend_available_at = now + timedelta(seconds=self._settings.resend_cooldown_seconds)

        await self._repository.create(
            user_id=user.id,
            email=user.email,
            code_hash=code_hash,
            expires_at=expires_at,
            resend_available_at=resend_available_at,
            attempts_left=self._settings.max_attempts,
        )

        await self._sender.send(
            EmailMessage(
                to_email=user.email,
                subject="Код подтверждения CareerPath",
                body=f"Ваш код подтверждения: {code}. Код действует {self._settings.ttl_minutes} минут.",
            )
        )

        return resend_available_at

    async def verify(self, user: User, code: str) -> None:
        now = self._now()
        latest = await self._repository.get_latest_active(user.id)
        if latest is None:
            raise CodeInvalidError("Код подтверждения не найден")

        expires_at = latest.expires_at if latest.expires_at.tzinfo else latest.expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            raise CodeExpiredError("Код подтверждения истек")

        if latest.attempts_left <= 0:
            raise TooManyAttemptsError("Превышено количество попыток")

        expected = self._hash_code(user.id, code)
        if expected != latest.code_hash:
            await self._repository.decrement_attempts(latest)
            if latest.attempts_left <= 0:
                raise TooManyAttemptsError("Превышено количество попыток")
            raise CodeInvalidError("Неверный код подтверждения")

        await self._repository.consume(latest, consumed_at=now)
        user.email_verified = True
