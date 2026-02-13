"""
Vector embedding model for snapagentdb.

This table stores document chunk embeddings with LIST partitioning by agent_id.
Each Agent gets its own partition with an independent IVFFlat vector index
for efficient per-Agent similarity search.

Note: PRIMARY KEY is composite (id, agent_id) as required by PostgreSQL
partitioned tables — the partition key must be included in the PK.
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
    Vector embeddings table (partitioned by agent_id).

    Each row stores a single document chunk with its vector embedding.
    The table is LIST-partitioned by agent_id so each Agent's data
    lives in a dedicated physical partition with its own IVFFlat index.
    """

    __tablename__ = "snap_vec_ebd"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Partition key — also part of composite PK
    agent_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, nullable=False
    )

    file_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=False
    )

    # Content and embedding
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = Column(Vector())  # Dimension-free: supports 1536, 3072, etc.

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
