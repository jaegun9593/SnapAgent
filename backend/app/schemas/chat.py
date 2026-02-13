"""
Pydantic schemas for chat endpoints.
"""
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    """Schema for creating a new chat session."""

    agent_id: UUID = Field(..., description="Agent ID to use for this session")
    title: Optional[str] = Field(None, max_length=255, description="Session title")


class ChatSessionResponse(BaseModel):
    """Response schema for chat session information."""

    id: UUID
    agent_id: UUID
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatSessionListResponse(BaseModel):
    """Response schema for chat session list."""

    sessions: List[ChatSessionResponse]
    total: int


class ChatMessageCreate(BaseModel):
    """Schema for creating a new chat message."""

    content: str = Field(..., min_length=1, description="Message content")
    config: Optional[Dict[str, Any]] = Field(None, description="Runtime config overrides")


class ChatMessageResponse(BaseModel):
    """Response schema for chat message."""

    id: UUID
    session_id: UUID
    role: Literal["user", "assistant", "system"]
    content: str
    tool_calls: Optional[Any] = None
    token_usage: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageListResponse(BaseModel):
    """Response schema for chat message list."""

    messages: List[ChatMessageResponse]
    total: int


class ChatSessionDeleteResponse(BaseModel):
    """Response schema for chat session deletion."""

    message: str = Field(default="Chat session deleted successfully")
