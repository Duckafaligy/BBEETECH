# l4_core/audit/audit_orchestrator.py

"""
Audit Orchestrator (L4+)
------------------------
High-level orchestrator that:
  - Collects audit targets from DB and code
  - Invokes the AuditEngine
  - Provides workspace-wide and industry-wide audit entrypoints
  - Future: CLI / API integration, scheduled audits, dashboards
"""

from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from l4_core.audit.audit_models import AuditTarget, AuditTargetType
from l4_core.audit.audit_engine import AuditEngine
from l4_core.db.models import FlowDefinition
from l4_core.ai.workspace_factory import INDUSTRY_MAP
from l4_core.utils.logging import log_engine_event, generate_trace_id
from l4_core.db.models import Workspace



class AuditOrchestrator:
    """
    High-level orchestrator for collecting audit targets and invoking the AuditEngine.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.engine = AuditEngine(db=db)

    # ---------------------------------------------------------
    # WORKSPACE FLOW AUDIT
    # ---------------------------------------------------------
    async def audit_workspace_flows(
        self,
        workspace_id: str,
        apply_fixes: bool = False,
        dry_run: bool = True,
    ) -> None:

        trace_id = generate_trace_id()

        log_engine_event(
            engine="audit-orchestrator",
            message="Collecting workspace flow targets",
            trace_id=trace_id,
            extra={"workspace_id": workspace_id},
        )

        result = await self.db.execute(
            select(FlowDefinition).where(FlowDefinition.workspace_id == workspace_id)
        )
        flows = result.scalars().all()

        targets: List[AuditTarget] = []

        for f in flows:
            targets.append(
                AuditTarget(
                    type=AuditTargetType.FLOW,
                    identifier=f"{workspace_id}:{f.key}",
                    metadata={
                        "workspace_id": workspace_id,
                        "flow_id": f.id,
                        "key": f.key,
                        "definition": f.definition,
                    },
                )
            )

        log_engine_event(
            engine="audit-orchestrator",
            message="Invoking audit engine for workspace flows",
            trace_id=trace_id,
            extra={"target_count": len(targets)},
        )

        await self.engine.audit_targets(
            scope=f"workspace:{workspace_id}:flows",
            targets=targets,
            apply_fixes=apply_fixes,
            dry_run=dry_run,
        )

    # ---------------------------------------------------------
    # INDUSTRY PRESET AUDIT
    # ---------------------------------------------------------
    async def audit_industry_presets(
        self,
        apply_fixes: bool = False,
        dry_run: bool = True,
    ) -> None:

        trace_id = generate_trace_id()

        log_engine_event(
            engine="audit-orchestrator",
            message="Collecting industry preset targets",
            trace_id=trace_id,
            extra={"industry_count": len(INDUSTRY_MAP)},
        )

        targets: List[AuditTarget] = []

        for name, preset in INDUSTRY_MAP.items():
            targets.append(
                AuditTarget(
                    type=AuditTargetType.PRESET,
                    identifier=name,
                    metadata={
                        "name": name,
                        "preset": preset,
                    },
                )
            )

        log_engine_event(
            engine="audit-orchestrator",
            message="Invoking audit engine for industry presets",
            trace_id=trace_id,
            extra={"target_count": len(targets)},
        )

        await self.engine.audit_targets(
            scope="industries:presets",
            targets=targets,
            apply_fixes=apply_fixes,
            dry_run=dry_run,
        )


    # ---------------------------------------------------------
    # AUDIT ALL WORKSPACES
    # ---------------------------------------------------------
    async def audit_all_workspaces(self, apply_fixes: bool = False, dry_run: bool = True):
        from l4_core.db.models import Workspace
        from sqlalchemy import select

        trace_id = generate_trace_id()

        # FIX: reset failed transaction state
        await self.db.rollback()

        result = await self.db.execute(select(Workspace))
        workspaces = result.scalars().all()

        log_engine_event(
            engine="audit-orchestrator",
            message="Auditing all workspaces",
            trace_id=trace_id,
            extra={"workspace_count": len(workspaces)},
        )

        for ws in workspaces:
            await self.audit_workspace_flows(
                workspace_id=ws.id,
                apply_fixes=apply_fixes,
                dry_run=dry_run,
            )

