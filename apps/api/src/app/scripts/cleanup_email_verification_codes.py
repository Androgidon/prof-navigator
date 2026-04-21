import asyncio
from argparse import ArgumentParser
from datetime import timedelta

from app.db.base import async_session
from app.repositories.email_verification_code_repository import EmailVerificationCodeRepository
from app.services.email_verification_service import utc_now


def parse_args() -> int:
    parser = ArgumentParser(description="Cleanup expired/consumed email verification codes")
    parser.add_argument("--keep-consumed-hours", type=int, default=24)
    args = parser.parse_args()
    return max(1, args.keep_consumed_hours)


async def run(keep_consumed_hours: int) -> None:
    now = utc_now()
    consumed_before = now - timedelta(hours=keep_consumed_hours)

    async with async_session() as session:
        repo = EmailVerificationCodeRepository(session)
        deleted = await repo.delete_expired_or_consumed_before(now=now, consumed_before=consumed_before)
        await session.commit()

    print(f"Deleted verification codes: {deleted}")


def main() -> None:
    asyncio.run(run(parse_args()))


if __name__ == "__main__":
    main()
