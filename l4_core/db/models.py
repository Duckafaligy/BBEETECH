# l4_core/db/models.py

"""
Database Models (L4+)
---------------------
This module defines the full relational schema for the AI OS.

Features:
  - Strong typing via SQLAlchemy 2.0 Mapped[]
  - Clean grouping: Workspaces, Engines, Flows, Artifacts, Logs, Sandbox, Learning, Audit, Analytics
  - Future-proof indexes
  - Relationship loading strategies
  - Multi-tenant workspace awareness
  - Audit-ready and analytics-ready fields
"""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    Index,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from l4_core.db.core import Base
from l4_core.utils.ids import generate_id

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from l4_core.db.core import Base


class AIEngine(Base):
    __tablename__ = "ai_engines"

    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)

    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    label = Column(String, nullable=False)

    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    allow_fallback = Column(Boolean, default=True)

    # REMOVE back_populates — this is the fix
    workspace = relationship("Workspace")




# ============================================================
# WORKSPACES
# ============================================================

class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    name: Mapped[str] = mapped_column(String, nullable=False)
    owner_id: Mapped[str | None] = mapped_column(String, nullable=True)
    workspace_type: Mapped[str] = mapped_column(String, nullable=False)

    settings: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    engines: Mapped[list["WorkspaceEngineConfig"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    flows: Mapped[list["FlowDefinition"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    artifacts: Mapped[list["Artifact"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


Index("idx_workspace_type", Workspace.workspace_type)


# ============================================================
# ENGINE CONFIG
# ============================================================

class WorkspaceEngineConfig(Base):
    __tablename__ = "workspace_engine_configs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    workspace_id: Mapped[str] = mapped_column(
        String, ForeignKey("workspaces.id"), nullable=False
    )

    provider: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[str | None] = mapped_column(String, nullable=True)

    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=1)
    allow_fallback: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    workspace: Mapped["Workspace"] = relationship(back_populates="engines")


Index("idx_engine_workspace", WorkspaceEngineConfig.workspace_id)


# ============================================================
# FLOWS
# ============================================================

class FlowDefinition(Base):
    __tablename__ = "flow_definitions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    workspace_id: Mapped[str] = mapped_column(
        String, ForeignKey("workspaces.id"), nullable=False
    )

    key: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    definition: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    workspace: Mapped["Workspace"] = relationship(back_populates="flows")

    runs: Mapped[list["FlowRun"]] = relationship(
        back_populates="flow",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


Index("idx_flow_workspace", FlowDefinition.workspace_id)


class FlowRun(Base):
    __tablename__ = "flow_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    flow_id: Mapped[str] = mapped_column(
        String, ForeignKey("flow_definitions.id"), nullable=False
    )
    workspace_id: Mapped[str] = mapped_column(
        String, ForeignKey("workspaces.id"), nullable=False
    )

    status: Mapped[str] = mapped_column(String, default="pending")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    input_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    output_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    error_payload: Mapped[dict] = mapped_column(JSON, default=dict)

    trace_id: Mapped[str | None] = mapped_column(String, nullable=True)

    flow: Mapped["FlowDefinition"] = relationship(back_populates="runs")
    workspace: Mapped["Workspace"] = relationship()


Index("idx_flowrun_workspace", FlowRun.workspace_id)


# ============================================================
# ARTIFACTS + VERSIONING
# ============================================================

class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    workspace_id: Mapped[str] = mapped_column(
        String, ForeignKey("workspaces.id"), nullable=False
    )

    artifact_type: Mapped[str] = mapped_column(String, nullable=False)
    key: Mapped[str] = mapped_column(String, nullable=False)

    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    workspace: Mapped["Workspace"] = relationship(back_populates="artifacts")

    versions: Mapped[list["ArtifactVersion"]] = relationship(
        back_populates="artifact",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


Index("idx_artifact_workspace", Artifact.workspace_id)
Index("idx_artifact_key", Artifact.key)


class ArtifactVersion(Base):
    __tablename__ = "artifact_versions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    artifact_id: Mapped[str] = mapped_column(
        String, ForeignKey("artifacts.id"), nullable=False
    )

    version_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_format: Mapped[str] = mapped_column(String, default="text")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by_engine: Mapped[str | None] = mapped_column(String, nullable=True)
    created_by_flow_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("flow_definitions.id"), nullable=True
    )

    sandbox_status: Mapped[str | None] = mapped_column(String, nullable=True)
    sandbox_metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    artifact: Mapped["Artifact"] = relationship(back_populates="versions")
    created_by_flow: Mapped["FlowDefinition"] = relationship()


Index("idx_artifact_version", ArtifactVersion.artifact_id)


# ============================================================
# LOGGING
# ============================================================

class PromptLog(Base):
    __tablename__ = "prompt_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    workspace_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("workspaces.id"), nullable=True
    )
    flow_run_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("flow_runs.id"), nullable=True
    )

    provider: Mapped[str | None] = mapped_column(String, nullable=True)
    model: Mapped[str | None] = mapped_column(String, nullable=True)

    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    workspace: Mapped["Workspace"] = relationship()
    flow_run: Mapped["FlowRun"] = relationship()


class AIRunLog(Base):
    __tablename__ = "ai_run_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    workspace_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("workspaces.id"), nullable=True
    )
    flow_run_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("flow_runs.id"), nullable=True
    )

    provider: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    trace_id: Mapped[str | None] = mapped_column(String, nullable=True)

    request_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    response_payload: Mapped[dict] = mapped_column(JSON, default=dict)

    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    workspace: Mapped["Workspace"] = relationship()
    flow_run: Mapped["FlowRun"] = relationship()


class CodeSandboxRun(Base):
    __tablename__ = "code_sandbox_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    artifact_version_id: Mapped[str] = mapped_column(
        String, ForeignKey("artifact_versions.id"), nullable=False
    )
    workspace_id: Mapped[str] = mapped_column(
        String, ForeignKey("workspaces.id"), nullable=False
    )

    environment: Mapped[str] = mapped_column(String, nullable=False)
    command: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(String, default="pending")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    stdout: Mapped[str | None] = mapped_column(Text, nullable=True)
    stderr: Mapped[str | None] = mapped_column(Text, nullable=True)
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)

    error_class: Mapped[str | None] = mapped_column(String, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    workspace: Mapped["Workspace"] = relationship()
    artifact_version: Mapped["ArtifactVersion"] = relationship()


Index("idx_sandbox_workspace", CodeSandboxRun.workspace_id)


# ============================================================
# ERROR → FIX MAPPING (LEARNING)
# ============================================================

class ErrorPattern(Base):
    __tablename__ = "error_patterns"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    error_class: Mapped[str] = mapped_column(String, nullable=False)
    signature: Mapped[str] = mapped_column(String, nullable=False)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FixPattern(Base):
    __tablename__ = "fix_patterns"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    error_pattern_id: Mapped[str] = mapped_column(
        String, ForeignKey("error_patterns.id"), nullable=False
    )

    fix_description: Mapped[str] = mapped_column(Text, nullable=False)
    fix_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    error_pattern: Mapped["ErrorPattern"] = relationship()


class CodeDiff(Base):
    __tablename__ = "code_diffs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    artifact_version_id: Mapped[str] = mapped_column(
        String, ForeignKey("artifact_versions.id"), nullable=False
    )

    before: Mapped[str] = mapped_column(Text, nullable=False)
    after: Mapped[str] = mapped_column(Text, nullable=False)
    diff: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    artifact_version: Mapped["ArtifactVersion"] = relationship()


# ============================================================
# AUDIT + ROLLBACK
# ============================================================

class FileAudit(Base):
    __tablename__ = "file_audits"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    workspace_id: Mapped[str] = mapped_column(
        String, ForeignKey("workspaces.id"), nullable=False
    )

    file_path: Mapped[str] = mapped_column(String, nullable=False)
    new_content: Mapped[str] = mapped_column(Text, nullable=False)
    old_content: Mapped[str | None] = mapped_column(Text, nullable=True)

    audit_status: Mapped[str] = mapped_column(String, default="pending")
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    workspace: Mapped["Workspace"] = relationship()


class FileRollback(Base):
    __tablename__ = "file_rollbacks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    audit_id: Mapped[str] = mapped_column(
        String, ForeignKey("file_audits.id"), nullable=False
    )

    restored_content: Mapped[str] = mapped_column(Text, nullable=False)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    audit: Mapped["FileAudit"] = relationship()


# ============================================================
# ANALYTICS
# ============================================================

class EnginePerformance(Base):
    __tablename__ = "engine_performance"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)

    total_calls: Mapped[int] = mapped_column(Integer, default=0)
    total_failures: Mapped[int] = mapped_column(Integer, default=0)
    avg_latency_ms: Mapped[int] = mapped_column(Integer, default=0)

    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class WorkspaceAnalytics(Base):
    __tablename__ = "workspace_analytics"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_id)
    workspace_id: Mapped[str] = mapped_column(
        String, ForeignKey("workspaces.id"), nullable=False
    )

    total_flows_run: Mapped[int] = mapped_column(Integer, default=0)
    total_artifacts_created: Mapped[int] = mapped_column(Integer, default=0)
    total_errors: Mapped[int] = mapped_column(Integer, default=0)

    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    workspace: Mapped["Workspace"] = relationship()
