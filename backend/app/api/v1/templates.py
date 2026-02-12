"""
Template API endpoints.
- GET: Any authenticated user can list/view templates.
- POST/PUT/DELETE: Admin only.
"""
from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import AdminUser, CurrentUser, DBSession
from app.schemas.template import (
    TemplateCreate,
    TemplateListResponse,
    TemplateResponse,
    TemplateUpdate,
    TemplateDeleteResponse,
)
from app.services.template_service import TemplateService


router = APIRouter(prefix="/templates", tags=["Templates"])


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    data: TemplateCreate,
    current_user: AdminUser,
    db: DBSession,
):
    """Create a new template (admin only)."""
    service = TemplateService(db)
    template = await service.create_template(current_user, data)
    return template


@router.get("/", response_model=TemplateListResponse)
async def list_templates(
    current_user: CurrentUser,
    db: DBSession,
):
    """List all templates (system + user's own)."""
    service = TemplateService(db)
    templates = await service.list_templates(current_user)
    return TemplateListResponse(templates=templates, total=len(templates))


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """Get template details by ID."""
    service = TemplateService(db)
    template = await service.get_template(template_id)
    return template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: UUID,
    data: TemplateUpdate,
    current_user: AdminUser,
    db: DBSession,
):
    """Update an existing template (admin only)."""
    service = TemplateService(db)
    template = await service.update_template(current_user, template_id, data)
    return template


@router.delete("/{template_id}", response_model=TemplateDeleteResponse)
async def delete_template(
    template_id: UUID,
    current_user: AdminUser,
    db: DBSession,
):
    """Delete a template - soft delete (admin only)."""
    service = TemplateService(db)
    await service.delete_template(current_user, template_id)
    return TemplateDeleteResponse(message="Template deleted successfully")
