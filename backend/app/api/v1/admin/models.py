"""
Admin Model CRUD + test + Open Router available models listing.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import AdminUser, DBSession
from app.schemas.model import (
    ModelCreate,
    ModelDeleteResponse,
    ModelListResponse,
    ModelResponse,
    ModelTestRequest,
    ModelTestResponse,
    ModelUpdate,
    OpenRouterModelListResponse,
)
from app.services.model_service import ModelService


router = APIRouter(prefix="/models", tags=["Admin - Models"])


@router.post("/", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    data: ModelCreate,
    admin_user: AdminUser,
    db: DBSession,
):
    """Register a new model (admin only)."""
    service = ModelService(db)
    model = await service.create_model(admin_user, data)
    return model


@router.get("/", response_model=ModelListResponse)
async def list_models(
    admin_user: AdminUser,
    db: DBSession,
    model_type: Optional[str] = Query(None),
):
    """List all registered models."""
    service = ModelService(db)
    models = await service.list_models(model_type=model_type)
    return ModelListResponse(models=models, total=len(models))


@router.get("/openrouter/available", response_model=OpenRouterModelListResponse)
async def list_openrouter_models(
    admin_user: AdminUser,
    db: DBSession,
):
    """List available models from Open Router API."""
    service = ModelService(db)
    models = await service.list_openrouter_available_models()
    return OpenRouterModelListResponse(models=models, total=len(models))


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: UUID,
    admin_user: AdminUser,
    db: DBSession,
):
    """Get model details by ID."""
    service = ModelService(db)
    model = await service.get_model(model_id)
    return model


@router.put("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: UUID,
    data: ModelUpdate,
    admin_user: AdminUser,
    db: DBSession,
):
    """Update a registered model."""
    service = ModelService(db)
    model = await service.update_model(model_id, data)
    return model


@router.delete("/{model_id}", response_model=ModelDeleteResponse)
async def delete_model(
    model_id: UUID,
    admin_user: AdminUser,
    db: DBSession,
):
    """Delete a registered model (soft delete)."""
    service = ModelService(db)
    await service.delete_model(model_id)
    return ModelDeleteResponse(message="Model deleted successfully")


@router.post("/{model_id}/test", response_model=ModelTestResponse)
async def test_model(
    model_id: UUID,
    data: ModelTestRequest,
    admin_user: AdminUser,
    db: DBSession,
):
    """Test a model with a sample prompt."""
    service = ModelService(db)
    result = await service.test_model(model_id, data)
    return result
