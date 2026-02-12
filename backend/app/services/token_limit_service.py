"""
Token limit service for managing usage limits.
"""
import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models import TokenLimit, User
from app.schemas.token_limit import (
    TokenLimitCreate,
    TokenLimitResponse,
    TokenLimitUpdate,
)

logger = logging.getLogger(__name__)


class TokenLimitService:
    """Service for token limit operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_token_limit(
        self, admin_user: User, data: TokenLimitCreate
    ) -> TokenLimitResponse:
        """Create a new token limit."""
        limit = TokenLimit(
            user_email=data.user_email,
            limit_type=data.limit_type,
            max_tokens=data.max_tokens,
            max_api_calls=data.max_api_calls,
            is_active=data.is_active,
            created_by=admin_user.email,
            updated_by=admin_user.email,
        )
        self.db.add(limit)
        await self.db.commit()
        await self.db.refresh(limit)
        return TokenLimitResponse.model_validate(limit)

    async def list_token_limits(
        self, user_email: Optional[str] = None
    ) -> List[TokenLimitResponse]:
        """List token limits."""
        query = select(TokenLimit).where(TokenLimit.use_yn == "Y")
        if user_email:
            query = query.where(TokenLimit.user_email == user_email)
        query = query.order_by(TokenLimit.created_at.desc())

        result = await self.db.execute(query)
        limits = result.scalars().all()
        return [TokenLimitResponse.model_validate(l) for l in limits]

    async def get_token_limit(self, limit_id: UUID) -> TokenLimitResponse:
        """Get token limit details."""
        result = await self.db.execute(
            select(TokenLimit).where(TokenLimit.id == limit_id, TokenLimit.use_yn == "Y")
        )
        limit = result.scalar_one_or_none()
        if not limit:
            raise NotFoundError(f"Token limit not found: {limit_id}")
        return TokenLimitResponse.model_validate(limit)

    async def update_token_limit(
        self, limit_id: UUID, data: TokenLimitUpdate
    ) -> TokenLimitResponse:
        """Update a token limit."""
        result = await self.db.execute(
            select(TokenLimit).where(TokenLimit.id == limit_id, TokenLimit.use_yn == "Y")
        )
        limit = result.scalar_one_or_none()
        if not limit:
            raise NotFoundError(f"Token limit not found: {limit_id}")

        for field in ["max_tokens", "max_api_calls", "is_active"]:
            value = getattr(data, field, None)
            if value is not None:
                setattr(limit, field, value)

        await self.db.commit()
        await self.db.refresh(limit)
        return TokenLimitResponse.model_validate(limit)

    async def delete_token_limit(self, limit_id: UUID) -> None:
        """Soft delete a token limit."""
        result = await self.db.execute(
            select(TokenLimit).where(TokenLimit.id == limit_id, TokenLimit.use_yn == "Y")
        )
        limit = result.scalar_one_or_none()
        if not limit:
            raise NotFoundError(f"Token limit not found: {limit_id}")
        limit.use_yn = "N"
        await self.db.commit()
