"""
Authentication service for user registration, login, and token management.
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.db.models import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: RegisterRequest) -> User:
        """
        Register a new user.

        Args:
            data: Registration data (email, password, full_name)

        Returns:
            The created User object

        Raises:
            ConflictError: If email already exists
        """
        # Check if email already exists
        result = await self.db.execute(
            select(User).where(User.email == data.email, User.use_yn == "Y")
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ConflictError(f"Email '{data.email}' already registered")

        # Create new user
        hashed_password = get_password_hash(data.password)
        user = User(
            email=data.email,
            hashed_password=hashed_password,
            full_name=data.full_name,
            role="user",
            is_active=True,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def register_and_login(self, data: RegisterRequest) -> TokenResponse:
        """
        Register a new user and return tokens (auto-login after registration).

        Args:
            data: Registration data (email, password, full_name)

        Returns:
            TokenResponse with access and refresh tokens

        Raises:
            ConflictError: If email already exists
        """
        # Register the user
        user = await self.register(data)

        # Generate tokens
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = create_refresh_token(data={"sub": user.email})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def login(self, data: LoginRequest) -> TokenResponse:
        """
        Authenticate user and generate tokens.

        Args:
            data: Login data (email, password)

        Returns:
            TokenResponse with access and refresh tokens

        Raises:
            UnauthorizedError: If credentials are invalid
        """
        # Get user by email
        result = await self.db.execute(
            select(User).where(User.email == data.email, User.use_yn == "Y")
        )
        user = result.scalar_one_or_none()

        # Verify user exists and password is correct
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise UnauthorizedError("User account is inactive")

        # Generate tokens
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = create_refresh_token(data={"sub": user.email})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: The refresh token

        Returns:
            TokenResponse with new access and refresh tokens

        Raises:
            UnauthorizedError: If refresh token is invalid
        """
        # Decode refresh token
        payload = decode_token(refresh_token)
        if not payload:
            raise UnauthorizedError("Invalid or expired refresh token")

        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")

        # Get user email
        user_email = payload.get("sub")
        if not user_email:
            raise UnauthorizedError("Invalid token payload")

        # Verify user exists and is active
        result = await self.db.execute(
            select(User).where(
                User.email == user_email, User.use_yn == "Y", User.is_active == True
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            raise UnauthorizedError("User not found or inactive")

        # Generate new tokens
        new_access_token = create_access_token(data={"sub": user.email})
        new_refresh_token = create_refresh_token(data={"sub": user.email})

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )
