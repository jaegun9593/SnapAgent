"""
Pydantic schemas for user endpoints.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    full_name: Optional[str] = Field(None, max_length=100, description="User full name")


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    full_name: Optional[str] = Field(None, max_length=100, description="User full name")
    password: Optional[str] = Field(None, min_length=8, description="New password")


class UserResponse(BaseModel):
    """Schema for user response."""

    email: EmailStr
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserDeleteResponse(BaseModel):
    """Response schema for user deletion."""

    message: str = Field(default="User deleted successfully")
