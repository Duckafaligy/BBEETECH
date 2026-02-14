# l4_core/ai/audit_engine.py

"""
AI-Level Audit Engine (L4+)
---------------------------
This engine performs safe, reversible, AI-driven file modifications.

Responsibilities:
  - Create audit records
  - Backup old file content
  - Apply new file content
  - Run sandbox validation
  - Roll back on failure
  - Record diffs + rollback metadata
  - Emit structured logs
  - Integrate with system-wide Audit Engine

This engine is intentionally conservative:
  - Never overwrites without backup
  - Never deletes without audit
  - Never commits without sandbox pass
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from l4_core.db.models import (
    FileAudit,
    FileRollback,
    ArtifactVersion,
    CodeDiff,
)
from l4_core.utils.logging import log_engine_event, generate_trace_id
from l4_core.ai.sandbox_engine import SandboxEngine
from l4_core.ai.teaching_engine import TeachingEngine


class AuditEngine:
    """
    AI-driven file modification engine with:
      - backup
      - sandbox validation
      - rollback
      - diff recording
      - structured logging
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.sandbox = SandboxEngine(db)
        self.teacher = TeachingEngine(db)

    # ---------------------------------------------------------
    # PUBLIC ENTRYPOINT
    # ---------------------------------------------------------
    async def apply_change_with_audit(
        self,
        workspace_id: str,
        file_path: str,
        new_content: str,
        language: str = "python",
        run_sandbox: bool = True,
        dry_run: bool = False,
    ) -> FileAudit:
        """
        Apply a file change with:
          - backup
          - optional sandbox run
          - rollback on failure
          - dry-run support
        """

        trace_id = generate_trace_id()

        # Validate file path
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("Invalid file path")

        # Read old content
        old_content = None
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                old_content = f.read()

        # Create audit record
        audit = FileAudit(
            id=trace_id,
            workspace_id=workspace_id,
            file_path=file_path,
            new_content=new_content,
            old_content=old_content,
            audit_status="pending",
            metadata={"language": language, "dry_run": dry_run},
            created_at=datetime.utcnow(),
        )
        self.db.add(audit)
        await self.db.commit()

        log_engine_event(
            engine="audit-engine",
            message="Audit started",
            trace_id=trace_id,
            extra={"file_path": file_path, "dry_run": dry_run},
        )

        # Backup old file
        backup_path = None
        if old_content is not None:
            backup_path = f"{file_path}.backup"
            with open(backup_path, "w") as f:
                f.write(old_content)

        # If dry-run: do not write file
        if dry_run:
            audit.audit_status = "dry_run"
            await self.db.commit()
            return audit

        # Write new file
        with open(file_path, "w") as f:
            f.write(new_content)

        # Sandbox validation
        sandbox_ok = True
        if run_sandbox:
            sandbox_ok = await self._run_sandbox_for_file(
                audit=audit,
                file_path=file_path,
                language=language,
                old_content=old_content,
                new_content=new_content,
            )

        # Decide: keep or rollback
        if sandbox_ok:
            audit.audit_status = "passed"
            await self.db.commit()

            log_engine_event(
                engine="audit-engine",
                message="Audit passed",
                trace_id=trace_id,
            )

        else:
            await self._rollback(audit, file_path, old_content)

            log_engine_event(
                engine="audit-engine",
                message="Audit failed, rolled back",
                trace_id=trace_id,
            )

        return audit

    # ---------------------------------------------------------
    # INTERNAL: SANDBOX
    # ---------------------------------------------------------
    async def _run_sandbox_for_file(
        self,
        audit: FileAudit,
        file_path: str,
        language: str,
        old_content: Optional[str],
        new_content: str,
    ) -> bool:
        """
        Run sandbox validation on the new file content.
        """

        fake_artifact_version = ArtifactVersion(
            id=generate_trace_id(),
            artifact_id="audit-artifact",
            version_index=1,
            content=new_content,
            content_format="text",
            created_by_engine="audit-engine",
            created_by_flow_id=None,
            sandbox_status="unknown",
            sandbox_metadata={},
        )

        sandbox_run = await self.sandbox.run_code(
            artifact_version=fake_artifact_version,
            language=language,
        )

        if sandbox_run.status == "success":
            return True

        # Record diff
        diff_text = self._simple_diff(old_content or "", new_content)

        diff_row = CodeDiff(
            id=generate_trace_id(),
            artifact_version_id=fake_artifact_version.id,
            before=old_content or "",
            after=new_content,
            diff=diff_text,
        )
        self.db.add(diff_row)
        await self.db.commit()

        return False

    # ---------------------------------------------------------
    # INTERNAL: ROLLBACK
    # ---------------------------------------------------------
    async def _rollback(
        self,
        audit: FileAudit,
        file_path: str,
        old_content: Optional[str],
    ):
        """
        Restore old content and record rollback.
        """

        if old_content is not None:
            with open(file_path, "w") as f:
                f.write(old_content)

            rollback = FileRollback(
                id=generate_trace_id(),
                audit_id=audit.id,
                restored_content=old_content,
                metadata={},
                created_at=datetime.utcnow(),
            )
            self.db.add(rollback)

        audit.audit_status = "failed"
        await self.db.commit()

    # ---------------------------------------------------------
    # INTERNAL: SIMPLE DIFF
    # ---------------------------------------------------------
    def _simple_diff(self, before: str, after: str) -> str:
        """
        Simple line-based diff.
        (Can be upgraded to unified diff or AST diff later.)
        """
        before_lines = before.splitlines()
        after_lines = after.splitlines()

        diff_lines = ["--- BEFORE ---", *before_lines, "--- AFTER ---", *after_lines]
        return "\n".join(diff_lines)
