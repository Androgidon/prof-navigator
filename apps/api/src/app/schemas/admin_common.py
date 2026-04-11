from __future__ import annotations

from pydantic import BaseModel


class AdminMeResponse(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool


class ApiErrorResponse(BaseModel):
    code: str
    detail: str
