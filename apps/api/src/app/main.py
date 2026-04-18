import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.health import router as health_router
from app.api.v1 import router as api_router
from app.core.settings import get_settings

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    logger.info("create_app: start")
    settings = get_settings()
    app = FastAPI(title="CareerPath API", version="0.1.0")

    raw_cors = settings.cors_allow_origins
    allow_origins = [origin.strip() for origin in raw_cors.split(",") if origin.strip()] if isinstance(raw_cors, str) else []

    logger.info(
        "API startup configuration",
        extra={
            "cors_allow_origins_count": len(allow_origins),
            "cors_allow_origins": allow_origins,
        },
    )

    @app.middleware("http")
    async def log_unhandled_exceptions(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception:
            logger.exception("Unhandled API error", extra={"path": request.url.path, "method": request.method})
            raise

    @app.exception_handler(ResponseValidationError)
    async def response_validation_exception_handler(request: Request, exc: ResponseValidationError) -> JSONResponse:
        logger.exception("Response validation error", extra={"path": request.url.path, "method": request.method})
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Global exception handler caught error", extra={"path": request.url.path, "method": request.method})
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.exception("Request validation error", extra={"path": request.url.path, "method": request.method})
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.get("/")
    async def root_health() -> dict[str, str]:
        return {"status": "ok", "service": "careerpath-api"}

    logger.info("create_app: add CORS middleware")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("create_app: include routers")
    app.include_router(health_router, prefix="/health")
    app.include_router(api_router, prefix="/api/v1")
    logger.info("create_app: completed")
    return app


app = create_app()
