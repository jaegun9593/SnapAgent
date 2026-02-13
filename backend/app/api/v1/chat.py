"""
Chat API endpoints - Sessions CRUD + message send (SSE streaming).
"""
import json
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, status
from fastapi.responses import StreamingResponse

from app.api.deps import CurrentUser, DBSession
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageListResponse,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionDeleteResponse,
    ChatSessionListResponse,
    ChatSessionResponse,
)
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    data: ChatSessionCreate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Create a new chat session for an agent."""
    service = ChatService(db)
    session = await service.create_session(current_user, data)
    return session


@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_sessions(
    current_user: CurrentUser,
    db: DBSession,
    agent_id: Optional[UUID] = Query(None),
):
    """List chat sessions, optionally filtered by agent."""
    service = ChatService(db)
    sessions = await service.list_sessions(current_user, agent_id=agent_id)
    return ChatSessionListResponse(sessions=sessions, total=len(sessions))


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session(
    session_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """Get chat session details."""
    service = ChatService(db)
    session = await service.get_session(current_user, session_id)
    return session


@router.delete("/sessions/{session_id}", response_model=ChatSessionDeleteResponse)
async def delete_session(
    session_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """Delete a chat session."""
    service = ChatService(db)
    await service.delete_session(current_user, session_id)
    return ChatSessionDeleteResponse(message="Chat session deleted successfully")


@router.get("/sessions/{session_id}/messages", response_model=ChatMessageListResponse)
async def list_messages(
    session_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """List all messages in a chat session."""
    service = ChatService(db)
    messages = await service.list_messages(current_user, session_id)
    return ChatMessageListResponse(messages=messages, total=len(messages))


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: UUID,
    data: ChatMessageCreate,
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Send a message and receive SSE streaming response.

    SSE events emitted:
    - event: thinking (intent classification)
    - event: tool_start (tool name + input)
    - event: tool_result (tool output)
    - event: evaluation (score + pass/fail)
    - event: answer_token (streaming tokens)
    - event: answer_end (usage stats)
    - event: done
    """
    service = ChatService(db)

    async def event_generator():
        try:
            async for event_type, event_data in service.send_message_stream(
                current_user, session_id, data
            ):
                payload = {"type": event_type, **event_data}
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.error(f"SSE stream error: {e}")
            error_data = {"type": "error", "error": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
