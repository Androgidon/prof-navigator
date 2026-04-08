from datetime import datetime, timedelta
import uuid

from app.core.config import get_settings
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_session
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
)
from app.services.auth_service import AuthService

settings = get_settings()

router = APIRouter()


def _now() -> datetime:
    return datetime.utcnow()


@router.post("/register", response_model=TokenResponse)
async def register(payload: UserCreate, session=Depends(get_session)) -> TokenResponse:
    repo = UserRepository(session)
    token_repo = RefreshTokenRepository(session)
    existing = await repo.find_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    hashed = AuthService.hash_password(payload.password)
    user = await repo.create(payload.email, hashed)
    access_token = AuthService.create_access_token(str(user.id))
    refresh_id = user.id
    refresh_token_value = AuthService.create_refresh_token(str(user.id), str(refresh_id))
    await token_repo.create(
        user_id=str(user.id),
        token_id=refresh_id,
        token_hash=AuthService.hash_token(refresh_token_value),
        expires_at=_now() + timedelta(days=settings.refresh_token_expire_days),
    )
    await session.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token_value)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, session=Depends(get_session)) -> TokenResponse:
    repo = UserRepository(session)
    token_repo = RefreshTokenRepository(session)
    user = await repo.find_by_email(payload.email)
    if not user or not AuthService.verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = AuthService.create_access_token(str(user.id))
    refresh_id = user.id
    refresh_token_value = AuthService.create_refresh_token(str(user.id), str(refresh_id))
    await token_repo.create(
        user_id=str(user.id),
        token_id=refresh_id,
        token_hash=AuthService.hash_token(refresh_token_value),
        expires_at=_now() + timedelta(days=settings.refresh_token_expire_days),
    )
    await session.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token_value)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshTokenRequest, session=Depends(get_session)) -> TokenResponse:
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
    access_token = AuthService.create_access_token(user_id)
    refresh_id = stored.token_id
    refresh_token_value = AuthService.create_refresh_token(user_id, str(refresh_id))
    stored.revoked = True
    await token_repo.create(
        user_id=user_id,
        token_id=uuid.uuid4(),
        token_hash=AuthService.hash_token(refresh_token_value),
        expires_at=_now() + timedelta(days=settings.refresh_token_expire_days),
    )
    await session.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token_value)
