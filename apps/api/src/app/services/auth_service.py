from datetime import datetime, timedelta

from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.settings import get_settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
settings = get_settings()


class AuthService:
    algorithm = "HS256"

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return pwd_context.verify(password, hashed)

    @staticmethod
    def hash_token(token: str) -> str:
        return pwd_context.hash(token)

    @staticmethod
    def verify_token_hash(token: str, hashed: str) -> bool:
        return pwd_context.verify(token, hashed)

    @staticmethod
    def token_payload(token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(
                token,
                settings.jwt_secret.get_secret_value(),
                algorithms=[AuthService.algorithm],
            )
        except JWTError:
            return None

    @staticmethod
    def token_expiration(payload: Optional[Dict[str, Any]]) -> Optional[datetime]:
        if not payload:
            return None
        exp = payload.get("exp")
        if exp is None:
            return None
        return datetime.utcfromtimestamp(exp)

    @staticmethod
    def create_access_token(subject: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        payload = {"sub": subject, "exp": expire}
        return jwt.encode(payload, settings.jwt_secret.get_secret_value(), algorithm=AuthService.algorithm)

    @staticmethod
    def create_refresh_token(subject: str, token_id: str) -> str:
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        payload = {"sub": subject, "exp": expire, "type": "refresh", "jti": token_id}
        return jwt.encode(payload, settings.jwt_secret.get_secret_value(), algorithm=AuthService.algorithm)
