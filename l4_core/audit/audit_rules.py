# l4_core/audit/audit_rules.py

"""
Audit Rules (L4+)
-----------------
Defines the rule system used by the AuditEngine.

Features:
  - Trace-aware evaluation
  - Rule categories (structure, consistency, safety, completeness)
  - Strong typing
  - Future-proof for scoring, severities, and rule groups
"""

from __future__ import annotations

from typing import List, Protocol, Optional

from l4_core.audit.audit_models import (
    AuditTarget,
    AuditIssue,
    AuditSeverity,
    AuditResult,
    AuditAction,
    AuditActionType,
)
from l4_core.utils.logging import log_engine_event


# ---------------------------------------------------------
# RULE PROTOCOL
# ---------------------------------------------------------
class AuditRule(Protocol):
    name: str
    category: str  # e.g. "structure", "consistency", "safety"

    async def evaluate(
        self,
        target: AuditTarget,
        trace_id: Optional[str] = None,
    ) -> AuditResult:
        ...


# ---------------------------------------------------------
# FLOW DEFINITION RULE
# ---------------------------------------------------------
class FlowDefinitionRule:
    """
    Ensures flow definitions are structurally valid and aligned with runtime expectations.
    """

    name = "flow_definition_rule"
    category = "structure"

    async def evaluate(
        self,
        target: AuditTarget,
        trace_id: Optional[str] = None,
    ) -> AuditResult:

        issues: List[AuditIssue] = []
        actions: List[AuditAction] = []

        definition = target.metadata.get("definition") or {}
        key = target.metadata.get("key")

        # Log rule evaluation
        if trace_id:
            log_engine_event(
                engine="audit-engine",
                message="Evaluating flow definition rule",
                trace_id=trace_id,
                extra={"flow_key": key},
            )

        # Validate type
        if not isinstance(definition, dict):
            issues.append(
                AuditIssue(
                    id=f"flow:{key}:invalid_definition_type",
                    target=target,
                    severity=AuditSeverity.ERROR,
                    code="FLOW_INVALID_DEFINITION_TYPE",
                    message="Flow definition must be a dict.",
                    details={"actual_type": str(type(definition))},
                )
            )
            actions.append(
                AuditAction(
                    type=AuditActionType.SUGGEST_CHANGE,
                    description="Convert flow definition to a dict structure.",
                    payload={"flow_key": key},
                    auto_applicable=False,
                )
            )

        # Future: validate steps, engines, inputs, outputs, IR schema

        return AuditResult(target=target, issues=issues, actions=actions)


# ---------------------------------------------------------
# PRESET STRUCTURE RULE
# ---------------------------------------------------------
class PresetStructureRule:
    """
    Ensures industry presets use the correct keys: flows, engines, pages, etc.
    """

    name = "preset_structure_rule"
    category = "structure"

    async def evaluate(
        self,
        target: AuditTarget,
        trace_id: Optional[str] = None,
    ) -> AuditResult:

        issues: List[AuditIssue] = []
        actions: List[AuditAction] = []

        preset = target.metadata.get("preset") or {}
        name = target.metadata.get("name")

        if trace_id:
            log_engine_event(
                engine="audit-engine",
                message="Evaluating preset structure rule",
                trace_id=trace_id,
                extra={"preset_name": name},
            )

        required_keys = ["flows", "engines"]
        missing = [k for k in required_keys if k not in preset]

        if missing:
            issues.append(
                AuditIssue(
                    id=f"preset:{name}:missing_keys",
                    target=target,
                    severity=AuditSeverity.ERROR,
                    code="PRESET_MISSING_KEYS",
                    message=f"Preset is missing required keys: {missing}",
                    details={"missing_keys": missing},
                )
            )
            actions.append(
                AuditAction(
                    type=AuditActionType.SUGGEST_CHANGE,
                    description="Add required keys to preset.",
                    payload={"preset_name": name, "missing_keys": missing},
                    auto_applicable=False,
                )
            )

        return AuditResult(target=target, issues=issues, actions=actions)


# ---------------------------------------------------------
# DEFAULT RULESET
# ---------------------------------------------------------
def default_rules() -> List[AuditRule]:
    """
    Returns the default set of audit rules.
    Future: dynamic rule loading, rule categories, severity filters.
    """
    return [
        FlowDefinitionRule(),
        PresetStructureRule(),
    ]
