from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.v1 import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(title="CareerPath API", version="0.1.0")
    app.include_router(health_router, prefix="/health")
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
