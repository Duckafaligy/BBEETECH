# l4_core/db/models.py

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, JSON
from sqlalchemy.sql import func

from ..utils.ids import generate_id
from .core import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_id
    )
    name: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_id
    )
    workspace_id: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Flow(Base):
    __tablename__ = "flows"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_id
    )
    workspace_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # JSON definition of the flow
    definition: Mapped[dict] = mapped_column(JSON, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Page(Base):
    __tablename__ = "pages"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_id
    )
    workspace_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # JSON structure for UI rendering
    schema: Mapped[dict] = mapped_column(JSON, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
