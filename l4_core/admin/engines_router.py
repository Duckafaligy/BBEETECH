# l4_core/admin/engines_router.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import AIEngine, get_db
from ..utils.logging import log_system

router = APIRouter(prefix="/admin/engines", tags=["admin-engines"])


class EngineToggleRequest:
    def __init__(self, enabled: bool):
        self.enabled = enabled


@router.get("/", response_model=list[dict])
async def list_engines(db: AsyncSession = Depends(get_db)) -> List[dict]:
    stmt = select(AIEngine).order_by(AIEngine.priority.asc())
    result = await db.execute(stmt)
    engines = result.scalars().all()

    return [
        {
            "id": e.id,
            "provider": e.provider,
            "model": e.model,
            "label": e.label,
            "enabled": e.enabled,
            "priority": e.priority,
            "allow_fallback": e.allow_fallback,
            "total_calls": e.total_calls,
            "total_tokens": e.total_tokens,
            "avg_latency_ms": e.avg_latency_ms,
            "created_at": e.created_at,
            "updated_at": e.updated_at,
        }
        for e in engines
    ]


@router.post("/{engine_id}/toggle")
async def toggle_engine(
    engine_id: str,
    body: EngineToggleRequest,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(AIEngine).where(AIEngine.id == engine_id)
    result = await db.execute(stmt)
    engine = result.scalar_one_or_none()

    if not engine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engine not found",
        )

    engine.enabled = body.enabled
    await db.commit()
    await db.refresh(engine)

    log_system(
        f"Engine toggled: {engine.provider}:{engine.model}",
        extra={"enabled": engine.enabled, "engine_id": engine.id},
    )

    return {
        "id": engine.id,
        "provider": engine.provider,
        "model": engine.model,
        "enabled": engine.enabled,
    }
