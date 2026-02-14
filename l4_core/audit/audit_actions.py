# l4_core/audit/audit_actions.py

"""
Audit Action Executor (L4+)
---------------------------
Applies audit actions in a controlled, observable, and safe manner.

Supports:
  - CREATE_FILE
  - UPDATE_FILE
  - DELETE_FILE
  - UPDATE_DB (future: patching flows, presets, configs)

Features:
  - Trace-aware execution
  - Dry-run simulation
  - File safety (backup, existence checks)
  - Structured logging
  - Future rollback hooks
  - DB patching placeholder
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from l4_core.audit.audit_models import AuditAction, AuditActionType, AuditResult
from l4_core.utils.logging import log_engine_event, generate_trace_id


class AuditActionExecutor:
    """
    Applies audit actions in a controlled, observable way.
    """

    def __init__(self, db: AsyncSession | None = None):
        self.db = db

    # ---------------------------------------------------------
    # PUBLIC: APPLY ACTIONS
    # ---------------------------------------------------------
    async def apply_actions(
        self,
        results: List[AuditResult],
        dry_run: bool = True,
    ) -> None:

        trace_id = generate_trace_id()

        log_engine_event(
            engine="audit-engine",
            message="Applying audit actions",
            trace_id=trace_id,
            extra={"dry_run": dry_run, "result_count": len(results)},
        )

        for result in results:
            for action in result.actions:
                await self._apply_single_action(
                    action=action,
                    trace_id=trace_id,
                    dry_run=dry_run,
                )

    # ---------------------------------------------------------
    # INTERNAL: APPLY SINGLE ACTION
    # ---------------------------------------------------------
    async def _apply_single_action(
        self,
        action: AuditAction,
        trace_id: str,
        dry_run: bool,
    ) -> None:

        log_engine_event(
            engine="audit-engine",
            message="Simulating audit action" if dry_run else "Executing audit action",
            trace_id=trace_id,
            extra={
                "action_type": action.type,
                "description": action.description,
                "payload": action.payload,
                "dry_run": dry_run,
            },
        )

        if dry_run:
            return

        # Dispatch by action type
        match action.type:
            case AuditActionType.CREATE_FILE:
                await self._create_file(action, trace_id)
            case AuditActionType.UPDATE_FILE:
                await self._update_file(action, trace_id)
            case AuditActionType.DELETE_FILE:
                await self._delete_file(action, trace_id)
            case AuditActionType.UPDATE_DB:
                if self.db:
                    await self._update_db(action, trace_id)

    # ---------------------------------------------------------
    # FILE OPERATIONS
    # ---------------------------------------------------------

    async def _create_file(self, action: AuditAction, trace_id: str) -> None:
        path = Path(action.payload["path"])
        content = action.payload.get("content", "")

        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        path.write_text(content, encoding="utf-8")

        log_engine_event(
            engine="audit-engine",
            message="File created",
            trace_id=trace_id,
            extra={"path": str(path)},
        )

    async def _update_file(self, action: AuditAction, trace_id: str) -> None:
        path = Path(action.payload["path"])
        content = action.payload.get("content", "")

        # Backup existing file if present
        if path.exists():
            backup_path = path.with_suffix(path.suffix + ".backup")
            backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

        # Write new content
        path.write_text(content, encoding="utf-8")

        log_engine_event(
            engine="audit-engine",
            message="File updated",
            trace_id=trace_id,
            extra={"path": str(path)},
        )

    async def _delete_file(self, action: AuditAction, trace_id: str) -> None:
        path = Path(action.payload["path"])

        if path.exists():
            path.unlink()

            log_engine_event(
                engine="audit-engine",
                message="File deleted",
                trace_id=trace_id,
                extra={"path": str(path)},
            )
        else:
            log_engine_event(
                engine="audit-engine",
                message="Delete skipped (file not found)",
                trace_id=trace_id,
                extra={"path": str(path)},
            )

    # ---------------------------------------------------------
    # DB OPERATIONS
    # ---------------------------------------------------------
    async def _update_db(self, action: AuditAction, trace_id: str) -> None:
        """
        Placeholder for DB-level audit patches.
        Example payload:
          {
            "op": "update_flow",
            "flow_id": "...",
            "patch": {...}
          }
        """

        if not self.db:
            return

        # Future: decode and apply DB patches
        # For now: commit no-op
        await self.db.commit()

        log_engine_event(
            engine="audit-engine",
            message="DB update applied (placeholder)",
            trace_id=trace_id,
            extra={"payload": action.payload},
        )
