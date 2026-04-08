from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = Field(default="CareerPath API")
    environment: str = Field(default="local")
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@db:5432/careerpath",
        env="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", env="REDIS_URL")
    jwt_secret: SecretStr = Field(default="change-me", env="JWT_SECRET")
    access_token_expire_minutes: int = Field(default=15, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=30, env="REFRESH_TOKEN_EXPIRE_DAYS")
    rate_limit_login_window_seconds: int = Field(default=900, env="RATE_LIMIT_WINDOW_SECONDS")
    rate_limit_login_max_attempts: int = Field(default=5, env="RATE_LIMIT_MAX_ATTEMPTS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
