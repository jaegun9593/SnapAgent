"""
Dependency injection functions for FastAPI routes.
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.security import decode_token
from app.db.database import get_db
from app.db.models import User


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        The authenticated User object

    Raises:
        UnauthorizedError: If token is invalid or user not found
    """
    token = credentials.credentials

    # Decode token
    payload = decode_token(token)
    if payload is None:
        raise UnauthorizedError("Invalid or expired token")

    # Get user email from token
    user_email = payload.get("sub")
    if user_email is None:
        raise UnauthorizedError("Invalid token payload")

    # Get user from database
    result = await db.execute(
        select(User).where(User.email == user_email, User.use_yn == "Y", User.is_active == True)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedError("User not found or inactive")

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Ensure the current user is active.

    Args:
        current_user: The current user from get_current_user

    Returns:
        The active User object

    Raises:
        UnauthorizedError: If user is inactive
    """
    if not current_user.is_active:
        raise UnauthorizedError("Inactive user")

    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Ensure the current user is an admin.

    Args:
        current_user: The current active user

    Returns:
        The admin User object

    Raises:
        ForbiddenError: If user is not an admin
    """
    if current_user.role != "admin":
        raise ForbiddenError("Admin access required")

    return current_user


# Type aliases for dependency injection
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_active_user)]
AdminUser = Annotated[User, Depends(get_current_admin_user)]
