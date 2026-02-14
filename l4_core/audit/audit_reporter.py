# l4_core/audit/audit_reporter.py

"""
Audit Reporter (L4+)
--------------------
Responsible for emitting audit reports to logs, files, or future UIs.

Features:
  - Trace-aware reporting
  - Structured JSON output
  - Severity grouping
  - Summary metadata
  - Future-proof for dashboards, CLI, and API endpoints
"""

from __future__ import annotations

import json
from typing import List, Dict, Any

from l4_core.audit.audit_models import AuditReport, AuditResult, AuditIssue, AuditSeverity
from l4_core.utils.logging import log_engine_event, generate_trace_id


class AuditReporter:
    """
    Converts audit reports into structured formats and emits them.
    """

    def __init__(self) -> None:
        ...

    # ---------------------------------------------------------
    # PUBLIC: CONVERT REPORT TO DICT
    # ---------------------------------------------------------
    def to_dict(self, report: AuditReport) -> Dict[str, Any]:
        return {
            "scope": report.scope,
            "has_critical": report.has_critical(),
            "total_issues": report.total_issues(),
            "total_actions": report.total_actions(),
            "severity_summary": self._severity_summary(report),
            "results": [
                {
                    "target": {
                        "type": r.target.type,
                        "identifier": r.target.identifier,
                        "metadata": r.target.metadata,
                    },
                    "issues": [
                        {
                            "id": i.id,
                            "severity": i.severity,
                            "code": i.code,
                            "message": i.message,
                            "details": i.details,
                        }
                        for i in r.issues
                    ],
                    "actions": [
                        {
                            "type": a.type,
                            "description": a.description,
                            "payload": a.payload,
                            "auto_applicable": a.auto_applicable,
                        }
                        for a in r.actions
                    ],
                }
                for r in report.results
            ],
        }

    # ---------------------------------------------------------
    # PUBLIC: JSON OUTPUT
    # ---------------------------------------------------------
    def to_json(self, report: AuditReport, indent: int = 2) -> str:
        return json.dumps(self.to_dict(report), indent=indent)

    # ---------------------------------------------------------
    # PUBLIC: LOG REPORT
    # ---------------------------------------------------------
    def log_report(self, report: AuditReport) -> None:
        trace_id = generate_trace_id()

        log_engine_event(
            engine="audit-engine",
            message="Audit report generated",
            trace_id=trace_id,
            extra=self.to_dict(report),
        )

    # ---------------------------------------------------------
    # INTERNAL: SEVERITY SUMMARY
    # ---------------------------------------------------------
    def _severity_summary(self, report: AuditReport) -> Dict[str, int]:
        summary = {
            "info": 0,
            "warning": 0,
            "error": 0,
            "critical": 0,
        }

        for result in report.results:
            for issue in result.issues:
                sev = issue.severity.value
                if sev in summary:
                    summary[sev] += 1

        return summary
