"""
Pydantic schemas for template endpoints.
"""
from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TemplateCreate(BaseModel):
    """Schema for creating a new template."""

    name: str = Field(..., max_length=255, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    tool_config: Optional[Any] = Field(None, description="Pre-configured tool settings")
    system_prompt_template: Optional[str] = Field(None, description="System prompt template text")
    category: Optional[str] = Field(None, max_length=100, description="Template category")
    is_system: bool = Field(False, description="Whether this is a system template")


class TemplateUpdate(BaseModel):
    """Schema for updating an existing template."""

    name: Optional[str] = Field(None, max_length=255, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    tool_config: Optional[Any] = Field(None, description="Pre-configured tool settings")
    system_prompt_template: Optional[str] = Field(None, description="System prompt template text")
    category: Optional[str] = Field(None, max_length=100, description="Template category")


class TemplateResponse(BaseModel):
    """Response schema for template."""

    id: UUID
    name: str
    description: Optional[str]
    tool_config: Optional[Any]
    system_prompt_template: Optional[str]
    category: Optional[str]
    is_system: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """Response schema for template list."""

    templates: List[TemplateResponse]
    total: int


class TemplateDeleteResponse(BaseModel):
    """Response schema for template deletion."""

    message: str = Field(default="Template deleted successfully")
