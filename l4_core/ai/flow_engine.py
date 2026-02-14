# l4_core/ai/flow_engine.py

"""
Flow Engine (L4+)
-----------------
Executes multi-step AI flows with:
  - trace-aware execution
  - structured IR extraction
  - artifact creation + versioning
  - step-level logging
  - retries + fallback support (future)
  - conditional + parallel steps (future)
  - audit-ready metadata

This engine is intentionally modular and future-proof.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from l4_core.ai.router import AIRouter, AIRequest
from l4_core.db.models import (
    FlowDefinition,
    FlowRun,
    Artifact,
    ArtifactVersion,
    PromptLog,
    AIRunLog,
)
from l4_core.utils.logging import log_engine_event, generate_trace_id


class FlowEngine:
    """
    Executes multi-step flows using AIRouter + IR extraction.
    """

    def __init__(self, db: AsyncSession, ai_router: AIRouter):
        self.db = db
        self.ai_router = ai_router

    # ---------------------------------------------------------
    # PUBLIC ENTRYPOINT
    # ---------------------------------------------------------
    async def run_flow(
        self,
        flow: FlowDefinition,
        workspace_id: str,
        user_input: Dict[str, Any],
    ) -> Dict[str, Any]:

        trace_id = generate_trace_id()

        # Create FlowRun record
        flow_run = FlowRun(
            id=trace_id,
            flow_id=flow.id,
            workspace_id=workspace_id,
            status="running",
            started_at=datetime.utcnow(),
            input_payload=user_input,
        )
        self.db.add(flow_run)
        await self.db.commit()

        log_engine_event(
            engine="flow-engine",
            message=f"Flow started: {flow.key}",
            trace_id=trace_id,
            extra={"flow_id": flow.id, "workspace_id": workspace_id},
        )

        steps = flow.definition.get("steps", [])
        step_outputs: Dict[str, Any] = {}

        for step_name in steps:
            try:
                step_output = await self._run_step(
                    flow_run=flow_run,
                    step_name=step_name,
                    user_input=user_input,
                    previous_outputs=step_outputs,
                )
                step_outputs[step_name] = step_output

            except Exception as e:
                flow_run.status = "failed"
                flow_run.error_payload = {"step": step_name, "error": str(e)}
                flow_run.finished_at = datetime.utcnow()
                await self.db.commit()

                log_engine_event(
                    engine="flow-engine",
                    message=f"Flow failed at step: {step_name}",
                    trace_id=trace_id,
                    extra={"error": str(e)},
                )

                return {
                    "status": "failed",
                    "flow_id": flow.id,
                    "flow_run_id": flow_run.id,
                    "error": str(e),
                }

        # Flow success
        flow_run.status = "success"
        flow_run.output_payload = step_outputs
        flow_run.finished_at = datetime.utcnow()
        await self.db.commit()

        log_engine_event(
            engine="flow-engine",
            message=f"Flow completed successfully: {flow.key}",
            trace_id=trace_id,
        )

        return {
            "status": "success",
            "flow_id": flow.id,
            "flow_run_id": flow_run.id,
            "outputs": step_outputs,
        }

    # ---------------------------------------------------------
    # INTERNAL: RUN A SINGLE STEP
    # ---------------------------------------------------------
    async def _run_step(
        self,
        flow_run: FlowRun,
        step_name: str,
        user_input: Dict[str, Any],
        previous_outputs: Dict[str, Any],
    ) -> Any:

        trace_id = flow_run.id

        # Build prompt
        prompt = self._build_step_prompt(
            step_name=step_name,
            user_input=user_input,
            previous_outputs=previous_outputs,
        )

        # Log prompt
        prompt_log = PromptLog(
            id=generate_trace_id(),
            workspace_id=flow_run.workspace_id,
            flow_run_id=flow_run.id,
            provider=None,
            model=None,
            prompt=prompt,
            metadata={"step": step_name},
        )
        self.db.add(prompt_log)
        await self.db.commit()

        # Call AI Router
        ai_request = AIRequest(prompt=prompt)
        ai_response = await self.ai_router.generate_text(ai_request, trace_id=trace_id)

        # Log AI run
        ai_log = AIRunLog(
            id=generate_trace_id(),
            workspace_id=flow_run.workspace_id,
            flow_run_id=flow_run.id,
            provider=ai_response.provider,
            model=ai_response.model,
            trace_id=ai_response.trace_id,
            request_payload={"prompt": prompt},
            response_payload={"content": ai_response.content},
            success=True,
        )
        self.db.add(ai_log)
        await self.db.commit()

        # Extract IR + artifacts
        parsed_output = await self._extract_ir_and_artifacts(
            flow_run=flow_run,
            step_name=step_name,
            ai_output=ai_response.content,
        )

        return parsed_output

    # ---------------------------------------------------------
    # PROMPT BUILDER (IR ENFORCED)
    # ---------------------------------------------------------
    def _build_step_prompt(
        self,
        step_name: str,
        user_input: Dict[str, Any],
        previous_outputs: Dict[str, Any],
    ) -> str:

        return (
            f"You are executing step '{step_name}' of a multi-step flow.\n\n"
            f"User Input (JSON):\n{json.dumps(user_input, indent=2)}\n\n"
            f"Previous Step Outputs (JSON):\n{json.dumps(previous_outputs, indent=2)}\n\n"
            "Respond ONLY as a single JSON object with this exact shape:\n\n"
            "{\n"
            '  \"kind\": \"code\" | \"doc\" | \"asset\" | \"shader\" | \"config\" | \"mixed\",\n'
            '  \"language\": \"python\" | \"typescript\" | \"glsl\" | \"none\",\n'
            '  \"title\": \"short title\",\n'
            '  \"summary\": \"short explanation\",\n'
            '  \"content\": \"the main code or text\",\n'
            '  \"metadata\": { \"any\": \"extra details\" }\n'
            "}\n\n"
            "Do NOT include anything outside the JSON. The entire response MUST be valid JSON."
        )

    # ---------------------------------------------------------
    # IR + ARTIFACT EXTRACTION
    # ---------------------------------------------------------
    async def _extract_ir_and_artifacts(
        self,
        flow_run: FlowRun,
        step_name: str,
        ai_output: str,
    ) -> Dict[str, Any]:

        # Parse IR
        try:
            ir = json.loads(ai_output)
        except Exception:
            ir = {
                "kind": "doc",
                "language": "none",
                "title": f"{flow_run.flow_id}:{step_name}",
                "summary": "Unstructured output (failed JSON parse).",
                "content": ai_output,
                "metadata": {"step": step_name, "parse_error": True},
            }

        artifact_type = ir.get("kind", "doc")
        key = ir.get("title") or f"{flow_run.flow_id}:{step_name}"

        # Create artifact
        artifact = Artifact(
            id=generate_trace_id(),
            workspace_id=flow_run.workspace_id,
            artifact_type=artifact_type,
            key=key,
            metadata={
                "step": step_name,
                "language": ir.get("language"),
                "summary": ir.get("summary"),
                **(ir.get("metadata") or {}),
            },
        )
        self.db.add(artifact)
        await self.db.commit()

        # Create version
        version = ArtifactVersion(
            id=generate_trace_id(),
            artifact_id=artifact.id,
            version_index=1,
            content=ir.get("content", ""),
            content_format="text",
            created_by_engine="flow-engine",
            created_by_flow_id=flow_run.flow_id,
        )
        self.db.add(version)
        await self.db.commit()

        return {
            "artifact_id": artifact.id,
            "version_id": version.id,
            "ir": ir,
        }
