from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    type: str
    env: str | None = None
