"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DBSession
from app.schemas.auth import (
    LoginRequest,
    LogoutResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: DBSession):
    """
    Register a new user account and return tokens.

    Args:
        data: Registration data (email, password, full_name)
        db: Database session

    Returns:
        Access token and refresh token (user is logged in after registration)

    Raises:
        409 Conflict: If email already exists
    """
    auth_service = AuthService(db)
    tokens = await auth_service.register_and_login(data)
    return tokens


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: DBSession):
    """
    Authenticate user and get access tokens.

    Args:
        data: Login credentials (email, password)
        db: Database session

    Returns:
        Access token and refresh token

    Raises:
        401 Unauthorized: If credentials are invalid
    """
    auth_service = AuthService(db)
    tokens = await auth_service.login(data)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: DBSession):
    """
    Refresh access token using refresh token.

    Args:
        data: Refresh token
        db: Database session

    Returns:
        New access token and refresh token

    Raises:
        401 Unauthorized: If refresh token is invalid
    """
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_access_token(data.refresh_token)
    return tokens


@router.post("/logout", response_model=LogoutResponse)
async def logout():
    """
    Logout user (client-side token removal).

    Note: Since we're using stateless JWT tokens, logout is handled
    client-side by removing the tokens. This endpoint is provided
    for API consistency.

    Returns:
        Logout confirmation message
    """
    return LogoutResponse(message="Logged out successfully")
