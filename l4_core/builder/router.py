# l4_core/builder/router.py

from __future__ import annotations

from fastapi import APIRouter, Depends
from l4_core.db.core import get_db
from l4_core.ai.flow_engine import FlowEngine
from l4_core.ai.workspace_factory import WorkspaceFactory

router = APIRouter()


@router.post("/generate")
async def generate_artifact(payload: dict, db=Depends(get_db)):
    """
    High-level builder endpoint.
    From IR/spec, generate code, docs, or assets.
    """
    workspace_id = payload.get("workspace_id")
    flow_key = payload.get("flow_key")
    inputs = payload.get("inputs", {})

    factory = WorkspaceFactory(db)
    workspace = await factory.get_workspace(workspace_id)

    engine = FlowEngine(db, workspace=workspace)
    result = await engine.run_flow(flow_key=flow_key, inputs=inputs)

    return {"workspace_id": workspace_id, "flow_key": flow_key, "result": result}
