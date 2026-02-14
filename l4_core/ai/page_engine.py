# l4_core/ai/page_engine.py

"""
Page Engine (L4+)
-----------------
Resolves page definitions into structured Page IR for the frontend.

Responsibilities:
  - Load page definitions from industry presets
  - Resolve widgets dynamically
  - Fetch data for each widget
  - Emit trace-aware logs
  - Provide consistent IR for the frontend cockpit
  - Future-proof for interactive widgets, caching, and analytics
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from l4_core.db.models import (
    Workspace,
    FlowDefinition,
    FlowRun,
    Artifact,
    ArtifactVersion,
    WorkspaceAnalytics,
)
from l4_core.utils.logging import log_engine_event, generate_trace_id


class PageEngine:
    """
    Converts page definitions into structured Page IR.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ---------------------------------------------------------
    # PUBLIC ENTRYPOINT
    # ---------------------------------------------------------
    async def render_page(
        self,
        workspace: Workspace,
        page_definition: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Render a page into a structured IR.
        """

        trace_id = generate_trace_id()
        page_key = page_definition.get("key")

        log_engine_event(
            engine="page-engine",
            message=f"Rendering page: {page_key}",
            trace_id=trace_id,
            extra={"workspace_id": workspace.id},
        )

        widgets = page_definition.get("widgets", [])
        rendered_widgets = []

        for widget in widgets:
            try:
                rendered = await self._render_widget(workspace, widget, trace_id)
                rendered_widgets.append(rendered)

            except Exception as e:
                # Widget-level failure isolation
                log_engine_event(
                    engine="page-engine",
                    message=f"Widget failed: {widget.get('key')}",
                    trace_id=trace_id,
                    extra={"error": str(e)},
                )
                rendered_widgets.append(
                    {
                        "type": widget.get("type"),
                        "key": widget.get("key"),
                        "error": str(e),
                        "data": None,
                    }
                )

        return {
            "page_key": page_key,
            "page_label": page_definition.get("label"),
            "widgets": rendered_widgets,
            "trace_id": trace_id,
        }

    # ---------------------------------------------------------
    # INTERNAL: RENDER A SINGLE WIDGET
    # ---------------------------------------------------------
    async def _render_widget(
        self,
        workspace: Workspace,
        widget: Dict[str, Any],
        trace_id: str,
    ) -> Dict[str, Any]:

        widget_type = widget.get("type")
        widget_key = widget.get("key")

        log_engine_event(
            engine="page-engine",
            message=f"Rendering widget: {widget_key}",
            trace_id=trace_id,
            extra={"widget_type": widget_type},
        )

        # Dispatch by widget type
        match widget_type:
            case "stat":
                return await self._render_stat(workspace, widget_key, trace_id)
            case "list":
                return await self._render_list(workspace, widget_key, trace_id)
            case "editor":
                return await self._render_editor(workspace, widget_key, trace_id)
            case "output_panel":
                return await self._render_output_panel(workspace, widget_key, trace_id)
            case "chart":
                return await self._render_chart(workspace, widget_key, trace_id)
            case "canvas":
                return await self._render_canvas(workspace, widget_key, trace_id)
            case "control_panel":
                return await self._render_control_panel(workspace, widget_key, trace_id)

        # Unknown widget fallback
        return {
            "type": widget_type,
            "key": widget_key,
            "data": None,
            "warning": "Unknown widget type",
        }

    # ---------------------------------------------------------
    # WIDGET TYPES
    # ---------------------------------------------------------

    async def _render_stat(self, workspace: Workspace, key: str, trace_id: str) -> Dict[str, Any]:
        if key == "total_assets":
            count = await self._count(Artifact, workspace.id)
            return {"type": "stat", "key": key, "value": count}

        if key == "total_shaders":
            count = await self._count_by_type(workspace.id, "shader")
            return {"type": "stat", "key": key, "value": count}

        if key == "recent_runs":
            runs = await self._recent_flow_runs(workspace.id)
            return {"type": "stat", "key": key, "value": len(runs)}

        return {"type": "stat", "key": key, "value": None}

    async def _render_list(self, workspace: Workspace, key: str, trace_id: str) -> Dict[str, Any]:
        if key == "recent_flows":
            flows = await self._recent_flow_runs(workspace.id)
            return {"type": "list", "key": key, "items": flows}

        return {"type": "list", "key": key, "items": []}

    async def _render_editor(self, workspace: Workspace, key: str, trace_id: str) -> Dict[str, Any]:
        return {
            "type": "editor",
            "key": key,
            "initial_value": "",
        }

    async def _render_output_panel(self, workspace: Workspace, key: str, trace_id: str) -> Dict[str, Any]:
        artifact = await self._latest_artifact(workspace.id, key)
        return {
            "type": "output_panel",
            "key": key,
            "content": artifact.get("content") if artifact else None,
        }

    async def _render_chart(self, workspace: Workspace, key: str, trace_id: str) -> Dict[str, Any]:
        analytics = await self._workspace_analytics(workspace.id)
        return {
            "type": "chart",
            "key": key,
            "data": analytics,
        }

    async def _render_canvas(self, workspace: Workspace, key: str, trace_id: str) -> Dict[str, Any]:
        return {
            "type": "canvas",
            "key": key,
            "scene": {},
        }

    async def _render_control_panel(self, workspace: Workspace, key: str, trace_id: str) -> Dict[str, Any]:
        return {
            "type": "control_panel",
            "key": key,
            "controls": [],
        }

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    async def _count(self, model, workspace_id: str) -> int:
        result = await self.db.execute(
            select(model).where(model.workspace_id == workspace_id)
        )
        return len(result.scalars().all())

    async def _count_by_type(self, workspace_id: str, artifact_type: str) -> int:
        result = await self.db.execute(
            select(Artifact).where(
                Artifact.workspace_id == workspace_id,
                Artifact.artifact_type == artifact_type,
            )
        )
        return len(result.scalars().all())

    async def _recent_flow_runs(self, workspace_id: str) -> List[Dict[str, Any]]:
        result = await self.db.execute(
            select(FlowRun)
            .where(FlowRun.workspace_id == workspace_id)
            .order_by(FlowRun.started_at.desc())
            .limit(10)
        )
        runs = result.scalars().all()
        return [
            {
                "id": r.id,
                "status": r.status,
                "started_at": r.started_at.isoformat(),
            }
            for r in runs
        ]

    async def _latest_artifact(self, workspace_id: str, key: str) -> Optional[Dict[str, Any]]:
        result = await self.db.execute(
            select(Artifact)
            .where(
                Artifact.workspace_id == workspace_id,
                Artifact.key == key,
            )
            .order_by(Artifact.updated_at.desc())
        )
        artifact = result.scalars().first()
        if not artifact:
            return None

        version = artifact.versions[-1] if artifact.versions else None
        if not version:
            return None

        return {
            "artifact_id": artifact.id,
            "version_id": version.id,
            "content": version.content,
        }

    async def _workspace_analytics(self, workspace_id: str) -> Dict[str, Any]:
        result = await self.db.execute(
            select(WorkspaceAnalytics).where(
                WorkspaceAnalytics.workspace_id == workspace_id
            )
        )
        analytics = result.scalars().first()
        return analytics.metadata if analytics else {}
