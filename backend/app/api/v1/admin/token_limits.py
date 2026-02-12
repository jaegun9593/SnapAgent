"""
Admin Token Limit CRUD + per-user query.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import AdminUser, DBSession
from app.schemas.token_limit import (
    TokenLimitCreate,
    TokenLimitDeleteResponse,
    TokenLimitListResponse,
    TokenLimitResponse,
    TokenLimitUpdate,
)
from app.services.token_limit_service import TokenLimitService


router = APIRouter(prefix="/token-limits", tags=["Admin - Token Limits"])


@router.post("/", response_model=TokenLimitResponse, status_code=status.HTTP_201_CREATED)
async def create_token_limit(
    data: TokenLimitCreate,
    admin_user: AdminUser,
    db: DBSession,
):
    """Create a new token limit (global or per-user)."""
    service = TokenLimitService(db)
    limit = await service.create_token_limit(admin_user, data)
    return limit


@router.get("/", response_model=TokenLimitListResponse)
async def list_token_limits(
    admin_user: AdminUser,
    db: DBSession,
    user_email: Optional[str] = Query(None),
):
    """List token limits, optionally filtered by user."""
    service = TokenLimitService(db)
    limits = await service.list_token_limits(user_email=user_email)
    return TokenLimitListResponse(limits=limits, total=len(limits))


@router.get("/{limit_id}", response_model=TokenLimitResponse)
async def get_token_limit(
    limit_id: UUID,
    admin_user: AdminUser,
    db: DBSession,
):
    """Get token limit details by ID."""
    service = TokenLimitService(db)
    limit = await service.get_token_limit(limit_id)
    return limit


@router.put("/{limit_id}", response_model=TokenLimitResponse)
async def update_token_limit(
    limit_id: UUID,
    data: TokenLimitUpdate,
    admin_user: AdminUser,
    db: DBSession,
):
    """Update a token limit."""
    service = TokenLimitService(db)
    limit = await service.update_token_limit(limit_id, data)
    return limit


@router.delete("/{limit_id}", response_model=TokenLimitDeleteResponse)
async def delete_token_limit(
    limit_id: UUID,
    admin_user: AdminUser,
    db: DBSession,
):
    """Delete a token limit (soft delete)."""
    service = TokenLimitService(db)
    await service.delete_token_limit(limit_id)
    return TokenLimitDeleteResponse(message="Token limit deleted successfully")
