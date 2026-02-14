# l4_core/app.py

from __future__ import annotations

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from l4_core.config import settings
from l4_core.db.core import init_db, AsyncSessionLocal
from l4_core.utils.logging import log_engine_event, generate_trace_id

# Routers
from l4_core.ai.router import router as ai_router
from l4_core.builder.router import router as builder_router
from l4_core.flows.router import router as flows_router
from l4_core.pages.router import router as pages_router

from l4_core.audit.audit_orchestrator import AuditOrchestrator


def create_app() -> FastAPI:
    trace_id = generate_trace_id()

    app = FastAPI(
        title="Level 4 AI Backend",
        version="1.0.0",
        description="Stateless, multi-engine, Level-4 AI orchestration backend.",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(ai_router, prefix="/api/ai", tags=["ai"])
    app.include_router(builder_router, prefix="/api/builder", tags=["builder"])
    app.include_router(flows_router, prefix="/api/flows", tags=["flows"])
    app.include_router(pages_router, prefix="/api/pages", tags=["pages"])

    # Health
    @app.get("/health", tags=["system"])
    async def health_check():
        return {
            "status": "ok",
            "env": settings.ENV,
            "version": "1.0.0",
        }

    # Startup
    @app.on_event("startup")
    async def on_startup():
        await init_db()

        if settings.ENABLE_AUDIT_ON_STARTUP:
            async with AsyncSessionLocal() as db:
                auditor = AuditOrchestrator(db)
                await auditor.audit_all_workspaces(apply_fixes=False)

        log_engine_event(
            engine="system",
            message="Application startup complete",
            trace_id=trace_id,
            extra={"audit_on_startup": settings.ENABLE_AUDIT_ON_STARTUP},
        )

    # Shutdown
    @app.on_event("shutdown")
    async def on_shutdown():
        log_engine_event(
            engine="system",
            message="Application shutdown complete",
            trace_id=trace_id,
        )

    return app


app = create_app()
