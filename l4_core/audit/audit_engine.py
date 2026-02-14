# l4_core/audit/audit_engine.py

"""
Audit Engine (L4+)
------------------
Evaluates audit rules over targets, produces structured reports,
and optionally applies actions.

Features:
  - Trace-aware execution
  - Rule-level logging
  - Error isolation per rule
  - Dry-run support
  - Future-proof for:
      • rule categories
      • severities
      • scoring
      • workspace-wide audits
"""

from __future__ import annotations

from typing import List, Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from l4_core.audit.audit_models import AuditTarget, AuditReport, AuditResult
from l4_core.audit.audit_rules import AuditRule, default_rules
from l4_core.audit.audit_actions import AuditActionExecutor
from l4_core.audit.audit_reporter import AuditReporter
from l4_core.utils.logging import log_engine_event, generate_trace_id


class AuditEngine:
    """
    Core audit engine: evaluates rules over targets, produces a report,
    and optionally applies actions.
    """

    def __init__(
        self,
        db: AsyncSession | None = None,
        rules: Iterable[AuditRule] | None = None,
    ):
        self.db = db
        self.rules: List[AuditRule] = list(rules) if rules is not None else default_rules()
        self.action_executor = AuditActionExecutor(db=db)
        self.reporter = AuditReporter()

    # ---------------------------------------------------------
    # PUBLIC: AUDIT TARGETS
    # ---------------------------------------------------------
    async def audit_targets(
        self,
        scope: str,
        targets: List[AuditTarget],
        apply_fixes: bool = False,
        dry_run: bool = True,
    ) -> AuditReport:

        trace_id = generate_trace_id()

        log_engine_event(
            engine="audit-engine",
            message="Starting audit",
            trace_id=trace_id,
            extra={
                "scope": scope,
                "num_targets": len(targets),
                "apply_fixes": apply_fixes,
                "dry_run": dry_run,
            },
        )

        results: List[AuditResult] = []

        # -----------------------------------------------------
        # RULE EVALUATION
        # -----------------------------------------------------
        for target in targets:
            for rule in self.rules:
                try:
                    rule_result = await rule.evaluate(target, trace_id=trace_id)

                    if rule_result.issues or rule_result.actions:
                        results.append(rule_result)

                    log_engine_event(
                        engine="audit-engine",
                        message="Rule evaluated",
                        trace_id=trace_id,
                        extra={
                            "rule": rule.name,
                            "target": target.identifier,
                            "issues": len(rule_result.issues),
                            "actions": len(rule_result.actions),
                        },
                    )

                except Exception as e:
                    # Rule-level isolation
                    log_engine_event(
                        engine="audit-engine",
                        message="Rule evaluation error",
                        trace_id=trace_id,
                        extra={
                            "rule": rule.name,
                            "target": target.identifier,
                            "error": str(e),
                        },
                    )

        # -----------------------------------------------------
        # BUILD REPORT
        # -----------------------------------------------------
        report = AuditReport(scope=scope, results=results)

        # Emit report (logging, saving, etc.)
        self.reporter.log_report(report)

        # -----------------------------------------------------
        # APPLY FIXES (OPTIONAL)
        # -----------------------------------------------------
        if apply_fixes and results:
            log_engine_event(
                engine="audit-engine",
                message="Applying audit fixes",
                trace_id=trace_id,
                extra={"dry_run": dry_run},
            )
            await self.action_executor.apply_actions(results, dry_run=dry_run)

        log_engine_event(
            engine="audit-engine",
            message="Audit completed",
            trace_id=trace_id,
            extra={"total_results": len(results)},
        )

        return report
