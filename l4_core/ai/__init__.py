# l4_core/ai/__init__.py

"""
L4+ AI Subsystem Public API
---------------------------
This module defines the public interface for the AI subsystem.

It exposes:
  - AIRouter (provider selection + retries + routing)
  - RuntimeEngine (flow execution)
  - WorkspaceFactory (workspace initialization)
  - FlowEngine / PageEngine / TeachingEngine / SandboxEngine / PatternEngine
  - AIRequest / AIResponse (normalized request/response types)

Upgrades in L4+ version:
  - Clean, stable public API surface
  - Audit-ready exports
  - Avoids circular imports
  - Future-proof for plugin engines
"""

from __future__ import annotations

# Core router + request/response types
from .router import AIRouter, AIRequest, AIResponse

# Engines
from .flow_engine import FlowEngine
from .page_engine import PageEngine
from .teaching_engine import TeachingEngine
from .sandbox_engine import SandboxEngine
from .pattern_engine import PatternEngine
from .runtime_engine import RuntimeEngine

# Workspace factory
from .workspace_factory import WorkspaceFactory

# Audit engine (AI-level audit, not system-wide audit)
from .audit_engine import AuditEngine


__all__ = [
    # Router + request/response
    "AIRouter",
    "AIRequest",
    "AIResponse",

    # Engines
    "FlowEngine",
    "PageEngine",
    "TeachingEngine",
    "SandboxEngine",
    "PatternEngine",
    "RuntimeEngine",

    # Workspace
    "WorkspaceFactory",

    # Audit
    "AuditEngine",
]
