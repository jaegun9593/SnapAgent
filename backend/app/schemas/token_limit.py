"""
Pydantic schemas for token limit endpoints.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TokenLimitCreate(BaseModel):
    """Schema for creating a new token limit."""

    user_email: Optional[str] = Field(None, description="User email (null for global)")
    limit_type: str = Field(..., description="Limit type: 'daily', 'monthly', 'total'")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens allowed")
    max_api_calls: Optional[int] = Field(None, description="Maximum API calls allowed")
    is_active: bool = Field(True, description="Whether the limit is active")


class TokenLimitUpdate(BaseModel):
    """Schema for updating a token limit."""

    max_tokens: Optional[int] = Field(None, description="Maximum tokens allowed")
    max_api_calls: Optional[int] = Field(None, description="Maximum API calls allowed")
    is_active: Optional[bool] = Field(None, description="Whether the limit is active")


class TokenLimitResponse(BaseModel):
    """Response schema for token limit."""

    id: UUID
    user_email: Optional[str]
    limit_type: str
    max_tokens: Optional[int]
    max_api_calls: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenLimitListResponse(BaseModel):
    """Response schema for token limit list."""

    limits: List[TokenLimitResponse]
    total: int


class TokenLimitDeleteResponse(BaseModel):
    """Response schema for token limit deletion."""

    message: str = Field(default="Token limit deleted successfully")
