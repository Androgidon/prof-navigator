from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.v1 import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(title="CareerPath API", version="0.1.0")

    @app.get("/")
    async def root_health() -> dict[str, str]:
        return {"status": "ok", "service": "careerpath-api"}
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router, prefix="/health")
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
