from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class ProfessionListItemResponse(BaseModel):
    slug: str
    title: str
    cluster: str
    summary: str
    status: str


class RelatedProfessionResponse(BaseModel):
    slug: str
    title: str
    cluster: str


class ProfessionResponse(ProfessionListItemResponse):
    what_specialist_does: str
    who_suits: List[str] = Field(default_factory=list)
    important_subjects: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    how_to_start: List[str] = Field(default_factory=list)
    related_professions: List[RelatedProfessionResponse] = Field(default_factory=list)
