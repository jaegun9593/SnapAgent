"""
Retriever module for combining search results from multiple sources.
"""
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.embedding import EmbeddingService
from app.rag.vectorstore import VectorStore

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieve relevant documents using vector similarity search."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService(db)
        self.vector_store = VectorStore(db)

    async def retrieve(
        self,
        query: str,
        agent_id: UUID,
        embedding_model_id: Optional[UUID] = None,
        top_k: int = 5,
        threshold: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks for a query.

        Args:
            query: The search query
            agent_id: Agent ID to search within
            embedding_model_id: Model to use for query embedding
            top_k: Number of results to return
            threshold: Minimum similarity threshold

        Returns:
            List of matching chunks with metadata
        """
        # Generate query embedding
        embedding = await self.embedding_service.embed_query(
            query, model_id=embedding_model_id
        )
        if not embedding:
            logger.error("Failed to generate query embedding")
            return []

        # Search vectors
        results = await self.vector_store.similarity_search(
            agent_id=agent_id,
            query_embedding=embedding,
            top_k=top_k,
            similarity_threshold=threshold,
        )

        return results
