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
from app.rag.vectorstore import VectorStore

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing embeddings."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _resolve_api_settings(self) -> tuple:
        """Resolve OpenRouter API key and base URL (DB first, env fallback)."""
        api_key = settings.openrouter_api_key
        base_url = settings.openrouter_base_url

        try:
            from app.db.models import SystemSetting
            from app.core.encryption import decrypt_api_key

            # Use nested transaction (savepoint) to avoid aborting the main transaction
            async with self.db.begin_nested():
                result = await self.db.execute(
                    select(SystemSetting).where(
                        SystemSetting.setting_key == "openrouter_api_key",
                        SystemSetting.use_yn == "Y",
                    )
                )
                row = result.scalar_one_or_none()
                if row:
                    api_key = decrypt_api_key(row.setting_value) if row.is_encrypted else row.setting_value

                result = await self.db.execute(
                    select(SystemSetting).where(
                        SystemSetting.setting_key == "openrouter_base_url",
                        SystemSetting.use_yn == "Y",
                    )
                )
                row = result.scalar_one_or_none()
                if row:
                    base_url = row.setting_value
        except Exception:
            pass

        return api_key, base_url

    async def embed_query(
        self, text: str, model_id: Optional[UUID] = None
    ) -> Optional[List[float]]:
        """
        Generate embedding for a query text via OpenRouter API.

        Args:
            text: Text to embed
            model_id: Optional model ID to use

        Returns:
            List of floats representing the embedding vector
        """
        embedding_model = "openai/text-embedding-3-small"

        if model_id:
            result = await self.db.execute(
                select(Model).where(Model.id == model_id, Model.use_yn == "Y")
            )
            model = result.scalar_one_or_none()
            if model:
                embedding_model = model.model_id

        api_key, base_url = await self._resolve_api_settings()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{base_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {api_key}",
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

        # Ensure Agent partition exists before inserting embeddings
        vector_store = VectorStore(self.db)
        await vector_store.create_partition(agent.id)

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

            # Generate embeddings
            chunk_texts = [c["content"] for c in chunks]
            chunk_embeddings = []
            for chunk_text in chunk_texts:
                embedding = await self.embed_query(
                    chunk_text, model_id=agent.embedding_model_id
                )
                if embedding:
                    chunk_embeddings.append(embedding)
                else:
                    chunk_embeddings.append(None)

            # Store valid embeddings via VectorStore
            valid_chunks = []
            valid_embeddings = []
            for chunk_data, emb in zip(chunks, chunk_embeddings):
                if emb is not None:
                    valid_chunks.append(chunk_data["content"])
                    valid_embeddings.append(emb)

            if valid_chunks:
                await vector_store.add_chunks(
                    agent_id=agent.id,
                    file_id=file_id,
                    chunks=valid_chunks,
                    embeddings=valid_embeddings,
                    user_email=user.email,
                )
                chunks_created += len(valid_chunks)

            files_processed += 1

        # Create IVFFlat vector index after inserting data
        if chunks_created > 0:
            try:
                lists = min(100, max(1, chunks_created // 10))
                await vector_store.create_vector_index(agent.id, lists=lists)
            except Exception as e:
                logger.warning(f"Vector index creation deferred: {e}")

        return {
            "files_processed": files_processed,
            "chunks_created": chunks_created,
        }
