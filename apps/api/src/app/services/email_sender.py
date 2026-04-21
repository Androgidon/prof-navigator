from __future__ import annotations

import logging
from dataclasses import dataclass

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    to_email: str
    subject: str
    body: str


class EmailSender:
    async def send(self, message: EmailMessage) -> None:
        raise NotImplementedError


class ConsoleEmailSender(EmailSender):
    async def send(self, message: EmailMessage) -> None:
        logger.info(
            "EMAIL_STUB to=%s subject=%s body=%s",
            message.to_email,
            message.subject,
            message.body,
        )


class EmailSenderFactory:
    @staticmethod
    def build() -> EmailSender:
        settings = get_settings()
        provider = settings.email_provider.strip().lower()
        # Stub-only for now, provider extension point is ready.
        if provider in {"console", "stub", ""}:
            return ConsoleEmailSender()
        return ConsoleEmailSender()
