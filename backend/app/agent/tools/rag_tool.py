"""
RAG vector search tool for retrieving relevant document chunks.
"""
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.base import BaseTool
from app.db.models import Agent, AgentFile, File, User
from app.db.vector_models import SnapVecEbd

logger = logging.getLogger(__name__)


class RAGTool(BaseTool):
    """RAG tool for searching uploaded document vectors."""

    def __init__(self, db: AsyncSession, agent: Agent, user: User):
        self.db = db
        self.agent = agent
        self.user = user

    @property
    def name(self) -> str:
        return "rag_search"

    @property
    def description(self) -> str:
        return "Search uploaded documents using vector similarity"

    async def execute(
        self, query: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute RAG search."""
        return await self.search(query, config=config)

    async def search(
        self, query: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search document vectors for relevant chunks.

        Args:
            query: The search query
            config: Configuration with top_k, similarity_threshold

        Returns:
            Dict with content string and chunks list
        """
        top_k = (config or {}).get("top_k", 5)
        threshold = (config or {}).get("similarity_threshold", 0.3)

        try:
            # Get query embedding
            embedding = await self._get_embedding(query)
            if not embedding:
                return {"content": "Failed to generate embedding for query", "chunks": []}

            # Vector similarity search
            results = await self.db.execute(
                text("""
                    SELECT
                        sve.id,
                        sve.content,
                        sve.chunk_index,
                        sve.file_id,
                        sve.extra,
                        1 - (sve.embedding <=> :embedding::vector) as similarity
                    FROM snap_vec_ebd sve
                    WHERE sve.agent_id = :agent_id
                      AND sve.use_yn = 'Y'
                      AND 1 - (sve.embedding <=> :embedding::vector) >= :threshold
                    ORDER BY similarity DESC
                    LIMIT :top_k
                """),
                {
                    "embedding": str(embedding),
                    "agent_id": str(self.agent.id),
                    "threshold": threshold,
                    "top_k": top_k,
                },
            )

            rows = results.fetchall()
            chunks = []
            content_parts = []

            for row in rows:
                chunk_data = {
                    "id": str(row.id),
                    "content": row.content,
                    "chunk_index": row.chunk_index,
                    "file_id": str(row.file_id),
                    "similarity": round(float(row.similarity), 4),
                    "extra": row.extra,
                }
                chunks.append(chunk_data)
                content_parts.append(row.content)

            content = "\n\n---\n\n".join(content_parts) if content_parts else "No relevant documents found"

            return {"content": content, "chunks": chunks}

        except Exception as e:
            logger.error(f"RAG search error: {e}")
            return {"content": f"RAG search failed: {str(e)}", "chunks": []}

    async def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for query text using the agent's embedding model."""
        try:
            from app.rag.embedding import EmbeddingService

            embedding_service = EmbeddingService(self.db)
            embedding = await embedding_service.embed_query(
                text, model_id=self.agent.embedding_model_id
            )
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None
