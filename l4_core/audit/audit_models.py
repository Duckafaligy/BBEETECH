# l4_core/audit/audit_models.py

"""
Audit Models (L4+)
------------------
Defines the core data structures for the audit subsystem.

Features:
  - Strongly typed audit targets
  - Severity-aware issues
  - Action metadata for auto-application
  - Future-proof for:
      • rule categories
      • scoring
      • grouping
      • dashboards
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------
# ENUMS
# ---------------------------------------------------------
class AuditTargetType(str, Enum):
    FILE = "file"
    FLOW = "flow"
    PRESET = "preset"
    ENGINE_CONFIG = "engine_config"
    WORKSPACE = "workspace"
    ROUTER = "router"
    RUNTIME_ENGINE = "runtime_engine"


class AuditSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditActionType(str, Enum):
    NOOP = "noop"
    SUGGEST_CHANGE = "suggest_change"
    APPLY_CHANGE = "apply_change"
    CREATE_FILE = "create_file"
    UPDATE_FILE = "update_file"
    DELETE_FILE = "delete_file"
    UPDATE_DB = "update_db"


# ---------------------------------------------------------
# CORE MODELS
# ---------------------------------------------------------
@dataclass
class AuditTarget:
    """
    Represents an entity being audited.
    Example identifiers:
      - file path
      - flow key
      - workspace id
      - engine config id
    """
    type: AuditTargetType
    identifier: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditIssue:
    """
    Represents a single audit issue detected by a rule.
    """
    id: str
    target: AuditTarget
    severity: AuditSeverity
    code: str  # e.g. "FLOW_MISSING_DEFINITION"
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    # Future: rule_name, rule_category, score, etc.


@dataclass
class AuditAction:
    """
    Represents an action that can fix or improve a target.
    """
    type: AuditActionType
    description: str
    payload: Dict[str, Any]
    auto_applicable: bool = False  # Whether the system can safely apply it automatically


@dataclass
class AuditResult:
    """
    Represents the result of evaluating a single rule on a single target.
    """
    target: AuditTarget
    issues: List[AuditIssue] = field(default_factory=list)
    actions: List[AuditAction] = field(default_factory=list)


@dataclass
class AuditReport:
    """
    Represents the full audit report for a given scope.
    """
    scope: str  # e.g. "workspace:59f2...", "repo", "industry:software_dev"
    results: List[AuditResult]

    def has_critical(self) -> bool:
        return any(
            issue.severity in {AuditSeverity.ERROR, AuditSeverity.CRITICAL}
            for result in self.results
            for issue in result.issues
        )

    def total_issues(self) -> int:
        return sum(len(result.issues) for result in self.results)

    def total_actions(self) -> int:
        return sum(len(result.actions) for result in self.results)
