"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DBSession
from app.core.exceptions import ValidationError
from app.schemas.auth import (
    CaptchaResponse,
    LoginRequest,
    LogoutResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService
from app.services.captcha_service import CaptchaService


router = APIRouter(prefix="/auth", tags=["Authentication"])

captcha_service = CaptchaService()


@router.get("/captcha", response_model=CaptchaResponse)
async def get_captcha():
    """
    Generate a new CAPTCHA image for registration.

    Returns:
        CAPTCHA ID and base64-encoded image
    """
    captcha_id, image_base64 = captcha_service.generate()
    return CaptchaResponse(captcha_id=captcha_id, image_base64=image_base64)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: DBSession):
    """
    Register a new user account and return tokens.

    Args:
        data: Registration data (email, password, full_name, captcha_id, captcha_text)
        db: Database session

    Returns:
        Access token and refresh token (user is logged in after registration)

    Raises:
        409 Conflict: If email already exists
        422 Validation Error: If CAPTCHA is invalid
    """
    if not CaptchaService.verify(data.captcha_id, data.captcha_text):
        raise ValidationError(
            message="보안 문자가 올바르지 않습니다",
            error_code="INVALID_CAPTCHA",
        )

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
