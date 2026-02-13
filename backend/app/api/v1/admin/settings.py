"""
Admin System Settings API - GET / POST / DELETE.
"""
from fastapi import APIRouter, status

from app.api.deps import AdminUser, DBSession
from app.schemas.system_setting import (
    SystemSettingDeleteResponse,
    SystemSettingListResponse,
    SystemSettingResponse,
    SystemSettingUpsert,
)
from app.services.system_setting_service import SystemSettingService

router = APIRouter(prefix="/settings", tags=["Admin - Settings"])


@router.get("/", response_model=SystemSettingListResponse)
async def list_settings(
    admin_user: AdminUser,
    db: DBSession,
):
    """List all system settings (encrypted values are masked)."""
    service = SystemSettingService(db)
    settings = await service.list_settings()
    return SystemSettingListResponse(settings=settings, total=len(settings))


@router.post("/", response_model=SystemSettingResponse, status_code=status.HTTP_200_OK)
async def upsert_setting(
    data: SystemSettingUpsert,
    admin_user: AdminUser,
    db: DBSession,
):
    """Create or update a system setting (upsert by key)."""
    service = SystemSettingService(db)
    return await service.upsert_setting(admin_user, data)


@router.delete("/{setting_key}", response_model=SystemSettingDeleteResponse)
async def delete_setting(
    setting_key: str,
    admin_user: AdminUser,
    db: DBSession,
):
    """Soft delete a system setting by key."""
    service = SystemSettingService(db)
    await service.delete_setting(setting_key)
    return SystemSettingDeleteResponse(message=f"Setting '{setting_key}' deleted")
