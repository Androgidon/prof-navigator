from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ProfessionListItemResponse(BaseModel):
    id: str
    external_id: int
    slug: str
    title: str
    cluster: str
    summary: str
    status: str
    first_steps_short: List[str] = Field(default_factory=list)
    important_subjects_short: List[str] = Field(default_factory=list)
    completeness_score: int


class ProfessionDetailResponse(ProfessionListItemResponse):
    matrix_version_slug: str


class ProfessionCreateRequest(BaseModel):
    external_id: int
    slug: str
    title: str
    cluster: str
    summary: str
    status: str = "draft"
    matrix_version_slug: str = "matrix_v1"
    first_steps_short: List[str] = Field(default_factory=list)
    important_subjects_short: List[str] = Field(default_factory=list)


class ProfessionPatchRequest(BaseModel):
    title: Optional[str] = None
    cluster: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    first_steps_short: Optional[List[str]] = None
    important_subjects_short: Optional[List[str]] = None
    matrix_version_slug: Optional[str] = None
