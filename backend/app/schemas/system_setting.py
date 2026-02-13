"""
Pydantic schemas for system settings.
"""
from typing import List, Optional

from pydantic import BaseModel


class SystemSettingUpsert(BaseModel):
    """Request body for creating or updating a system setting."""
    setting_key: str
    setting_value: str
    is_encrypted: bool = False
    description: Optional[str] = None


class SystemSettingResponse(BaseModel):
    """Single setting response (encrypted values are masked)."""
    setting_key: str
    setting_value: str
    is_encrypted: bool
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class SystemSettingListResponse(BaseModel):
    """List of system settings."""
    settings: List[SystemSettingResponse]
    total: int


class SystemSettingDeleteResponse(BaseModel):
    """Response after deleting a setting."""
    message: str
