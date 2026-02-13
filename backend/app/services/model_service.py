"""
Model service for admin model management and Open Router integration.
"""
import logging
import time
from typing import List, Optional
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import NotFoundError
from app.db.models import Model, SystemSetting, User
from app.schemas.model import (
    ModelCreate,
    ModelResponse,
    ModelTestRequest,
    ModelTestResponse,
    ModelUpdate,
    OpenRouterModel,
)

logger = logging.getLogger(__name__)


class ModelService:
    """Service for model operations."""

    def __init__(self, db: Optional[AsyncSession]):
        self.db = db

    async def _get_setting_value(self, key: str) -> Optional[str]:
        """Get a decrypted setting value from DB. Returns None if no db or not found."""
        if not self.db:
            return None
        from app.core.encryption import decrypt_api_key

        result = await self.db.execute(
            select(SystemSetting).where(
                SystemSetting.setting_key == key,
                SystemSetting.use_yn == "Y",
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            return None
        if row.is_encrypted:
            try:
                return decrypt_api_key(row.setting_value)
            except ValueError:
                logger.error("Failed to decrypt setting: %s", key)
                return None
        return row.setting_value

    async def _get_openrouter_api_key(self) -> Optional[str]:
        """Get OpenRouter API key: DB first, then env fallback."""
        db_val = await self._get_setting_value("openrouter_api_key")
        return db_val or settings.openrouter_api_key

    async def _get_openrouter_base_url(self) -> str:
        """Get OpenRouter base URL: DB first, then env fallback."""
        db_val = await self._get_setting_value("openrouter_base_url")
        return db_val or settings.openrouter_base_url

    async def create_model(self, user: User, data: ModelCreate) -> ModelResponse:
        """Register a new model."""
        model = Model(
            name=data.name,
            provider=data.provider,
            model_id=data.model_id,
            model_type=data.model_type,
            config=data.config,
            pricing=data.pricing,
            is_active=data.is_active,
            created_by=user.email,
            updated_by=user.email,
        )
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return ModelResponse.model_validate(model)

    async def list_models(self, model_type: Optional[str] = None) -> List[ModelResponse]:
        """List all registered models."""
        query = select(Model).where(Model.use_yn == "Y")
        if model_type:
            query = query.where(Model.model_type == model_type)
        query = query.order_by(Model.name)

        result = await self.db.execute(query)
        models = result.scalars().all()
        return [ModelResponse.model_validate(m) for m in models]

    async def list_active_models(self, model_type: Optional[str] = None) -> List[ModelResponse]:
        """List only active models (for user-facing endpoints)."""
        query = select(Model).where(Model.use_yn == "Y", Model.is_active == True)
        if model_type:
            query = query.where(Model.model_type == model_type)
        query = query.order_by(Model.name)

        result = await self.db.execute(query)
        models = result.scalars().all()
        return [ModelResponse.model_validate(m) for m in models]

    async def get_model(self, model_id: UUID) -> ModelResponse:
        """Get model details."""
        result = await self.db.execute(
            select(Model).where(Model.id == model_id, Model.use_yn == "Y")
        )
        model = result.scalar_one_or_none()
        if not model:
            raise NotFoundError(f"Model not found: {model_id}")
        return ModelResponse.model_validate(model)

    async def update_model(self, model_id: UUID, data: ModelUpdate) -> ModelResponse:
        """Update a model."""
        result = await self.db.execute(
            select(Model).where(Model.id == model_id, Model.use_yn == "Y")
        )
        model = result.scalar_one_or_none()
        if not model:
            raise NotFoundError(f"Model not found: {model_id}")

        for field in ["name", "provider", "model_id", "model_type", "config", "pricing", "is_active"]:
            value = getattr(data, field, None)
            if value is not None:
                setattr(model, field, value)

        await self.db.commit()
        await self.db.refresh(model)
        return ModelResponse.model_validate(model)

    async def delete_model(self, model_id: UUID) -> None:
        """Soft delete a model."""
        result = await self.db.execute(
            select(Model).where(Model.id == model_id, Model.use_yn == "Y")
        )
        model = result.scalar_one_or_none()
        if not model:
            raise NotFoundError(f"Model not found: {model_id}")
        model.use_yn = "N"
        await self.db.commit()

    async def test_model(self, model_id: UUID, data: ModelTestRequest) -> ModelTestResponse:
        """Test a model with a sample prompt."""
        result = await self.db.execute(
            select(Model).where(Model.id == model_id, Model.use_yn == "Y")
        )
        model = result.scalar_one_or_none()
        if not model:
            raise NotFoundError(f"Model not found: {model_id}")

        try:
            api_key = await self._get_openrouter_api_key()
            base_url = await self._get_openrouter_base_url()
            if not api_key:
                return ModelTestResponse(
                    success=False,
                    message="Model test failed",
                    error="OpenRouter API key is not configured",
                )

            start_time = time.time()

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model.model_id,
                        "messages": [{"role": "user", "content": data.prompt}],
                        "max_tokens": 100,
                    },
                )
                response.raise_for_status()

            elapsed = int((time.time() - start_time) * 1000)
            return ModelTestResponse(
                success=True,
                message="Model test successful",
                response_time=elapsed,
            )
        except Exception as e:
            logger.error(f"Model test failed: {e}")
            return ModelTestResponse(
                success=False,
                message="Model test failed",
                error=str(e),
            )

    async def list_openrouter_available_models(self) -> List[OpenRouterModel]:
        """Fetch available models from Open Router API."""
        try:
            api_key = await self._get_openrouter_api_key()
            base_url = await self._get_openrouter_base_url()
            if not api_key:
                logger.warning("OpenRouter API key is not configured")
                return []

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{base_url}/models",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                    },
                )
                response.raise_for_status()
                data = response.json()

            models = []
            for item in data.get("data", []):
                models.append(
                    OpenRouterModel(
                        id=item.get("id", ""),
                        name=item.get("name", ""),
                        description=item.get("description"),
                        pricing=item.get("pricing"),
                        context_length=item.get("context_length"),
                    )
                )
            return models
        except Exception as e:
            logger.error(f"Failed to fetch Open Router models: {e}")
            return []
