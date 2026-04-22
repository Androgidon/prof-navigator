from __future__ import annotations

import asyncio
import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage as SmtpEmailMessage

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


class SmtpEmailSender(EmailSender):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        from_address: str,
        use_tls: bool,
        use_ssl: bool,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._from_address = from_address
        self._use_tls = use_tls
        self._use_ssl = use_ssl

    def _send_sync(self, message: EmailMessage) -> None:
        email_message = SmtpEmailMessage()
        email_message["From"] = self._from_address
        email_message["To"] = message.to_email
        email_message["Subject"] = message.subject
        email_message.set_content(message.body)

        smtp_cls = smtplib.SMTP_SSL if self._use_ssl else smtplib.SMTP
        with smtp_cls(self._host, self._port, timeout=20) as smtp:
            if not self._use_ssl and self._use_tls:
                smtp.starttls()
            if self._username:
                smtp.login(self._username, self._password)
            smtp.send_message(email_message)

    async def send(self, message: EmailMessage) -> None:
        await asyncio.to_thread(self._send_sync, message)


class EmailSenderFactory:
    @staticmethod
    def build() -> EmailSender:
        settings = get_settings()
        provider = settings.email_provider.strip().lower()

        if provider in {"smtp", "mail", "mailgun-smtp"}:
            if not settings.smtp_host.strip():
                logger.warning("EMAIL_PROVIDER=%s but SMTP_HOST is empty, fallback to console", provider)
                return ConsoleEmailSender()
            return SmtpEmailSender(
                host=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_username,
                password=settings.smtp_password.get_secret_value(),
                from_address=settings.email_from_address,
                use_tls=settings.smtp_use_tls,
                use_ssl=settings.smtp_use_ssl,
            )

        if provider in {"console", "stub", ""}:
            return ConsoleEmailSender()
        logger.warning("Unknown EMAIL_PROVIDER=%s, fallback to console", provider)
        return ConsoleEmailSender()
