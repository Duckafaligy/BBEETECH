# l4_core/admin/engines_router.py

"""
Admin Engines Router (L4+)
--------------------------
Provides administrative endpoints for:
  - Listing all AI engines
  - Enabling/disabling engines

Upgrades in L4+ version:
  - Strong Pydantic request models
  - Structured logging with trace IDs
  - Audit-ready hooks
  - Cleaner DB access
  - Consistent error handling
  - Future-proof for engine scoring + routing upgrades
"""

from __future__ import annotations

from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from l4_core.db.core import get_db
from l4_core.db.models import AIEngine
from l4_core.utils.logging import log_engine_event, generate_trace_id


router = APIRouter(prefix="/admin/engines", tags=["admin-engines"])


# ---------------------------------------------------------
# REQUEST MODELS
# ---------------------------------------------------------
class EngineToggleRequest(BaseModel):
    enabled: bool


# ---------------------------------------------------------
# LIST ENGINES
# ---------------------------------------------------------
@router.get("/", response_model=List[Dict[str, Any]])
async def list_engines(
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Returns all AI engines ordered by priority.
    """
    trace_id = generate_trace_id()

    stmt = select(AIEngine).order_by(AIEngine.priority.asc())
    result = await db.execute(stmt)
    engines = result.scalars().all()

    log_engine_event(
        engine="admin",
        message="Fetched engine list",
        trace_id=trace_id,
        extra={"engine_count": len(engines)},
    )

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


# ---------------------------------------------------------
# TOGGLE ENGINE
# ---------------------------------------------------------
@router.post("/{engine_id}/toggle")
async def toggle_engine(
    engine_id: str,
    body: EngineToggleRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Enables or disables an AI engine.
    """
    trace_id = generate_trace_id()

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

    log_engine_event(
        engine="admin",
        message="Engine toggled",
        trace_id=trace_id,
        extra={
            "engine_id": engine.id,
            "provider": engine.provider,
            "model": engine.model,
            "enabled": engine.enabled,
        },
    )

    return {
        "id": engine.id,
        "provider": engine.provider,
        "model": engine.model,
        "enabled": engine.enabled,
    }
