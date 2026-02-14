# l4_core/flows/router.py

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from l4_core.db.core import get_db
from l4_core.ai.flow_engine import FlowEngine
from l4_core.ai.workspace_factory import WorkspaceFactory

router = APIRouter()


@router.get("/list")
async def list_flows(workspace_id: str, db=Depends(get_db)):
    """
    List available flows for a workspace.
    """
    factory = WorkspaceFactory(db)
    workspace = await factory.get_workspace(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    engine = FlowEngine(db, workspace=workspace)
    flows = await engine.list_flows()
    return {"workspace_id": workspace_id, "flows": flows}


@router.post("/run")
async def run_flow(payload: dict, db=Depends(get_db)):
    """
    Execute a specific flow with inputs.
    """
    workspace_id = payload.get("workspace_id")
    flow_key = payload.get("flow_key")
    inputs = payload.get("inputs", {})

    factory = WorkspaceFactory(db)
    workspace = await factory.get_workspace(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    engine = FlowEngine(db, workspace=workspace)
    result = await engine.run_flow(flow_key=flow_key, inputs=inputs)

    return {"workspace_id": workspace_id, "flow_key": flow_key, "result": result}
