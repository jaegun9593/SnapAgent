"""
Embedding service for generating vector embeddings.
"""
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import Agent, AgentFile, File, Model, User
from app.db.vector_models import SnapVecEbd
from app.rag.chunking import TextChunker
from app.rag.parsing import DocumentParser

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing embeddings."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def embed_query(
        self, text: str, model_id: Optional[UUID] = None
    ) -> Optional[List[float]]:
        """
        Generate embedding for a query text.

        Args:
            text: Text to embed
            model_id: Optional model ID to use

        Returns:
            List of floats representing the embedding vector
        """
        embedding_model = "text-embedding-3-small"

        if model_id:
            result = await self.db.execute(
                select(Model).where(Model.id == model_id, Model.use_yn == "Y")
            )
            model = result.scalar_one_or_none()
            if model:
                embedding_model = model.model_id

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{settings.openai_base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": embedding_model,
                        "input": text,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None

    async def process_agent_files(
        self, agent: Agent, user: User, force: bool = False
    ) -> Dict[str, Any]:
        """
        Process all files associated with an agent.

        Args:
            agent: The agent whose files to process
            user: The current user
            force: Force re-processing

        Returns:
            Dict with processing results
        """
        # Get agent files
        result = await self.db.execute(
            select(AgentFile.file_id).where(
                AgentFile.agent_id == agent.id, AgentFile.use_yn == "Y"
            )
        )
        file_ids = [row[0] for row in result.all()]

        if not file_ids:
            return {"files_processed": 0, "chunks_created": 0}

        parser = DocumentParser()
        chunking_config = (agent.config or {}).get("chunking", {})
        chunker = TextChunker(
            chunk_size=chunking_config.get("chunk_size", 1000),
            chunk_overlap=chunking_config.get("chunk_overlap", 200),
        )

        files_processed = 0
        chunks_created = 0

        for file_id in file_ids:
            file_result = await self.db.execute(
                select(File).where(File.id == file_id)
            )
            file_record = file_result.scalar_one_or_none()
            if not file_record:
                continue

            # Parse document
            text = await parser.parse(file_record.file_path, file_record.mime_type)
            if not text:
                continue

            # Chunk text
            chunks = chunker.chunk(text)

            # Generate embeddings and store
            for chunk_data in chunks:
                embedding = await self.embed_query(
                    chunk_data["content"], model_id=agent.embedding_model_id
                )
                if embedding:
                    vec_record = SnapVecEbd(
                        agent_id=agent.id,
                        file_id=file_id,
                        content=chunk_data["content"],
                        embedding=embedding,
                        chunk_index=chunk_data["chunk_index"],
                        created_by=user.email,
                        updated_by=user.email,
                    )
                    self.db.add(vec_record)
                    chunks_created += 1

            files_processed += 1

        await self.db.commit()

        return {
            "files_processed": files_processed,
            "chunks_created": chunks_created,
        }
