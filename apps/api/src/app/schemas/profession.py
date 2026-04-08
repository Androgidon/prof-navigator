from __future__ import annotations

from pydantic import BaseModel


class ProfessionResponse(BaseModel):
    id: str
    slug: str
    title_ru: str
    title_uz: str
    description: str | None
    industry_id: str

    class Config:
        orm_mode = True
