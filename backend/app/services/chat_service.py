"""
Chat service for session management and message streaming.
"""
import json
import logging
import time
from typing import AsyncGenerator, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ForbiddenError
from app.db.models import Agent, ChatMessage, ChatSession, User
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionResponse,
)

logger = logging.getLogger(__name__)


class ChatService:
    """Service for chat operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self, user: User, data: ChatSessionCreate
    ) -> ChatSessionResponse:
        """Create a new chat session."""
        # Verify agent exists and belongs to user
        result = await self.db.execute(
            select(Agent).where(
                Agent.id == data.agent_id,
                Agent.user_email == user.email,
                Agent.use_yn == "Y",
            )
        )
        agent = result.scalar_one_or_none()
        if not agent:
            raise NotFoundError(f"Agent not found: {data.agent_id}")

        session = ChatSession(
            user_email=user.email,
            agent_id=data.agent_id,
            title=data.title or f"Chat with {agent.name}",
            created_by=user.email,
            updated_by=user.email,
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return ChatSessionResponse.model_validate(session)

    async def list_sessions(
        self, user: User, agent_id: Optional[UUID] = None
    ) -> List[ChatSessionResponse]:
        """List chat sessions."""
        query = select(ChatSession).where(
            ChatSession.user_email == user.email, ChatSession.use_yn == "Y"
        )
        if agent_id:
            query = query.where(ChatSession.agent_id == agent_id)
        query = query.order_by(ChatSession.updated_at.desc())

        result = await self.db.execute(query)
        sessions = result.scalars().all()
        return [ChatSessionResponse.model_validate(s) for s in sessions]

    async def get_session(
        self, user: User, session_id: UUID
    ) -> ChatSessionResponse:
        """Get a chat session."""
        result = await self.db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_email == user.email,
                ChatSession.use_yn == "Y",
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise NotFoundError(f"Session not found: {session_id}")
        return ChatSessionResponse.model_validate(session)

    async def delete_session(self, user: User, session_id: UUID) -> None:
        """Soft delete a chat session."""
        result = await self.db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_email == user.email,
                ChatSession.use_yn == "Y",
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise NotFoundError(f"Session not found: {session_id}")

        session.use_yn = "N"
        session.updated_by = user.email
        await self.db.commit()

    async def list_messages(
        self, user: User, session_id: UUID
    ) -> List[ChatMessageResponse]:
        """List messages in a session."""
        # Verify session ownership
        result = await self.db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_email == user.email,
                ChatSession.use_yn == "Y",
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise NotFoundError(f"Session not found: {session_id}")

        msg_result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id, ChatMessage.use_yn == "Y")
            .order_by(ChatMessage.created_at.asc())
        )
        messages = msg_result.scalars().all()
        return [ChatMessageResponse.model_validate(m) for m in messages]

    async def send_message_stream(
        self, user: User, session_id: UUID, data: ChatMessageCreate
    ) -> AsyncGenerator[Tuple[str, dict], None]:
        """
        Send a message and yield SSE events from the ReAct agent.

        Yields:
            Tuples of (event_type, event_data) for SSE streaming
        """
        # Verify session
        result = await self.db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_email == user.email,
                ChatSession.use_yn == "Y",
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise NotFoundError(f"Session not found: {session_id}")

        # Get agent
        agent_result = await self.db.execute(
            select(Agent).where(Agent.id == session.agent_id, Agent.use_yn == "Y")
        )
        agent = agent_result.scalar_one_or_none()
        if not agent:
            raise NotFoundError("Agent not found")

        # Save user message
        user_message = ChatMessage(
            session_id=session_id,
            role="user",
            content=data.content,
            created_by=user.email,
            updated_by=user.email,
        )
        self.db.add(user_message)
        await self.db.commit()

        # Get message history
        history_result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id, ChatMessage.use_yn == "Y")
            .order_by(ChatMessage.created_at.asc())
        )
        history = history_result.scalars().all()

        # Run ReAct agent
        start_time = time.time()
        full_response = ""
        tool_calls_data = []
        token_usage_data = {}

        try:
            from app.agent.react_agent import ReActAgent

            react_agent = ReActAgent(self.db, agent, user)

            async for event_type, event_data in react_agent.run_stream(
                data.content, history=history, config=data.config
            ):
                if event_type == "answer_token":
                    full_response += event_data.get("content", "")
                elif event_type == "tool_start" or event_type == "tool_result":
                    tool_calls_data.append(event_data)
                elif event_type == "answer_end":
                    token_usage_data = event_data.get("usage", {})

                yield event_type, event_data

        except Exception as e:
            logger.error(f"ReAct agent error: {e}")
            yield "error", {"error": str(e)}
            full_response = f"Error: {str(e)}"

        # Save assistant message
        latency_ms = int((time.time() - start_time) * 1000)
        assistant_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=full_response or "No response generated",
            tool_calls=tool_calls_data if tool_calls_data else None,
            token_usage=token_usage_data if token_usage_data else None,
            created_by=user.email,
            updated_by=user.email,
        )
        self.db.add(assistant_message)
        await self.db.commit()

        yield "done", {
            "message_id": str(assistant_message.id),
            "latency_ms": latency_ms,
        }
