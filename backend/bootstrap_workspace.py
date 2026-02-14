# backend/bootstrap_workspace.py

from __future__ import annotations

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession

from l4_core.db.core import init_db, AsyncSessionLocal
from l4_core.ai.workspace_factory import WorkspaceFactory
from l4_core.audit.audit_orchestrator import AuditOrchestrator
from l4_core.utils.logging import log_engine_event, generate_trace_id


async def create_workspace(
    name: str,
    workspace_type: str,
    owner_id: str = "system",
    run_audit: bool = True,
) -> str:
    trace_id = generate_trace_id()

    await init_db()

    async with AsyncSessionLocal() as db:
        factory = WorkspaceFactory(db)
        workspace = await factory.create_workspace(
            name=name,
            workspace_type=workspace_type,
            owner_id=owner_id,
        )

        log_engine_event(
            engine="bootstrap",
            message="Workspace created",
            trace_id=trace_id,
            extra={"workspace_id": workspace.id, "workspace_type": workspace_type},
        )

        if run_audit:
            auditor = AuditOrchestrator(db)
            await auditor.audit_workspace_flows(workspace.id, apply_fixes=False)

            log_engine_event(
                engine="bootstrap",
                message="Workspace audit complete",
                trace_id=trace_id,
                extra={"workspace_id": workspace.id},
            )

        return workspace.id


async def main():
    workspace_id = await create_workspace(
        name="Software Dev Demo",
        workspace_type="software_dev",
        owner_id="brendan",
        run_audit=True,
    )
    print("Workspace ID:", workspace_id)


if __name__ == "__main__":
    asyncio.run(main())
