"""
Vector store operations for managing document embeddings.
"""
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.vector_models import SnapVecEbd

logger = logging.getLogger(__name__)


class VectorStore:
    """Manage vector embeddings in the database."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def similarity_search(
        self,
        embedding: List[float],
        agent_id: UUID,
        top_k: int = 5,
        threshold: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.

        Args:
            embedding: Query embedding vector
            agent_id: Agent ID to search within
            top_k: Number of results to return
            threshold: Minimum similarity threshold

        Returns:
            List of matching chunks with similarity scores
        """
        result = await self.db.execute(
            text("""
                SELECT
                    id, content, chunk_index, file_id, extra,
                    1 - (embedding <=> :embedding::vector) as similarity
                FROM snap_vec_ebd
                WHERE agent_id = :agent_id
                  AND use_yn = 'Y'
                  AND 1 - (embedding <=> :embedding::vector) >= :threshold
                ORDER BY similarity DESC
                LIMIT :top_k
            """),
            {
                "embedding": str(embedding),
                "agent_id": str(agent_id),
                "threshold": threshold,
                "top_k": top_k,
            },
        )

        rows = result.fetchall()
        return [
            {
                "id": str(row.id),
                "content": row.content,
                "chunk_index": row.chunk_index,
                "file_id": str(row.file_id),
                "similarity": round(float(row.similarity), 4),
                "extra": row.extra,
            }
            for row in rows
        ]

    async def delete_by_agent(self, agent_id: UUID) -> int:
        """Delete all vectors for an agent."""
        result = await self.db.execute(
            text("UPDATE snap_vec_ebd SET use_yn = 'N' WHERE agent_id = :agent_id"),
            {"agent_id": str(agent_id)},
        )
        await self.db.commit()
        return result.rowcount

    async def delete_by_file(self, agent_id: UUID, file_id: UUID) -> int:
        """Delete all vectors for a specific file within an agent."""
        result = await self.db.execute(
            text(
                "UPDATE snap_vec_ebd SET use_yn = 'N' "
                "WHERE agent_id = :agent_id AND file_id = :file_id"
            ),
            {"agent_id": str(agent_id), "file_id": str(file_id)},
        )
        await self.db.commit()
        return result.rowcount
