from typing import Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    type: str
    env: Optional[str] = None
