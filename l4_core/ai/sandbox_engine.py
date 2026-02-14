# l4_core/ai/sandbox_engine.py

"""
Sandbox Engine (L4+)
--------------------
Executes generated code in isolated environments.

Supports:
  - Python
  - Node
  - Shell

Captures:
  - stdout
  - stderr
  - exit code
  - error class
  - error message

Integrates with:
  - TeachingEngine (learning from failures)
  - PatternEngine (future)
  - AuditEngine (future)

This engine is intentionally conservative and future-proof.
"""

from __future__ import annotations

import asyncio
import tempfile
import os
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from l4_core.db.models import (
    CodeSandboxRun,
    ArtifactVersion,
)
from l4_core.utils.logging import log_engine_event, generate_trace_id
from l4_core.ai.teaching_engine import TeachingEngine


class SandboxEngine:
    """
    Executes generated code in isolated environments.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.teacher = TeachingEngine(db)

    # ---------------------------------------------------------
    # PUBLIC ENTRYPOINT
    # ---------------------------------------------------------
    async def run_code(
        self,
        artifact_version: ArtifactVersion,
        language: str = "python",
        command: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> CodeSandboxRun:
        """
        Execute code in a sandbox and return the sandbox run row.
        """

        trace_id = trace_id or generate_trace_id()

        # Create sandbox run record
        sandbox_run = CodeSandboxRun(
            id=trace_id,
            artifact_version_id=artifact_version.id,
            workspace_id=artifact_version.artifact.workspace_id,
            environment=language,
            command=command or "",
            status="running",
            started_at=datetime.utcnow(),
        )
        self.db.add(sandbox_run)
        await self.db.commit()

        log_engine_event(
            engine="sandbox-engine",
            message="Sandbox execution started",
            trace_id=trace_id,
            extra={"artifact_version_id": artifact_version.id, "language": language},
        )

        # -----------------------------------------------------
        # EXECUTE CODE
        # -----------------------------------------------------
        try:
            stdout, stderr, exit_code = await self._execute(
                artifact_version=artifact_version,
                language=language,
                command=command,
            )

            sandbox_run.stdout = stdout
            sandbox_run.stderr = stderr
            sandbox_run.exit_code = exit_code

            if exit_code == 0:
                sandbox_run.status = "success"
                artifact_version.sandbox_status = "passed"
            else:
                sandbox_run.status = "failed"
                artifact_version.sandbox_status = "failed"
                sandbox_run.error_class = "RuntimeError"
                sandbox_run.error_message = stderr or "Unknown error"

        except Exception as e:
            sandbox_run.status = "failed"
            artifact_version.sandbox_status = "failed"
            sandbox_run.stderr = str(e)
            sandbox_run.error_class = e.__class__.__name__
            sandbox_run.error_message = str(e)

        sandbox_run.finished_at = datetime.utcnow()
        await self.db.commit()

        # -----------------------------------------------------
        # TEACHING ENGINE LEARNING
        # -----------------------------------------------------
        await self.teacher.learn_from_sandbox(sandbox_run)

        log_engine_event(
            engine="sandbox-engine",
            message="Sandbox execution finished",
            trace_id=trace_id,
            extra={"status": sandbox_run.status},
        )

        return sandbox_run

    # ---------------------------------------------------------
    # INTERNAL: EXECUTION
    # ---------------------------------------------------------
    async def _execute(
        self,
        artifact_version: ArtifactVersion,
        language: str,
        command: Optional[str],
    ):
        """
        Execute code in a temporary file.
        """

        code = artifact_version.content

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, self._filename_for(language))

            # Write code to file
            with open(file_path, "w") as f:
                f.write(code)

            # Determine command
            cmd = command or self._default_command(language, file_path)

            # Run process
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            return (
                stdout.decode(),
                stderr.decode(),
                process.returncode,
            )

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------
    def _filename_for(self, language: str) -> str:
        if language == "python":
            return "script.py"
        if language == "node":
            return "script.js"
        return "script.txt"

    def _default_command(self, language: str, file_path: str) -> str:
        if language == "python":
            return f"python3 {file_path}"
        if language == "node":
            return f"node {file_path}"
        return f"sh {file_path}"
