"""
Pydantic schemas for agent endpoints.
"""
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AgentToolConfig(BaseModel):
    """Tool configuration within an agent."""

    tool_type: Literal[
        "rag", "web_search", "tavily_search", "wikipedia", "arxiv",
        "calculator", "python_repl", "web_scraper", "custom_api"
    ] = Field(..., description="Type of tool")
    tool_config: Optional[Dict[str, Any]] = Field(None, description="Tool-specific configuration")
    is_enabled: bool = Field(True, description="Whether the tool is enabled")
    sort_order: int = Field(0, description="Sort order")


class AgentCreate(BaseModel):
    """Schema for creating a new agent."""

    name: str = Field(..., max_length=255, description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    system_prompt: Optional[str] = Field(None, description="System prompt")
    template_id: Optional[UUID] = Field(None, description="Template ID to base agent on")
    model_id: Optional[UUID] = Field(None, description="LLM model ID")
    embedding_model_id: Optional[UUID] = Field(None, description="Embedding model ID for RAG")
    config: Optional[Dict[str, Any]] = Field(None, description="Agent configuration")
    tools: Optional[List[AgentToolConfig]] = Field(None, description="Tools to attach")
    file_ids: Optional[List[UUID]] = Field(None, description="File IDs for RAG")
    sub_agent_ids: Optional[List[UUID]] = Field(None, description="Sub-agent IDs")
    status: Optional[str] = Field("draft", description="Agent status")


class AgentUpdate(BaseModel):
    """Schema for updating an existing agent."""

    name: Optional[str] = Field(None, max_length=255, description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    system_prompt: Optional[str] = Field(None, description="System prompt")
    template_id: Optional[UUID] = Field(None, description="Template ID")
    model_id: Optional[UUID] = Field(None, description="LLM model ID")
    embedding_model_id: Optional[UUID] = Field(None, description="Embedding model ID")
    config: Optional[Dict[str, Any]] = Field(None, description="Agent configuration")
    tools: Optional[List[AgentToolConfig]] = Field(None, description="Tools to update")
    file_ids: Optional[List[UUID]] = Field(None, description="File IDs for RAG")
    sub_agent_ids: Optional[List[UUID]] = Field(None, description="Sub-agent IDs")
    status: Optional[str] = Field(None, description="Agent status")


class AgentToolResponse(BaseModel):
    """Response schema for agent tool."""

    id: UUID
    tool_type: str
    tool_config: Optional[Dict[str, Any]]
    is_enabled: bool
    sort_order: int

    class Config:
        from_attributes = True


class AgentResponse(BaseModel):
    """Response schema for agent."""

    id: UUID
    name: str
    description: Optional[str]
    system_prompt: Optional[str]
    template_id: Optional[UUID]
    model_id: Optional[UUID]
    embedding_model_id: Optional[UUID]
    config: Optional[Dict[str, Any]]
    status: str
    tools: Optional[List[AgentToolResponse]] = None
    file_ids: Optional[List[UUID]] = None
    sub_agent_ids: Optional[List[UUID]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    """Response schema for agent list."""

    agents: List[AgentResponse]
    total: int


class AgentDeleteResponse(BaseModel):
    """Response schema for agent deletion."""

    message: str = Field(default="Agent deleted successfully")


class AgentStatusResponse(BaseModel):
    """Response schema for agent status."""

    status: str
    tool_count: int = 0
    file_count: int = 0
    vector_count: int = 0
    is_ready: bool = False


class AgentTestRequest(BaseModel):
    """Request schema for testing an agent."""

    query: str = Field(..., description="Test query to send to the agent")


class AgentTestResponse(BaseModel):
    """Response schema for agent test result."""

    success: bool
    response: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    token_usage: Optional[Dict[str, int]] = None
    latency_ms: Optional[int] = None
    error: Optional[str] = None


class AgentProcessRequest(BaseModel):
    """Request schema for processing agent files."""

    force: bool = Field(False, description="Force re-processing of all files")


class AgentProcessResponse(BaseModel):
    """Response schema for agent file processing."""

    message: str
    files_processed: int = 0
    chunks_created: int = 0
    status: str = "completed"
