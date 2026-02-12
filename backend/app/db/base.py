"""
SQLAlchemy base model and mixins.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class AuditMixin:
    """Mixin for audit fields (created_by, created_at, updated_by, updated_at, use_yn).

    All tables inherit these fields for tracking who created/modified records and when.
    """

    @declared_attr
    def created_by(cls) -> Mapped[Optional[str]]:
        """User who created this record (email)."""
        return mapped_column(
            String(255),
            ForeignKey("users.email", ondelete="SET NULL"),
            nullable=True,
        )

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        """Timestamp when this record was created."""
        return mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )

    @declared_attr
    def updated_by(cls) -> Mapped[Optional[str]]:
        """User who last updated this record (email)."""
        return mapped_column(
            String(255),
            ForeignKey("users.email", ondelete="SET NULL"),
            nullable=True,
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        """Timestamp when this record was last updated."""
        return mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )

    # use_yn field - 'Y' for active, 'N' for soft deleted
    use_yn: Mapped[str] = mapped_column(String(1), default="Y", nullable=False)
