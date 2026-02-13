# l4_core/db/ai_engines.py

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, Integer, Float, DateTime
from sqlalchemy.sql import func

from ..utils.ids import generate_id
from .core import Base


class AIEngine(Base):
    """
    Represents a single AI engine configuration.

    Examples:
    - openai-gpt-4o
    - deepseek-coder
    - claude-3-opus
    - gemini-1.5-pro
    """

    __tablename__ = "ai_engines"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_id
    )

    # e.g. "openai", "deepseek", "anthropic", "gemini"
    provider: Mapped[str] = mapped_column(String, nullable=False)

    # e.g. "gpt-4o", "deepseek-coder", "claude-3-opus", "gemini-1.5-pro"
    model: Mapped[str] = mapped_column(String, nullable=False)

    # Human-readable label for admin UI
    label: Mapped[str] = mapped_column(String, nullable=False)

    # Whether this engine is currently allowed to be used
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Priority for routing (lower = preferred)
    priority: Mapped[int] = mapped_column(Integer, default=10)

    # Whether this engine can be used as a fallback
    allow_fallback: Mapped[bool] = mapped_column(Boolean, default=True)

    # Simple usage metrics (can be expanded later)
    total_calls: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    avg_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
