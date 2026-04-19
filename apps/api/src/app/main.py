from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.v1 import router as api_router
from app.core.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="CareerPath API", version="0.1.0")

    allow_origins = [origin.strip() for origin in settings.cors_allow_origins.split(",") if origin.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root() -> dict[str, bool]:
        return {"ok": True}

    app.include_router(health_router, prefix="/health")
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
