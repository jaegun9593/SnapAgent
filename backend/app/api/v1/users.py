"""
User API endpoints.
"""
from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.user import UserDeleteResponse, UserResponse, UserUpdate
from app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser):
    """
    Get current user information.

    Args:
        current_user: The authenticated user

    Returns:
        User information
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    data: UserUpdate,
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Update current user information.

    Args:
        data: Update data (full_name, password)
        current_user: The authenticated user
        db: Database session

    Returns:
        Updated user information
    """
    user_service = UserService(db)
    updated_user = await user_service.update_user(current_user, data)
    return updated_user


@router.delete("/me", response_model=UserDeleteResponse)
async def delete_current_user(
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Delete current user account (soft delete).

    Args:
        current_user: The authenticated user
        db: Database session

    Returns:
        Deletion confirmation
    """
    user_service = UserService(db)
    await user_service.delete_user(current_user)
    return UserDeleteResponse(message="User account deleted successfully")
