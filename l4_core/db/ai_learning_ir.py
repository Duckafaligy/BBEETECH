# l4_core/db/ai_learning_ir.py

"""
AILearningIR (L4+)
------------------
Stores IR (Intent Representation) teaching data.

This table powers:
  - multi-level explanations (beginner → expert)
  - semantic meaning graphs
  - code-to-IR alignment
  - pattern evolution
  - future embedding-based retrieval
  - workspace-specific teaching memory
"""

from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, JSON, DateTime, Index
from sqlalchemy.sql import func

from l4_core.utils.ids import generate_id
from l4_core.db.core import Base


class AILearningIR(Base):
    """
    Represents a single IR teaching record.
    """

    __tablename__ = "ai_learning_ir"

    # ---------------------------------------------------------
    # IDENTITY
    # ---------------------------------------------------------
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=generate_id,
        doc="Unique identifier for this IR record",
    )

    workspace_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
        doc="Workspace this IR belongs to",
    )

    # ---------------------------------------------------------
    # CORE IR CONTENT
    # ---------------------------------------------------------
    ir_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="The IR text itself (the meaning or intent)",
    )

    code_snippet: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        doc="Optional code snippet associated with this IR",
    )

    # ---------------------------------------------------------
    # MULTI-LEVEL EXPLANATIONS
    # ---------------------------------------------------------
    explanation_beginner: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        doc="Beginner-level explanation",
    )

    explanation_intermediate: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        doc="Intermediate-level explanation",
    )

    explanation_expert: Mapped[str] = mapped_column(
        Text,
        nullable=True,
        doc="Expert-level explanation",
    )

    # ---------------------------------------------------------
    # SEMANTIC GRAPH + METADATA
    # ---------------------------------------------------------
    meaning_graph: Mapped[dict] = mapped_column(
        JSON,
        nullable=True,
        doc="Semantic graph of meaning, relationships, and concepts",
    )

    meta: Mapped[dict] = mapped_column(
        JSON,
        nullable=True,
        doc="Metadata for future AI evolution (embeddings, lineage, tags)",
    )

    # ---------------------------------------------------------
    # TIMESTAMPS
    # ---------------------------------------------------------
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


# ---------------------------------------------------------
# INDEXES (L4+)
# ---------------------------------------------------------
Index(
    "idx_ai_learning_ir_workspace",
    AILearningIR.workspace_id,
)

Index(
    "idx_ai_learning_ir_ir_text_gin",
    AILearningIR.ir_text,
    postgresql_using="gin",
)  # Future: full-text search / embeddings
