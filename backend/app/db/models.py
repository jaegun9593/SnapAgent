"""
SQLAlchemy ORM models for all database tables.

IMPORTANT: No SQLAlchemy relationships are defined in this file.
- Foreign key constraints exist at the database level for data integrity
- Relationships are logical only - use explicit joins when needed
- This prevents complex relationship configuration issues with AuditMixin
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import AuditMixin, Base


class User(Base, AuditMixin):
    """User account model."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), primary_key=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Model(Base, AuditMixin):
    """LLM or Embedding model configuration registered by admin."""

    __tablename__ = "models"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(
        String(100), nullable=False, default="openrouter"
    )
    model_id: Mapped[str] = mapped_column(String(255), nullable=False)
    model_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'llm' or 'embedding'
    config: Mapped[Optional[dict]] = mapped_column(JSONB)
    pricing: Mapped[Optional[dict]] = mapped_column(JSONB)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Template(Base, AuditMixin):
    """Agent template with pre-configured tool settings and system prompts."""

    __tablename__ = "templates"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    tool_config: Mapped[Optional[dict]] = mapped_column(JSONB)
    system_prompt_template: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)


class Agent(Base, AuditMixin):
    """Agent configuration combining model, tools, and system prompt."""

    __tablename__ = "agents"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_email: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.email", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text)
    template_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("templates.id", ondelete="SET NULL"), nullable=True
    )
    model_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("models.id", ondelete="RESTRICT"), nullable=True
    )
    embedding_model_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("models.id", ondelete="SET NULL"), nullable=True
    )
    config: Mapped[Optional[dict]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(50), default="draft")


class AgentTool(Base, AuditMixin):
    """Tool attached to an agent."""

    __tablename__ = "agent_tools"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    agent_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    tool_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'rag', 'web_search', 'custom_api'
    tool_config: Mapped[Optional[dict]] = mapped_column(JSONB)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[Optional[int]] = mapped_column(Integer, default=0)


class AgentFile(Base, AuditMixin):
    """Junction table for Agent-File relationship (RAG files)."""

    __tablename__ = "agent_files"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    agent_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    file_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (UniqueConstraint("agent_id", "file_id", name="uq_agent_file"),)


class AgentSubAgent(Base, AuditMixin):
    """Junction table for Agent parent-child relationships."""

    __tablename__ = "agent_sub_agents"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    parent_agent_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    child_agent_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    sort_order: Mapped[Optional[int]] = mapped_column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("parent_agent_id", "child_agent_id", name="uq_agent_sub_agent"),
    )


class File(Base):
    """Uploaded file metadata.

    Note: Files use hard delete (no use_yn field).
    Audit fields are defined directly without AuditMixin.
    """

    __tablename__ = "files"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_email: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.email", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(Integer)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))

    # Audit fields (without use_yn - hard delete only)
    created_by: Mapped[Optional[str]] = mapped_column(
        String(255), ForeignKey("users.email", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_by: Mapped[Optional[str]] = mapped_column(
        String(255), ForeignKey("users.email", ondelete="SET NULL"), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class ChatSession(Base, AuditMixin):
    """Chat session for Agent conversation."""

    __tablename__ = "chat_sessions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_email: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.email", ondelete="CASCADE"), nullable=False
    )
    agent_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[Optional[str]] = mapped_column(String(255))


class ChatMessage(Base, AuditMixin):
    """Chat message within a session."""

    __tablename__ = "chat_messages"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'user', 'assistant', 'system'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_calls: Mapped[Optional[dict]] = mapped_column(JSONB)
    token_usage: Mapped[Optional[dict]] = mapped_column(JSONB)


class UsageLog(Base):
    """Usage log for tracking token usage and API calls.

    Note: UsageLog uses hard delete (no use_yn field).
    Only created_at is tracked (no AuditMixin).
    """

    __tablename__ = "usage_logs"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_email: Mapped[str] = mapped_column(
        String(255), ForeignKey("users.email", ondelete="CASCADE"), nullable=False
    )
    agent_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True
    )
    model_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Token usage
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # Cost & performance
    cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 6), nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class TokenLimit(Base, AuditMixin):
    """Token usage limits (global or per-user)."""

    __tablename__ = "token_limits"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_email: Mapped[Optional[str]] = mapped_column(
        String(255), ForeignKey("users.email", ondelete="CASCADE"), nullable=True
    )
    limit_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'daily', 'monthly', 'total'
    max_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_api_calls: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
