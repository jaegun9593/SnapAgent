"""
Template service for CRUD operations.
"""
import logging
from typing import List
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError
from app.db.models import Template, User
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for template operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_template(self, user: User, data: TemplateCreate) -> TemplateResponse:
        """Create a new template."""
        template = Template(
            name=data.name,
            description=data.description,
            tool_config=data.tool_config,
            system_prompt_template=data.system_prompt_template,
            category=data.category,
            is_system=data.is_system if user.role == "admin" else False,
            created_by=user.email,
            updated_by=user.email,
        )
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return TemplateResponse.model_validate(template)

    async def list_templates(self, user: User) -> List[TemplateResponse]:
        """List all templates: system templates + user's own templates."""
        result = await self.db.execute(
            select(Template)
            .where(
                Template.use_yn == "Y",
                or_(
                    Template.is_system == True,
                    Template.created_by == user.email,
                ),
            )
            .order_by(Template.is_system.desc(), Template.updated_at.desc())
        )
        templates = result.scalars().all()
        return [TemplateResponse.model_validate(t) for t in templates]

    async def get_template(self, template_id: UUID) -> TemplateResponse:
        """Get template details."""
        result = await self.db.execute(
            select(Template).where(Template.id == template_id, Template.use_yn == "Y")
        )
        template = result.scalar_one_or_none()
        if not template:
            raise NotFoundError(f"Template not found: {template_id}")
        return TemplateResponse.model_validate(template)

    async def update_template(
        self, user: User, template_id: UUID, data: TemplateUpdate
    ) -> TemplateResponse:
        """Update an existing template."""
        result = await self.db.execute(
            select(Template).where(Template.id == template_id, Template.use_yn == "Y")
        )
        template = result.scalar_one_or_none()
        if not template:
            raise NotFoundError(f"Template not found: {template_id}")

        if template.is_system and user.role != "admin":
            raise ForbiddenError("Cannot modify system templates")

        if not template.is_system and template.created_by != user.email:
            raise ForbiddenError("Cannot modify other user's templates")

        for field in ["name", "description", "tool_config", "system_prompt_template", "category"]:
            value = getattr(data, field, None)
            if value is not None:
                setattr(template, field, value)

        template.updated_by = user.email
        await self.db.commit()
        await self.db.refresh(template)
        return TemplateResponse.model_validate(template)

    async def delete_template(self, user: User, template_id: UUID) -> None:
        """Soft delete a template."""
        result = await self.db.execute(
            select(Template).where(Template.id == template_id, Template.use_yn == "Y")
        )
        template = result.scalar_one_or_none()
        if not template:
            raise NotFoundError(f"Template not found: {template_id}")

        if template.is_system and user.role != "admin":
            raise ForbiddenError("Cannot delete system templates")

        template.use_yn = "N"
        template.updated_by = user.email
        await self.db.commit()
