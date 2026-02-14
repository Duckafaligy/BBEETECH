# l4_core/pages/router.py

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from l4_core.db.core import get_db
from l4_core.ai.page_engine import PageEngine
from l4_core.ai.workspace_factory import WorkspaceFactory

router = APIRouter()


@router.get("/definition")
async def get_page_definition(workspace_id: str, page_key: str, db=Depends(get_db)):
    """
    Return page IR for a given workspace + page key.
    """
    factory = WorkspaceFactory(db)
    workspace = await factory.get_workspace(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    engine = PageEngine(db, workspace=workspace)
    page_ir = await engine.get_page_ir(page_key=page_key)

    return {"workspace_id": workspace_id, "page_key": page_key, "page_ir": page_ir}


@router.post("/render")
async def render_page(payload: dict, db=Depends(get_db)):
    """
    Render a page IR into a concrete UI description for the frontend.
    """
    workspace_id = payload.get("workspace_id")
    page_key = payload.get("page_key")
    state = payload.get("state", {})

    factory = WorkspaceFactory(db)
    workspace = await factory.get_workspace(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    engine = PageEngine(db, workspace=workspace)
    rendered = await engine.render_page(page_key=page_key, state=state)

    return {
        "workspace_id": workspace_id,
        "page_key": page_key,
        "rendered": rendered,
    }
