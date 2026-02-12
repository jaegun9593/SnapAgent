"""
Agent API endpoints - Full CRUD + test + process + status.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.agent import (
    AgentCreate,
    AgentListResponse,
    AgentResponse,
    AgentUpdate,
    AgentDeleteResponse,
    AgentStatusResponse,
    AgentTestRequest,
    AgentTestResponse,
    AgentProcessRequest,
    AgentProcessResponse,
)
from app.services.agent_service import AgentService


router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    data: AgentCreate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Create a new agent."""
    service = AgentService(db)
    agent = await service.create_agent(current_user, data)
    return agent


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    current_user: CurrentUser,
    db: DBSession,
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """List all agents for the current user."""
    service = AgentService(db)
    agents = await service.list_agents(current_user, status_filter=status_filter)
    return AgentListResponse(agents=agents, total=len(agents))


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """Get agent details by ID."""
    service = AgentService(db)
    agent = await service.get_agent(current_user, agent_id)
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    data: AgentUpdate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Update an existing agent."""
    service = AgentService(db)
    agent = await service.update_agent(current_user, agent_id, data)
    return agent


@router.delete("/{agent_id}", response_model=AgentDeleteResponse)
async def delete_agent(
    agent_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """Delete an agent (soft delete)."""
    service = AgentService(db)
    await service.delete_agent(current_user, agent_id)
    return AgentDeleteResponse(message="Agent deleted successfully")


@router.get("/{agent_id}/status", response_model=AgentStatusResponse)
async def get_agent_status(
    agent_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """Get current status of an agent."""
    service = AgentService(db)
    status_info = await service.get_agent_status(current_user, agent_id)
    return status_info


@router.post("/{agent_id}/test", response_model=AgentTestResponse)
async def test_agent(
    agent_id: UUID,
    data: AgentTestRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    """Test an agent with a sample query."""
    service = AgentService(db)
    result = await service.test_agent(current_user, agent_id, data)
    return result


@router.post("/{agent_id}/process", response_model=AgentProcessResponse)
async def process_agent(
    agent_id: UUID,
    data: AgentProcessRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    """Process agent files (chunking + embedding)."""
    service = AgentService(db)
    result = await service.process_agent(current_user, agent_id, data)
    return result
