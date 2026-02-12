"""
User service for profile management.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.models import User
from app.schemas.user import UserUpdate


class UserService:
    """Service for user operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_user(self, user: User, data: UserUpdate) -> User:
        """
        Update user information.

        Args:
            user: The current user object
            data: Update data

        Returns:
            Updated user object
        """
        if data.full_name is not None:
            user.full_name = data.full_name

        if data.password is not None:
            user.hashed_password = get_password_hash(data.password)

        user.updated_by = user.email
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user: User) -> None:
        """
        Soft delete a user account.

        Args:
            user: The user to delete
        """
        user.use_yn = "N"
        user.is_active = False
        user.updated_by = user.email
        await self.db.commit()
