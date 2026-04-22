import os
from functools import lru_cache
from urllib.parse import urlsplit, urlunsplit

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        resolved = value
        if not resolved:
            resolved = os.getenv("DATABASE_URL")
        if not resolved:
            resolved = "postgresql+asyncpg://postgres:postgres@localhost:5432/careerpath"

        if isinstance(resolved, str) and resolved.startswith("postgres://"):
            resolved = resolved.replace("postgres://", "postgresql+asyncpg://", 1)
        if isinstance(resolved, str) and resolved.startswith("postgresql://") and "+asyncpg" not in resolved:
            resolved = resolved.replace("postgresql://", "postgresql+asyncpg://", 1)

        if isinstance(resolved, str):
            parsed = urlsplit(resolved)
            if parsed.hostname == "db":
                netloc = parsed.netloc.replace("db", "localhost", 1)
                resolved = urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))

        return resolved

    project_name: str = Field(default="CareerPath API")
    environment: str = Field(default="local")
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@db:5432/careerpath",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    jwt_secret: SecretStr = Field(default="change-me", alias="JWT_SECRET")
    access_token_expire_minutes: int = Field(default=15, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=30, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    rate_limit_login_window_seconds: int = Field(default=900, alias="RATE_LIMIT_WINDOW_SECONDS")
    rate_limit_login_max_attempts: int = Field(default=5, alias="RATE_LIMIT_MAX_ATTEMPTS")
    cors_allow_origins: str = Field(default="http://localhost:3000,http://localhost:3001", alias="CORS_ALLOW_ORIGINS")
    email_verification_enabled: bool = Field(default=False, alias="EMAIL_VERIFICATION_ENABLED")
    email_provider: str = Field(default="console", alias="EMAIL_PROVIDER")
    email_from_address: str = Field(default="noreply@careerpath.local", alias="EMAIL_FROM_ADDRESS")
    smtp_host: str = Field(default="", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_username: str = Field(default="", alias="SMTP_USERNAME")
    smtp_password: SecretStr = Field(default="", alias="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")
    smtp_use_ssl: bool = Field(default=False, alias="SMTP_USE_SSL")
    email_verification_code_ttl_minutes: int = Field(default=10, alias="EMAIL_VERIFICATION_CODE_TTL_MINUTES")
    email_verification_resend_cooldown_seconds: int = Field(default=60, alias="EMAIL_VERIFICATION_RESEND_COOLDOWN_SECONDS")
    email_verification_max_attempts: int = Field(default=5, alias="EMAIL_VERIFICATION_MAX_ATTEMPTS")
    email_verification_code_length: int = Field(default=6, alias="EMAIL_VERIFICATION_CODE_LENGTH")
    email_verification_code_secret: SecretStr = Field(default="change-me-email-code", alias="EMAIL_VERIFICATION_CODE_SECRET")

    ai_provider: str = Field(default="openrouter", alias="AI_PROVIDER")
    ai_model: str = Field(default="openai/gpt-4o-mini", alias="AI_MODEL")
    ai_temperature: float = Field(default=0.2, alias="AI_TEMPERATURE")
    ai_timeout_seconds: int = Field(default=12, alias="AI_TIMEOUT_SECONDS")
    ai_max_retries: int = Field(default=1, alias="AI_MAX_RETRIES")
    ai_openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", alias="AI_OPENROUTER_BASE_URL")
    ai_openrouter_api_key: SecretStr = Field(default="change-me-openrouter-key", alias="AI_OPENROUTER_API_KEY")
    ai_prompt_profile: str = Field(default="careerpath_v1_default", alias="AI_PROMPT_PROFILE")
    ai_default_system_prompt: str = Field(
        default="Ты карьерный AI-интервьюер CareerPath. Возвращай ТОЛЬКО JSON по контракту. Не используй topic/signal вне whitelist.",
        alias="AI_DEFAULT_SYSTEM_PROMPT",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
