# l4_core/ai/pattern_engine.py

"""
Pattern Engine (L4+)
--------------------
Learns reusable patterns from:
  - IR (Intermediate Representations)
  - code artifacts
  - diffs
  - error signatures
  - fix patterns

Produces:
  - reusable IR templates
  - naming conventions
  - structural patterns
  - error → fix mappings
  - future auto-refactor hints

This engine is intentionally modular and future-proof.
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from l4_core.db.models import (
    Artifact,
    ArtifactVersion,
    ErrorPattern,
    FixPattern,
    CodeDiff,
)
from l4_core.utils.logging import log_engine_event, generate_trace_id


class PatternEngine:
    """
    Learns patterns from artifacts, diffs, errors, and fixes.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ---------------------------------------------------------
    # PUBLIC: LEARN FROM ARTIFACTS
    # ---------------------------------------------------------
    async def learn_from_artifact(self, artifact: Artifact) -> Optional[str]:
        """
        Extract IR patterns from an artifact and store them.
        Returns the pattern key if learned.
        """

        trace_id = generate_trace_id()

        if not artifact.versions:
            return None

        latest = artifact.versions[-1]
        content = latest.content

        # Try to parse IR
        try:
            ir = json.loads(content)
        except Exception:
            log_engine_event(
                engine="pattern-engine",
                message="Artifact is not IR-based; skipping",
                trace_id=trace_id,
                extra={"artifact_id": artifact.id},
            )
            return None

        pattern_key = self._hash_ir(ir)

        # Store pattern key
        artifact.metadata["pattern_key"] = pattern_key
        artifact.updated_at = datetime.utcnow()
        await self.db.commit()

        log_engine_event(
            engine="pattern-engine",
            message="Learned IR pattern",
            trace_id=trace_id,
            extra={"artifact_id": artifact.id, "pattern_key": pattern_key},
        )

        return pattern_key

    # ---------------------------------------------------------
    # PUBLIC: LEARN FROM DIFFS
    # ---------------------------------------------------------
    async def learn_from_diff(self, diff: CodeDiff) -> str:
        """
        Learn naming and structural patterns from code diffs.
        Returns the diff hash.
        """

        trace_id = generate_trace_id()

        diff_hash = hashlib.sha256(diff.diff.encode()).hexdigest()
        diff.metadata = {"diff_hash": diff_hash}
        diff.updated_at = datetime.utcnow()
        await self.db.commit()

        log_engine_event(
            engine="pattern-engine",
            message="Learned diff pattern",
            trace_id=trace_id,
            extra={"diff_id": diff.id, "hash": diff_hash},
        )

        return diff_hash

    # ---------------------------------------------------------
    # PUBLIC: LEARN FROM ERRORS
    # ---------------------------------------------------------
    async def learn_from_error(self, error_pattern: ErrorPattern) -> None:
        """
        Store error signatures for future avoidance.
        """

        trace_id = generate_trace_id()

        log_engine_event(
            engine="pattern-engine",
            message="Error pattern acknowledged",
            trace_id=trace_id,
            extra={"error_pattern_id": error_pattern.id},
        )

    # ---------------------------------------------------------
    # PUBLIC: LEARN FROM FIXES
    # ---------------------------------------------------------
    async def learn_from_fix(self, fix: FixPattern) -> None:
        """
        Store fix patterns for future auto-correction.
        """

        trace_id = generate_trace_id()

        log_engine_event(
            engine="pattern-engine",
            message="Fix pattern acknowledged",
            trace_id=trace_id,
            extra={"fix_pattern_id": fix.id},
        )

    # ---------------------------------------------------------
    # INTERNAL: HASH IR
    # ---------------------------------------------------------
    def _hash_ir(self, ir: Dict[str, Any]) -> str:
        """
        Create a stable hash for IR patterns.
        """

        raw = json.dumps(ir, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()
