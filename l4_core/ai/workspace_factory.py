# l4_core/ai/workspace_factory.py

"""
Workspace Factory (L4+)
-----------------------
Creates a fully initialized workspace with:
  - Workspace row
  - Engine configs
  - Flow definitions
  - Analytics row
  - Future: default artifacts, IR templates, pages, dashboards

This module is trace-aware, audit-ready, and consistent with the
L4+ architecture across FlowEngine, RuntimeEngine, AIRouter, etc.
"""

from __future__ import annotations

from typing import Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from l4_core.db.models import (
    Workspace,
    WorkspaceEngineConfig,
    FlowDefinition,
    WorkspaceAnalytics,
)
from l4_core.utils.logging import log_engine_event, generate_trace_id

# Industry presets
from l4_core.industries.software_dev import SOFTWARE_DEV_PRESET
from l4_core.industries.game_dev import GAME_DEV_PRESET
from l4_core.industries.web_dev import WEB_DEV_PRESET
from l4_core.industries.app_dev import APP_DEV_PRESET
from l4_core.industries.graphics_3d import GRAPHICS_3D_PRESET
from l4_core.industries.physics_sim import PHYSICS_SIM_PRESET


INDUSTRY_MAP = {
    "software_dev": SOFTWARE_DEV_PRESET,
    "game_dev": GAME_DEV_PRESET,
    "web_dev": WEB_DEV_PRESET,
    "app_dev": APP_DEV_PRESET,
    "graphics_3d": GRAPHICS_3D_PRESET,
    "physics_sim": PHYSICS_SIM_PRESET,
}


class WorkspaceFactory:
    """
    Creates a fully initialized workspace.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ---------------------------------------------------------
    # PUBLIC ENTRYPOINT
    # ---------------------------------------------------------
    async def create_workspace(
        self,
        name: str,
        workspace_type: str,
        owner_id: str | None = None,
        settings: Dict[str, Any] | None = None,
    ) -> Workspace:

        trace_id = generate_trace_id()

        # Validate workspace type
        if workspace_type not in INDUSTRY_MAP:
            raise ValueError(f"Unknown workspace type: {workspace_type}")

        preset = INDUSTRY_MAP[workspace_type]

        log_engine_event(
            engine="workspace-factory",
            message="Workspace initialization started",
            trace_id=trace_id,
            extra={"workspace_type": workspace_type, "name": name},
        )

        # -----------------------------------------------------
        # CREATE WORKSPACE
        # -----------------------------------------------------
        workspace = Workspace(
            id=generate_trace_id(),
            name=name,
            owner_id=owner_id,
            workspace_type=workspace_type,
            settings=settings or {},
            created_at=datetime.utcnow(),
        )
        self.db.add(workspace)
        await self.db.commit()

        # -----------------------------------------------------
        # ENGINE CONFIGS
        # -----------------------------------------------------
        for engine_cfg in preset.get("engines", []):
            cfg = WorkspaceEngineConfig(
                id=generate_trace_id(),
                workspace_id=workspace.id,
                provider=engine_cfg["provider"],
                model=engine_cfg["model"],
                label=engine_cfg.get("label"),
                enabled=engine_cfg.get("enabled", True),
                priority=engine_cfg.get("priority", 1),
                allow_fallback=engine_cfg.get("allow_fallback", True),
            )
            self.db.add(cfg)

        await self.db.commit()

        # -----------------------------------------------------
        # FLOWS
        # -----------------------------------------------------
        for flow_def in preset.get("flows", []):
            flow = FlowDefinition(
                id=generate_trace_id(),
                workspace_id=workspace.id,
                key=flow_def["key"],
                label=flow_def["label"],
                description=flow_def.get("description"),
                definition=flow_def.get("definition", {}),
                created_at=datetime.utcnow(),
            )
            self.db.add(flow)

        await self.db.commit()

        # -----------------------------------------------------
        # ANALYTICS ROW
        # -----------------------------------------------------
        analytics = WorkspaceAnalytics(
            id=generate_trace_id(),
            workspace_id=workspace.id,
            total_flows_run=0,
            total_artifacts_created=0,
            total_errors=0,
            metadata={},
        )
        self.db.add(analytics)
        await self.db.commit()

        # -----------------------------------------------------
        # FUTURE: DEFAULT ARTIFACTS, PAGES, IR TEMPLATES
        # -----------------------------------------------------
        # (Reserved for L5+ workspace initialization)
        # e.g.:
        #   - default dashboards
        #   - starter artifacts
        #   - IR templates
        #   - pattern seeds

        log_engine_event(
            engine="workspace-factory",
            message="Workspace fully initialized",
            trace_id=trace_id,
            extra={"workspace_id": workspace.id},
        )

        return workspace
