# l4_core/db/ai_learning_ir.py

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, JSON, DateTime
from sqlalchemy.sql import func

from ..utils.ids import generate_id
from .core import Base


class AILearningIR(Base):
    """
    Stores IR (Intent Representation) teaching data.
    This is the memory your AI uses to:
    - explain code at multiple difficulty levels
    - break down meaning and intent
    - store code snippets linked to IR
    - evolve teaching patterns over time
    """

    __tablename__ = "ai_learning_ir"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_id
    )

    workspace_id: Mapped[str] = mapped_column(String, nullable=False)

    # The IR text itself (the "meaning" or "intent")
    ir_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Code snippet associated with the IR
    code_snippet: Mapped[str] = mapped_column(Text, nullable=True)

    # Beginner → Intermediate → Expert explanations
    explanation_beginner: Mapped[str] = mapped_column(Text, nullable=True)
    explanation_intermediate: Mapped[str] = mapped_column(Text, nullable=True)
    explanation_expert: Mapped[str] = mapped_column(Text, nullable=True)

    # Future: semantic graph of meaning, relationships, and concepts
    meaning_graph: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Metadata for future AI evolution
    metadata: Mapped[dict] = mapped_column(JSON, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

