"""
Agent service for CRUD operations and agent management.
"""
import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.db.models import Agent, AgentTool, AgentFile, AgentSubAgent, User
from app.db.vector_models import SnapVecEbd
from app.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentToolResponse,
    AgentStatusResponse,
    AgentTestRequest,
    AgentTestResponse,
    AgentProcessRequest,
    AgentProcessResponse,
)

logger = logging.getLogger(__name__)


class AgentService:
    """Service for agent operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_agent_or_404(self, user: User, agent_id: UUID) -> Agent:
        """Get agent by ID or raise 404."""
        result = await self.db.execute(
            select(Agent).where(
                Agent.id == agent_id,
                Agent.user_email == user.email,
                Agent.use_yn == "Y",
            )
        )
        agent = result.scalar_one_or_none()
        if not agent:
            raise NotFoundError(f"Agent not found: {agent_id}")
        return agent

    async def _get_agent_tools(self, agent_id: UUID) -> List[AgentToolResponse]:
        """Get tools for an agent."""
        result = await self.db.execute(
            select(AgentTool)
            .where(AgentTool.agent_id == agent_id, AgentTool.use_yn == "Y")
            .order_by(AgentTool.sort_order)
        )
        tools = result.scalars().all()
        return [AgentToolResponse.model_validate(t) for t in tools]

    async def _get_agent_file_ids(self, agent_id: UUID) -> List[UUID]:
        """Get file IDs for an agent."""
        result = await self.db.execute(
            select(AgentFile.file_id).where(
                AgentFile.agent_id == agent_id, AgentFile.use_yn == "Y"
            )
        )
        return [row[0] for row in result.all()]

    async def _get_sub_agent_ids(self, agent_id: UUID) -> List[UUID]:
        """Get sub-agent IDs for an agent."""
        result = await self.db.execute(
            select(AgentSubAgent.child_agent_id)
            .where(AgentSubAgent.parent_agent_id == agent_id, AgentSubAgent.use_yn == "Y")
            .order_by(AgentSubAgent.sort_order)
        )
        return [row[0] for row in result.all()]

    async def _build_response(self, agent: Agent) -> AgentResponse:
        """Build full agent response with tools, files, sub-agents."""
        tools = await self._get_agent_tools(agent.id)
        file_ids = await self._get_agent_file_ids(agent.id)
        sub_agent_ids = await self._get_sub_agent_ids(agent.id)
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            system_prompt=agent.system_prompt,
            template_id=agent.template_id,
            model_id=agent.model_id,
            embedding_model_id=agent.embedding_model_id,
            config=agent.config,
            status=agent.status,
            tools=tools,
            file_ids=file_ids,
            sub_agent_ids=sub_agent_ids,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
        )

    async def create_agent(self, user: User, data: AgentCreate) -> AgentResponse:
        """Create a new agent with tools and file associations."""
        agent = Agent(
            user_email=user.email,
            name=data.name,
            description=data.description,
            system_prompt=data.system_prompt,
            template_id=data.template_id,
            model_id=data.model_id,
            embedding_model_id=data.embedding_model_id,
            config=data.config,
            status=data.status or "draft",
            created_by=user.email,
            updated_by=user.email,
        )
        self.db.add(agent)
        await self.db.flush()

        # Add tools
        if data.tools:
            for tool_data in data.tools:
                tool = AgentTool(
                    agent_id=agent.id,
                    tool_type=tool_data.tool_type,
                    tool_config=tool_data.tool_config,
                    is_enabled=tool_data.is_enabled,
                    sort_order=tool_data.sort_order,
                    created_by=user.email,
                    updated_by=user.email,
                )
                self.db.add(tool)

        # Add file associations
        if data.file_ids:
            for file_id in data.file_ids:
                af = AgentFile(
                    agent_id=agent.id,
                    file_id=file_id,
                    created_by=user.email,
                    updated_by=user.email,
                )
                self.db.add(af)

        # Add sub-agent associations
        if data.sub_agent_ids:
            for idx, sub_id in enumerate(data.sub_agent_ids):
                sa = AgentSubAgent(
                    parent_agent_id=agent.id,
                    child_agent_id=sub_id,
                    sort_order=idx,
                    created_by=user.email,
                    updated_by=user.email,
                )
                self.db.add(sa)

        await self.db.commit()
        await self.db.refresh(agent)
        return await self._build_response(agent)

    async def list_agents(
        self, user: User, status_filter: Optional[str] = None
    ) -> List[AgentResponse]:
        """List all agents for a user."""
        query = select(Agent).where(
            Agent.user_email == user.email, Agent.use_yn == "Y"
        )
        if status_filter:
            query = query.where(Agent.status == status_filter)
        query = query.order_by(Agent.updated_at.desc())

        result = await self.db.execute(query)
        agents = result.scalars().all()
        return [await self._build_response(a) for a in agents]

    async def get_agent(self, user: User, agent_id: UUID) -> AgentResponse:
        """Get agent details."""
        agent = await self._get_agent_or_404(user, agent_id)
        return await self._build_response(agent)

    async def update_agent(
        self, user: User, agent_id: UUID, data: AgentUpdate
    ) -> AgentResponse:
        """Update an existing agent."""
        agent = await self._get_agent_or_404(user, agent_id)

        # Update scalar fields
        for field in ["name", "description", "system_prompt", "template_id",
                       "model_id", "embedding_model_id", "config", "status"]:
            value = getattr(data, field, None)
            if value is not None:
                setattr(agent, field, value)

        agent.updated_by = user.email

        # Update tools if provided
        if data.tools is not None:
            # Soft delete old tools
            old_tools_result = await self.db.execute(
                select(AgentTool).where(
                    AgentTool.agent_id == agent_id, AgentTool.use_yn == "Y"
                )
            )
            for old_tool in old_tools_result.scalars().all():
                old_tool.use_yn = "N"

            # Add new tools
            for tool_data in data.tools:
                tool = AgentTool(
                    agent_id=agent.id,
                    tool_type=tool_data.tool_type,
                    tool_config=tool_data.tool_config,
                    is_enabled=tool_data.is_enabled,
                    sort_order=tool_data.sort_order,
                    created_by=user.email,
                    updated_by=user.email,
                )
                self.db.add(tool)

        # Update file associations if provided
        if data.file_ids is not None:
            old_files_result = await self.db.execute(
                select(AgentFile).where(
                    AgentFile.agent_id == agent_id, AgentFile.use_yn == "Y"
                )
            )
            for old_file in old_files_result.scalars().all():
                old_file.use_yn = "N"

            for file_id in data.file_ids:
                af = AgentFile(
                    agent_id=agent.id,
                    file_id=file_id,
                    created_by=user.email,
                    updated_by=user.email,
                )
                self.db.add(af)

        # Update sub-agent associations if provided
        if data.sub_agent_ids is not None:
            old_subs_result = await self.db.execute(
                select(AgentSubAgent).where(
                    AgentSubAgent.parent_agent_id == agent_id, AgentSubAgent.use_yn == "Y"
                )
            )
            for old_sub in old_subs_result.scalars().all():
                old_sub.use_yn = "N"

            for idx, sub_id in enumerate(data.sub_agent_ids):
                sa = AgentSubAgent(
                    parent_agent_id=agent.id,
                    child_agent_id=sub_id,
                    sort_order=idx,
                    created_by=user.email,
                    updated_by=user.email,
                )
                self.db.add(sa)

        await self.db.commit()
        await self.db.refresh(agent)
        return await self._build_response(agent)

    async def delete_agent(self, user: User, agent_id: UUID) -> None:
        """Soft delete an agent."""
        agent = await self._get_agent_or_404(user, agent_id)
        agent.use_yn = "N"
        agent.updated_by = user.email
        await self.db.commit()

    async def get_agent_status(self, user: User, agent_id: UUID) -> AgentStatusResponse:
        """Get status information for an agent."""
        agent = await self._get_agent_or_404(user, agent_id)

        # Count tools
        tool_result = await self.db.execute(
            select(func.count()).where(
                AgentTool.agent_id == agent_id, AgentTool.use_yn == "Y"
            )
        )
        tool_count = tool_result.scalar() or 0

        # Count files
        file_result = await self.db.execute(
            select(func.count()).where(
                AgentFile.agent_id == agent_id, AgentFile.use_yn == "Y"
            )
        )
        file_count = file_result.scalar() or 0

        # Count vectors
        vec_result = await self.db.execute(
            select(func.count()).where(
                SnapVecEbd.agent_id == agent_id, SnapVecEbd.use_yn == "Y"
            )
        )
        vector_count = vec_result.scalar() or 0

        is_ready = agent.status == "active" and agent.model_id is not None

        return AgentStatusResponse(
            status=agent.status,
            tool_count=tool_count,
            file_count=file_count,
            vector_count=vector_count,
            is_ready=is_ready,
        )

    async def test_agent(
        self, user: User, agent_id: UUID, data: AgentTestRequest
    ) -> AgentTestResponse:
        """Test an agent with a sample query."""
        agent = await self._get_agent_or_404(user, agent_id)

        try:
            from app.agent.react_agent import ReActAgent

            react_agent = ReActAgent(self.db, agent, user)
            result = await react_agent.run(data.query)
            return AgentTestResponse(
                success=True,
                response=result.get("response"),
                tool_calls=result.get("tool_calls"),
                token_usage=result.get("token_usage"),
                latency_ms=result.get("latency_ms"),
            )
        except Exception as e:
            logger.error(f"Agent test failed: {e}")
            return AgentTestResponse(success=False, error=str(e))

    async def process_agent(
        self, user: User, agent_id: UUID, data: AgentProcessRequest
    ) -> AgentProcessResponse:
        """Process agent files (chunking + embedding)."""
        agent = await self._get_agent_or_404(user, agent_id)

        try:
            from app.rag.embedding import EmbeddingService

            embedding_service = EmbeddingService(self.db)
            result = await embedding_service.process_agent_files(
                agent, user, force=data.force
            )
            return AgentProcessResponse(
                message="Processing completed",
                files_processed=result.get("files_processed", 0),
                chunks_created=result.get("chunks_created", 0),
                status="completed",
            )
        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            return AgentProcessResponse(
                message=f"Processing failed: {str(e)}",
                status="failed",
            )
