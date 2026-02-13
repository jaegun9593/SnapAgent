"""
Vector store utilities for pgvector-based similarity search.

Uses snap_vec_ebd table with LIST partitioning by agent_id.
Each Agent gets its own partition with an independent IVFFlat index
for efficient per-Agent similarity search.
"""
import logging
from typing import Any, Dict, List, Tuple
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.vector_models import SnapVecEbd

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store for storing and searching document embeddings."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # Partition management
    # ------------------------------------------------------------------

    async def create_partition(self, agent_id: UUID) -> None:
        """
        Create a dedicated partition for an Agent.

        Uses a separate raw connection for DDL to avoid breaking
        the caller's transaction state.
        """
        from app.db.database import engine

        partition_name = f"snap_vec_ebd_{str(agent_id).replace('-', '_')}"

        async with engine.begin() as conn:
            # Create partition for this Agent
            await conn.execute(
                text(f"""
                    CREATE TABLE IF NOT EXISTS {partition_name}
                    PARTITION OF snap_vec_ebd
                    FOR VALUES IN ('{agent_id}')
                """)
            )

            # Create file_id index for filtering
            await conn.execute(
                text(f"""
                    CREATE INDEX IF NOT EXISTS idx_{partition_name}_file_id
                    ON {partition_name}(file_id)
                """)
            )

    async def create_vector_index(self, agent_id: UUID, lists: int = 100) -> None:
        """
        Create IVFFlat vector index on an Agent's partition.

        Detects embedding dimension from existing data and creates
        the index with an explicit dimension cast.
        Call after inserting embeddings for better index quality.
        """
        from app.db.database import engine

        partition_name = f"snap_vec_ebd_{str(agent_id).replace('-', '_')}"

        async with engine.begin() as conn:
            # Detect dimension from existing data
            result = await conn.execute(
                text(f"""
                    SELECT vector_dims(embedding)
                    FROM {partition_name}
                    WHERE embedding IS NOT NULL
                    LIMIT 1
                """)
            )
            row = result.fetchone()
            if not row:
                return  # No data yet, skip index creation

            dim = row[0]

            await conn.execute(
                text(f"""
                    CREATE INDEX IF NOT EXISTS idx_{partition_name}_embedding
                    ON {partition_name}
                    USING ivfflat ((embedding::vector({dim})) vector_cosine_ops)
                    WITH (lists = {lists})
                """)
            )

    async def drop_partition(self, agent_id: UUID) -> None:
        """
        Drop a partition for an Agent.

        Permanently deletes all embeddings for the Agent.
        Much faster than DELETE for large datasets.
        """
        from app.db.database import engine

        partition_name = f"snap_vec_ebd_{str(agent_id).replace('-', '_')}"

        async with engine.begin() as conn:
            await conn.execute(text(f"DROP TABLE IF EXISTS {partition_name}"))

    # ------------------------------------------------------------------
    # Chunk management
    # ------------------------------------------------------------------

    async def add_chunks(
        self,
        agent_id: UUID,
        file_id: UUID,
        chunks: List[str],
        embeddings: List[List[float]],
        user_email: str,
    ) -> List[SnapVecEbd]:
        """
        Add document chunks with embeddings to the vector store.

        Args:
            agent_id: Agent ID (partition key)
            file_id: File ID (FK to files table)
            chunks: List of text chunks
            embeddings: List of embedding vectors
            user_email: User email who created these chunks

        Returns:
            List of created SnapVecEbd objects
        """
        chunk_records = []

        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_record = SnapVecEbd(
                agent_id=agent_id,
                file_id=file_id,
                content=chunk_text,
                embedding=embedding,
                chunk_index=idx,
                created_by=user_email,
                updated_by=user_email,
            )
            self.db.add(chunk_record)
            chunk_records.append(chunk_record)

        await self.db.commit()
        return chunk_records

    # ------------------------------------------------------------------
    # Similarity search
    # ------------------------------------------------------------------

    async def similarity_search(
        self,
        agent_id: UUID,
        query_embedding: List[float],
        top_k: int = 5,
        similarity_threshold: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search using cosine similarity within a single Agent.

        Uses CAST() instead of :: to avoid asyncpg parameter binding conflict.
        """
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        query = text("""
            SELECT
                id, agent_id, file_id, content, chunk_index, extra,
                (1 - (embedding <=> CAST(:embedding AS vector))) as similarity
            FROM snap_vec_ebd
            WHERE agent_id = :agent_id
                AND use_yn = 'Y'
                AND (1 - (embedding <=> CAST(:embedding AS vector))) >= :threshold
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """)

        result = await self.db.execute(
            query,
            {
                "embedding": embedding_str,
                "agent_id": str(agent_id),
                "threshold": similarity_threshold,
                "limit": top_k,
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

    async def similarity_search_multi(
        self,
        agent_ids: List[UUID],
        query_embedding: List[float],
        top_k: int = 5,
        similarity_threshold: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search across multiple Agents.

        Returns top_k results globally, sorted by similarity score.
        """
        if not agent_ids:
            return []

        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        agent_id_list = ", ".join(f"'{str(aid)}'" for aid in agent_ids)

        query = text(f"""
            SELECT
                id, agent_id, file_id, content, chunk_index, extra,
                (1 - (embedding <=> CAST(:embedding AS vector))) as similarity
            FROM snap_vec_ebd
            WHERE agent_id IN ({agent_id_list})
                AND use_yn = 'Y'
                AND (1 - (embedding <=> CAST(:embedding AS vector))) >= :threshold
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """)

        result = await self.db.execute(
            query,
            {
                "embedding": embedding_str,
                "threshold": similarity_threshold,
                "limit": top_k,
            },
        )

        rows = result.fetchall()
        return [
            {
                "id": str(row.id),
                "agent_id": str(row.agent_id),
                "content": row.content,
                "chunk_index": row.chunk_index,
                "file_id": str(row.file_id),
                "similarity": round(float(row.similarity), 4),
                "extra": row.extra,
            }
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Count & delete
    # ------------------------------------------------------------------

    async def get_chunk_count(self, agent_id: UUID) -> int:
        """Get total number of active chunks for an Agent."""
        result = await self.db.execute(
            text("""
                SELECT COUNT(*) FROM snap_vec_ebd
                WHERE agent_id = :agent_id AND use_yn = 'Y'
            """),
            {"agent_id": str(agent_id)},
        )
        return result.scalar() or 0

    async def delete_by_agent(self, agent_id: UUID) -> int:
        """Soft delete all vectors for an Agent."""
        result = await self.db.execute(
            text("""
                UPDATE snap_vec_ebd
                SET use_yn = 'N', updated_at = now()
                WHERE agent_id = :agent_id AND use_yn = 'Y'
            """),
            {"agent_id": str(agent_id)},
        )
        await self.db.commit()
        return result.rowcount

    async def delete_by_file(self, agent_id: UUID, file_id: UUID) -> int:
        """Soft delete all vectors for a specific file within an Agent."""
        result = await self.db.execute(
            text("""
                UPDATE snap_vec_ebd
                SET use_yn = 'N', updated_at = now()
                WHERE agent_id = :agent_id AND file_id = :file_id AND use_yn = 'Y'
            """),
            {"agent_id": str(agent_id), "file_id": str(file_id)},
        )
        await self.db.commit()
        return result.rowcount
