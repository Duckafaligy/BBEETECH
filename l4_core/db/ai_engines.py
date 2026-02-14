# l4_core/db/ai_engines.py

"""
AIEngine (L4+)
--------------
Represents a single AI engine configuration used by the AIRouter.

Features:
  - Provider + model identity
  - Routing priority
  - Fallback eligibility
  - Usage metrics
  - Latency tracking
  - Future-proof for scoring, cost-awareness, and model families
"""

from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Integer, Float, DateTime, UniqueConstraint
from sqlalchemy.sql import func

from l4_core.utils.ids import generate_id
from l4_core.db.core import Base


class AIEngine(Base):
    """
    Represents a single AI engine configuration.

    Examples:
      - openai:gpt-4o
      - deepseek:coder
      - anthropic:claude-3-opus
      - gemini:1.5-pro
    """

    __tablename__ = "ai_engines"

    # Ensure provider+model pairs are unique
    __table_args__ = (
        UniqueConstraint("provider", "model", name="uq_provider_model"),
    )

    # ---------------------------------------------------------
    # IDENTITY
    # ---------------------------------------------------------
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=generate_id,
    )

    provider: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Provider name: openai, deepseek, anthropic, gemini, internal",
    )

    model: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Model identifier: gpt-4o, deepseek-coder, claude-3-opus, gemini-1.5-pro",
    )

    label: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="Human-readable label for admin UI",
    )

    # ---------------------------------------------------------
    # ROUTING CONFIG
    # ---------------------------------------------------------
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        doc="Whether this engine is currently allowed to be used",
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=10,
        doc="Lower = preferred for routing",
    )

    allow_fallback: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        doc="Whether this engine can be used as a fallback",
    )

    # ---------------------------------------------------------
    # METRICS (future: scoring, cost-awareness)
    # ---------------------------------------------------------
    total_calls: Mapped[int] = mapped_column(
        Integer,
        default=0,
        doc="Total number of calls made to this engine",
    )

    total_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        doc="Total tokens consumed by this engine",
    )

    avg_latency_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        doc="Rolling average latency in milliseconds",
    )

    # ---------------------------------------------------------
    # TIMESTAMPS
    # ---------------------------------------------------------
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
