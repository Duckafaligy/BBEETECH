# l4_core/app.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .builder.router import router as builder_router
from .flows.router import router as flows_router
from .pages.router import router as pages_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Level 4 AI Backend",
        version="1.0.0",
        description="Stateless, multi-engine, Level-4 AI orchestration backend.",
    )

    # CORS (adjust origins as needed)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(builder_router, prefix="/api/builder", tags=["builder"])
    app.include_router(flows_router, prefix="/api/flows", tags=["flows"])
    app.include_router(pages_router, prefix="/api/pages", tags=["pages"])

    @app.get("/health", tags=["system"])
    async def health_check():
        return {
            "status": "ok",
            "env": settings.ENV,
            "version": "1.0.0",
        }

    return app


app = create_app()
