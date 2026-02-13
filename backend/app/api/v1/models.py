"""
User-facing model listing endpoint.
Returns only active models registered by admin.
"""
from typing import Optional

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DBSession
from app.schemas.model import ModelListResponse
from app.services.model_service import ModelService

router = APIRouter(prefix="/models", tags=["Models"])


@router.get("/", response_model=ModelListResponse)
async def list_models(
    current_user: CurrentUser,
    db: DBSession,
    model_type: Optional[str] = Query(None, description="Filter by model type: 'llm' or 'embedding'"),
):
    """List active models available for agent configuration."""
    service = ModelService(db)
    models = await service.list_active_models(model_type=model_type)
    return ModelListResponse(models=models, total=len(models))
