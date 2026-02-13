"""
RAG vector search tool for retrieving relevant document chunks.
"""
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.base import BaseTool
from app.db.models import Agent, User

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

            # Vector similarity search via VectorStore
            from app.rag.vectorstore import VectorStore

            vector_store = VectorStore(self.db)
            results = await vector_store.similarity_search(
                agent_id=self.agent.id,
                query_embedding=embedding,
                top_k=top_k,
                similarity_threshold=threshold,
            )

            chunks = []
            content_parts = []

            for row in results:
                chunks.append(row)
                content_parts.append(row["content"])

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
