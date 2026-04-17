from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

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


@lru_cache()
def get_settings() -> Settings:
    return Settings()
