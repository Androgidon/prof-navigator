from __future__ import annotations

import uuid
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class ProfileBase(BaseModel):
    full_name: Optional[str] = None
    birth_date: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    school: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    language: Optional[str] = None
    grades: Optional[Dict[str, int]] = None
    interests: Optional[List[str]] = None


class ProfileCreate(ProfileBase):
    user_id: str


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
