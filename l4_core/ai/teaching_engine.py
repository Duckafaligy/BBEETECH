# l4_core/ai/teaching_engine.py

"""
Teaching Engine (L4+)
---------------------
The self-improving layer of the AI OS.

Learns from:
  - sandbox failures
  - code diffs
  - error patterns
  - fix patterns
  - engine performance
  - workspace analytics
  - IR patterns (future)
  - user corrections (future)

Updates:
  - error → fix mappings
  - engine performance stats
  - workspace analytics
  - code diff history
  - pattern memory
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from l4_core.db.models import (
    ErrorPattern,
    FixPattern,
    CodeDiff,
    ArtifactVersion,
    CodeSandboxRun,
    EnginePerformance,
    WorkspaceAnalytics,
)
from l4_core.utils.logging import log_engine_event, generate_trace_id


class TeachingEngine:
    """
    Central learning subsystem for the AI OS.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ---------------------------------------------------------
    # PUBLIC ENTRYPOINTS
    # ---------------------------------------------------------

    async def learn_from_sandbox(self, sandbox_run: CodeSandboxRun):
        """
        Learn from a sandbox execution (success or failure).
        """

        trace_id = generate_trace_id()

        if sandbox_run.status == "failed":
            await self._record_error_pattern(sandbox_run, trace_id)

        await self._update_engine_performance(sandbox_run, trace_id)
        await self._update_workspace_analytics(sandbox_run.workspace_id, trace_id)

        log_engine_event(
            engine="teaching-engine",
            message="Sandbox learning complete",
            trace_id=trace_id,
            extra={"sandbox_status": sandbox_run.status},
        )

    async def learn_from_diff(
        self,
        artifact_version: ArtifactVersion,
        before: str,
        after: str,
        diff: str,
    ):
        """
        Learn from code diffs (user corrections or AI retries).
        """

        trace_id = generate_trace_id()

        diff_row = CodeDiff(
            id=trace_id,
            artifact_version_id=artifact_version.id,
            before=before,
            after=after,
            diff=diff,
        )
        self.db.add(diff_row)
        await self.db.commit()

        log_engine_event(
            engine="teaching-engine",
            message="Recorded code diff",
            trace_id=trace_id,
            extra={"artifact_version_id": artifact_version.id},
        )

    async def learn_fix_for_error(
        self,
        error_pattern_id: str,
        fix_description: str,
        fix_code: Optional[str] = None,
    ):
        """
        Store a fix pattern for a known error pattern.
        """

        trace_id = generate_trace_id()

        fix = FixPattern(
            id=trace_id,
            error_pattern_id=error_pattern_id,
            fix_description=fix_description,
            fix_code=fix_code,
        )
        self.db.add(fix)
        await self.db.commit()

        log_engine_event(
            engine="teaching-engine",
            message="Stored fix pattern",
            trace_id=trace_id,
            extra={"error_pattern_id": error_pattern_id},
        )

    # ---------------------------------------------------------
    # INTERNAL: ERROR PATTERN LEARNING
    # ---------------------------------------------------------

    async def _record_error_pattern(
        self,
        sandbox_run: CodeSandboxRun,
        trace_id: str,
    ) -> str:
        """
        Extract and store an error pattern from a sandbox failure.
        """

        signature = self._hash_error(
            sandbox_run.error_class or "UnknownError",
            sandbox_run.error_message or "",
        )

        # Check if pattern already exists
        result = await self.db.execute(
            select(ErrorPattern).where(ErrorPattern.signature == signature)
        )
        existing = result.scalars().first()

        if existing:
            log_engine_event(
                engine="teaching-engine",
                message="Error pattern already known",
                trace_id=trace_id,
                extra={"signature": signature},
            )
            return existing.id

        # Create new error pattern
        pattern = ErrorPattern(
            id=generate_trace_id(),
            error_class=sandbox_run.error_class or "UnknownError",
            signature=signature,
            metadata={
                "message": sandbox_run.error_message,
                "stderr": sandbox_run.stderr,
                "exit_code": sandbox_run.exit_code,
            },
        )
        self.db.add(pattern)
        await self.db.commit()

        log_engine_event(
            engine="teaching-engine",
            message="Recorded new error pattern",
            trace_id=trace_id,
            extra={"signature": signature},
        )

        return pattern.id

    def _hash_error(self, error_class: str, error_message: str) -> str:
        """
        Create a stable hash for an error signature.
        """

        raw = f"{error_class}:{error_message}"
        return hashlib.sha256(raw.encode()).hexdigest()

    # ---------------------------------------------------------
    # INTERNAL: ENGINE PERFORMANCE LEARNING
    # ---------------------------------------------------------

    async def _update_engine_performance(
        self,
        sandbox_run: CodeSandboxRun,
        trace_id: str,
    ):
        """
        Update engine performance stats based on sandbox results.
        """

        provider, model = self._extract_engine_from_metadata(sandbox_run)

        # Fetch or create performance row
        result = await self.db.execute(
            select(EnginePerformance).where(
                EnginePerformance.provider == provider,
                EnginePerformance.model == model,
            )
        )
        perf = result.scalars().first()

        if not perf:
            perf = EnginePerformance(
                id=generate_trace_id(),
                provider=provider,
                model=model,
                total_calls=0,
                total_failures=0,
                avg_latency_ms=0,
            )
            self.db.add(perf)

        # Update stats
        perf.total_calls += 1
        if sandbox_run.status == "failed":
            perf.total_failures += 1

        # Update latency
        if sandbox_run.started_at and sandbox_run.finished_at:
            latency = (
                sandbox_run.finished_at - sandbox_run.started_at
            ).total_seconds() * 1000
            perf.avg_latency_ms = (perf.avg_latency_ms + latency) / 2

        await self.db.commit()

        log_engine_event(
            engine="teaching-engine",
            message="Updated engine performance",
            trace_id=trace_id,
            extra={"provider": provider, "model": model},
        )

    def _extract_engine_from_metadata(self, sandbox_run: CodeSandboxRun):
        """
        Extract provider/model from sandbox metadata.
        """

        meta = sandbox_run.error_metadata or {}
        provider = meta.get("provider", "unknown")
        model = meta.get("model", "unknown")
        return provider, model

    # ---------------------------------------------------------
    # INTERNAL: WORKSPACE ANALYTICS
    # ---------------------------------------------------------

    async def _update_workspace_analytics(
        self,
        workspace_id: str,
        trace_id: str,
    ):
        """
        Update workspace analytics after each sandbox run.
        """

        result = await self.db.execute(
            select(WorkspaceAnalytics).where(
                WorkspaceAnalytics.workspace_id == workspace_id
            )
        )
        analytics = result.scalars().first()

        if not analytics:
            analytics = WorkspaceAnalytics(
                id=generate_trace_id(),
                workspace_id=workspace_id,
                total_flows_run=0,
                total_artifacts_created=0,
                total_errors=0,
            )
            self.db.add(analytics)

        analytics.total_errors += 1
        analytics.updated_at = datetime.utcnow()

        await self.db.commit()

        log_engine_event(
            engine="teaching-engine",
            message="Updated workspace analytics",
            trace_id=trace_id,
            extra={"workspace_id": workspace_id},
        )
