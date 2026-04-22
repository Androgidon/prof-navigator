from datetime import datetime, timedelta, timezone
import uuid
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, get_db_session
from app.repositories.email_verification_code_repository import EmailVerificationCodeRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    AuthMeResponse,
    ChangeEmailConfirmRequest,
    ChangeEmailResponse,
    ChangeEmailStartRequest,
    RefreshTokenRequest,
    RegisterStartResponse,
    ResendEmailCodeRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    VerifyEmailCodeRequest,
)
from app.services.auth_service import AuthService
from app.services.email_sender import EmailSenderFactory
from app.services.email_verification_service import (
    CodeExpiredError,
    CodeInvalidError,
    EmailVerificationService,
    ResendCooldownError,
    TooManyAttemptsError,
    VerificationSettings,
)

settings = get_settings()

router = APIRouter()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _build_verification_service(session: AsyncSession) -> EmailVerificationService:
    return EmailVerificationService(
        repository=EmailVerificationCodeRepository(session),
        sender=EmailSenderFactory.build(),
        settings=VerificationSettings(
            ttl_minutes=settings.email_verification_code_ttl_minutes,
            resend_cooldown_seconds=settings.email_verification_resend_cooldown_seconds,
            max_attempts=settings.email_verification_max_attempts,
            code_length=settings.email_verification_code_length,
            code_secret=settings.email_verification_code_secret.get_secret_value(),
        ),
    )


def _token_pair_for_user(user_id: str) -> Tuple[str, uuid.UUID, str]:
    access_token = AuthService.create_access_token(user_id)
    refresh_id = uuid.uuid4()
    refresh_token_value = AuthService.create_refresh_token(user_id, str(refresh_id))
    return access_token, refresh_id, refresh_token_value


@router.post("/register/start", response_model=RegisterStartResponse)
async def register_start(payload: UserCreate, session: AsyncSession = Depends(get_db_session)) -> RegisterStartResponse:
    repo = UserRepository(session)
    token_repo = RefreshTokenRepository(session)

    existing = await repo.find_by_email(payload.email)
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пароли не совпадают")

    if not settings.email_verification_enabled:
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        hashed = AuthService.hash_password(payload.password)
        user = await repo.create(str(payload.email).strip().lower(), hashed)
        user.email_verified = True

        access_token, refresh_id, refresh_token_value = _token_pair_for_user(str(user.id))
        await token_repo.create(
            user_id=str(user.id),
            token_id=refresh_id,
            token_hash=AuthService.hash_token(refresh_token_value),
            expires_at=_now() + timedelta(days=settings.refresh_token_expire_days),
        )
        await session.commit()
        return RegisterStartResponse(
            status="registered",
            email=user.email,
            access_token=access_token,
            refresh_token=refresh_token_value,
        )

    verification_service = _build_verification_service(session)

    if existing:
        if existing.email_verified:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        if not AuthService.verify_password(payload.password, existing.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email уже зарегистрирован, завершите подтверждение через существующий пароль",
            )
        if not existing.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
        resend_available_at = await verification_service.issue_code(user=existing, force_resend=True)
        await session.commit()
        seconds = max(0, int((resend_available_at - _now()).total_seconds()))
        return RegisterStartResponse(
            status="verification_required",
            email=existing.email,
            resend_available_in_seconds=seconds,
        )

    hashed = AuthService.hash_password(payload.password)
    user = await repo.create(str(payload.email).strip().lower(), hashed)
    user.email_verified = False

    resend_available_at = await verification_service.issue_code(user=user, force_resend=False)

    await session.commit()
    seconds = max(0, int((resend_available_at - _now()).total_seconds()))
    return RegisterStartResponse(status="verification_required", email=user.email, resend_available_in_seconds=seconds)


@router.post("/verify-email-code", response_model=TokenResponse)
async def verify_email_code(payload: VerifyEmailCodeRequest, session: AsyncSession = Depends(get_db_session)) -> TokenResponse:
    if not settings.email_verification_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email verification disabled")

    repo = UserRepository(session)
    token_repo = RefreshTokenRepository(session)

    user = await repo.find_by_email(str(payload.email))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    verification_service = _build_verification_service(session)
    try:
        await verification_service.verify(user=user, code=payload.code)
    except CodeInvalidError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except CodeExpiredError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except TooManyAttemptsError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc))

    access_token, refresh_id, refresh_token_value = _token_pair_for_user(str(user.id))
    await token_repo.create(
        user_id=str(user.id),
        token_id=refresh_id,
        token_hash=AuthService.hash_token(refresh_token_value),
        expires_at=_now() + timedelta(days=settings.refresh_token_expire_days),
    )

    await session.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token_value)


@router.post("/resend-email-code", response_model=RegisterStartResponse)
async def resend_email_code(
    payload: ResendEmailCodeRequest,
    session: AsyncSession = Depends(get_db_session),
) -> RegisterStartResponse:
    if not settings.email_verification_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email verification disabled")

    repo = UserRepository(session)

    user = await repo.find_by_email(str(payload.email))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    if user.email_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email уже подтверждён")

    verification_service = _build_verification_service(session)
    try:
        resend_available_at = await verification_service.issue_code(user=user, force_resend=True)
    except ResendCooldownError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc))

    await session.commit()
    seconds = max(0, int((resend_available_at - _now()).total_seconds()))
    return RegisterStartResponse(status="verification_required", email=user.email, resend_available_in_seconds=seconds)


@router.post("/register", response_model=RegisterStartResponse)
async def register(payload: UserCreate, session: AsyncSession = Depends(get_db_session)) -> RegisterStartResponse:
    # Backward-compatible alias; now registration requires verification.
    return await register_start(payload=payload, session=session)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, session: AsyncSession = Depends(get_db_session)) -> TokenResponse:
    repo = UserRepository(session)
    token_repo = RefreshTokenRepository(session)
    user = await repo.find_by_email(payload.email)
    if not user or not AuthService.verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Подтвердите email перед входом",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    access_token, refresh_id, refresh_token_value = _token_pair_for_user(str(user.id))
    await token_repo.create(
        user_id=str(user.id),
        token_id=refresh_id,
        token_hash=AuthService.hash_token(refresh_token_value),
        expires_at=_now() + timedelta(days=settings.refresh_token_expire_days),
    )
    await session.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token_value)


@router.get("/me", response_model=AuthMeResponse)
async def auth_me(
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
) -> AuthMeResponse:
    return AuthMeResponse(user_id=str(current_user.id), email=current_user.email)


@router.post("/change-email/start", response_model=ChangeEmailResponse)
async def change_email_start(
    payload: ChangeEmailStartRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
) -> ChangeEmailResponse:
    if not settings.email_verification_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email verification disabled")

    repo = UserRepository(session)
    verification_service = _build_verification_service(session)

    new_email = str(payload.new_email).strip().lower()
    if new_email == current_user.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Новый email совпадает с текущим")

    existing = await repo.find_by_email(new_email)
    if existing and str(existing.id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    try:
        resend_available_at = await verification_service.issue_code(
            user=current_user,
            force_resend=True,
            target_email=new_email,
        )
    except ResendCooldownError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc))

    await session.commit()
    seconds = max(0, int((resend_available_at - _now()).total_seconds()))
    return ChangeEmailResponse(status="verification_required", email=new_email, resend_available_in_seconds=seconds)


@router.post("/change-email/confirm", response_model=ChangeEmailResponse)
async def change_email_confirm(
    payload: ChangeEmailConfirmRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user=Depends(get_current_user),
) -> ChangeEmailResponse:
    if not settings.email_verification_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email verification disabled")

    verification_service = _build_verification_service(session)
    verification_repo = EmailVerificationCodeRepository(session)
    latest = await verification_repo.get_latest_active(current_user.id)
    if latest is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Код подтверждения не найден")

    pending_email = latest.email.strip().lower()

    repo = UserRepository(session)
    existing = await repo.find_by_email(pending_email)
    if existing and str(existing.id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    try:
        await verification_service.verify(user=current_user, code=payload.code, expected_email=pending_email)
    except CodeInvalidError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except CodeExpiredError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except TooManyAttemptsError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc))

    current_user.email = pending_email
    current_user.email_verified = True
    await session.commit()

    return ChangeEmailResponse(status="changed", email=current_user.email, resend_available_in_seconds=0)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshTokenRequest, session: AsyncSession = Depends(get_db_session)) -> TokenResponse:
    token_repo = RefreshTokenRepository(session)
    decoded = AuthService.token_payload(payload.refresh_token)
    if not decoded or decoded.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    jti = decoded.get("jti")
    if not jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing id")
    stored = await token_repo.find_by_jti(jti)
    if not stored or stored.revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")
    expiration = AuthService.token_expiration(decoded)
    if expiration and expiration < _now():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    user_id = decoded.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing subject")

    repo = UserRepository(session)
    user = await repo.find_by_id(user_id)
    if not user or not user.email_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verified")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive")

    access_token = AuthService.create_access_token(user_id)
    next_refresh_id = uuid.uuid4()
    refresh_token_value = AuthService.create_refresh_token(user_id, str(next_refresh_id))
    stored.revoked = True
    await token_repo.create(
        user_id=user_id,
        token_id=next_refresh_id,
        token_hash=AuthService.hash_token(refresh_token_value),
        expires_at=_now() + timedelta(days=settings.refresh_token_expire_days),
    )
    await session.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token_value)
