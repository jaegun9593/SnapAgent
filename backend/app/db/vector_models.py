"""
Vector embedding model for snapdb.

This table stores document chunk embeddings in the main snapdb database
with FK references to agents and files tables.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SnapVecEbd(Base):
    """
    Vector embeddings table in snapdb.

    This table stores document chunk embeddings for similarity search.
    It has FK references to agents and files tables for data integrity.
    """

    __tablename__ = "snap_vec_ebd"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # FK references to main tables
    agent_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    file_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=False
    )

    # Content and embedding
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI embedding dimension

    # Chunk metadata
    chunk_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    extra: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Soft delete flag
    use_yn: Mapped[Optional[str]] = mapped_column(String(1), default="Y", nullable=True)

    # Audit fields
    created_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(default=func.now(), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(default=func.now(), nullable=True)
