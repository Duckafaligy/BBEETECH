# backend/runtime_router.py

"""
Runtime Router (L4+)
--------------------
Endpoints for executing runtime AI operations.
This file stays in backend/ and is included by the main FastAPI app.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from l4_core.db.core import get_db
from l4_core.ai.runtime_engine import RuntimeEngine

router = APIRouter()


@router.post("/run")
async def run_runtime(payload: dict, db=Depends(get_db)):
    engine = RuntimeEngine(db)
    result = await engine.run(payload)
    return {"result": result}
