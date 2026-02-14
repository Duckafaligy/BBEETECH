# l4_core/ai/runtime_engine.py

"""
Runtime Engine (L4+)
--------------------
High-level orchestrator for executing flows with:
  - retries
  - fallback chains (future)
  - pattern-aware recovery (future)
  - audit-aware execution (future)
  - trace propagation
  - structured logging

This engine wraps FlowEngine and centralizes execution policy.
"""

from __future__ import annotations

from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from l4_core.ai.router import AIRouter
from l4_core.ai.flow_engine import FlowEngine
from l4_core.utils.logging import log_engine_event, generate_trace_id
from l4_core.db.models import FlowDefinition


class RuntimeEngine:
    """
    High-level orchestrator for running flows with retries and future fallbacks.
    """

    def __init__(
        self,
        db: AsyncSession,
        ai_router: AIRouter,
        max_retries: int = 1,
    ):
        self.db = db
        self.ai_router = ai_router
        self.flow_engine = FlowEngine(db=db, ai_router=ai_router)
        self.max_retries = max_retries

    # ---------------------------------------------------------
    # PUBLIC: RUN FLOW BY KEY
    # ---------------------------------------------------------
    async def run_flow_by_key(
        self,
        workspace_id: str,
        flow_key: str,
        user_input: Dict[str, Any],
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Look up a FlowDefinition by key and execute it with retries.
        """

        trace_id = trace_id or generate_trace_id()

        flow = await self._get_flow_definition(workspace_id, flow_key)
        if not flow:
            log_engine_event(
                engine="runtime-engine",
                message="Flow not found",
                trace_id=trace_id,
                extra={"workspace_id": workspace_id, "flow_key": flow_key},
            )
            raise RuntimeError(f"Flow '{flow_key}' not found for workspace {workspace_id}.")

        log_engine_event(
            engine="runtime-engine",
            message="Runtime flow execution started",
            trace_id=trace_id,
            extra={"workspace_id": workspace_id, "flow_key": flow_key},
        )

        attempt = 0
        last_error: Optional[str] = None

        while attempt <= self.max_retries:
            attempt += 1

            try:
                result = await self.flow_engine.run_flow(
                    flow=flow,
                    workspace_id=workspace_id,
                    user_input=user_input,
                )

                if result.get("status") == "success":
                    log_engine_event(
                        engine="runtime-engine",
                        message="Runtime flow execution succeeded",
                        trace_id=trace_id,
                        extra={"attempt": attempt},
                    )
                    return {
                        "status": "success",
                        "attempts": attempt,
                        "flow_id": result.get("flow_id"),
                        "flow_run_id": result.get("flow_run_id"),
                        "outputs": result.get("outputs"),
                        "trace_id": trace_id,
                    }

                # FlowEngine returned failure
                last_error = result.get("error")
                log_engine_event(
                    engine="runtime-engine",
                    message="FlowEngine reported failure",
                    trace_id=trace_id,
                    extra={"attempt": attempt, "error": last_error},
                )

            except Exception as e:
                last_error = str(e)
                log_engine_event(
                    engine="runtime-engine",
                    message="Runtime flow execution error",
                    trace_id=trace_id,
                    extra={"attempt": attempt, "error": last_error},
                )

            # Retry logic
            if attempt <= self.max_retries:
                log_engine_event(
                    engine="runtime-engine",
                    message="Retrying flow execution",
                    trace_id=trace_id,
                    extra={"next_attempt": attempt + 1},
                )

        # All attempts failed
        log_engine_event(
            engine="runtime-engine",
            message="Runtime flow execution exhausted retries",
            trace_id=trace_id,
            extra={"max_retries": self.max_retries, "last_error": last_error},
        )

        return {
            "status": "failed",
            "attempts": attempt,
            "flow_id": flow.id,
            "error": last_error or "Unknown error",
            "trace_id": trace_id,
        }

    # ---------------------------------------------------------
    # INTERNAL: LOOKUP FLOW
    # ---------------------------------------------------------
    async def _get_flow_definition(
        self,
        workspace_id: str,
        flow_key: str,
    ) -> Optional[FlowDefinition]:
        stmt = (
            select(FlowDefinition)
            .where(
                FlowDefinition.workspace_id == workspace_id,
                FlowDefinition.key == flow_key,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()
