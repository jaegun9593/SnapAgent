"""
Pydantic schemas for model endpoints.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ModelCreate(BaseModel):
    """Schema for creating a new model."""

    name: str = Field(..., max_length=255, description="Display name")
    provider: str = Field("openrouter", description="Provider name")
    model_id: str = Field(..., max_length=255, description="Model identifier (e.g. openai/gpt-4o)")
    model_type: str = Field(..., description="Model type: 'llm' or 'embedding'")
    config: Optional[Dict[str, Any]] = Field(None, description="Model configuration")
    pricing: Optional[Dict[str, Any]] = Field(None, description="Pricing info per token")
    is_active: bool = Field(True, description="Whether the model is active")


class ModelUpdate(BaseModel):
    """Schema for updating a model."""

    name: Optional[str] = Field(None, max_length=255, description="Display name")
    provider: Optional[str] = Field(None, description="Provider name")
    model_id: Optional[str] = Field(None, max_length=255, description="Model identifier")
    model_type: Optional[str] = Field(None, description="Model type")
    config: Optional[Dict[str, Any]] = Field(None, description="Model configuration")
    pricing: Optional[Dict[str, Any]] = Field(None, description="Pricing info")
    is_active: Optional[bool] = Field(None, description="Active status")


class ModelResponse(BaseModel):
    """Response schema for model."""

    id: UUID
    name: str
    provider: str
    model_id: str
    model_type: str
    config: Optional[Dict[str, Any]]
    pricing: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelListResponse(BaseModel):
    """Response schema for model list."""

    models: List[ModelResponse]
    total: int


class ModelDeleteResponse(BaseModel):
    """Response schema for model deletion."""

    message: str = Field(default="Model deleted successfully")


class ModelTestRequest(BaseModel):
    """Request schema for testing a model."""

    prompt: str = Field("Hello, how are you?", description="Test prompt")


class ModelTestResponse(BaseModel):
    """Response schema for model test result."""

    success: bool
    message: str
    response_time: Optional[int] = None
    error: Optional[str] = None


class OpenRouterModel(BaseModel):
    """Schema for an available Open Router model."""

    id: str
    name: str
    description: Optional[str] = None
    pricing: Optional[Dict[str, Any]] = None
    context_length: Optional[int] = None


class OpenRouterModelListResponse(BaseModel):
    """Response schema for Open Router available models."""

    models: List[OpenRouterModel]
    total: int
