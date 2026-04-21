from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RegisterStartResponse(BaseModel):
    status: str
    email: EmailStr
    resend_available_in_seconds: int = 0
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class VerifyEmailCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)

    @field_validator("code")
    @classmethod
    def only_digits(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Код должен состоять из цифр")
        return value


class ResendEmailCodeRequest(BaseModel):
    email: EmailStr


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
