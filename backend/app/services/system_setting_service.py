"""
Service for system settings CRUD with Fernet encryption support.
"""
import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.encryption import decrypt_api_key, encrypt_api_key, mask_api_key
from app.db.models import SystemSetting, User
from app.schemas.system_setting import SystemSettingResponse, SystemSettingUpsert

logger = logging.getLogger(__name__)


class SystemSettingService:
    """Service for system setting operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_setting_value(self, key: str) -> Optional[str]:
        """Get the decrypted value of a setting by key. Returns None if not found."""
        result = await self.db.execute(
            select(SystemSetting).where(
                SystemSetting.setting_key == key,
                SystemSetting.use_yn == "Y",
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            return None
        if row.is_encrypted:
            try:
                return decrypt_api_key(row.setting_value)
            except ValueError:
                logger.error("Failed to decrypt setting: %s", key)
                return None
        return row.setting_value

    async def list_settings(self) -> List[SystemSettingResponse]:
        """List all active settings. Encrypted values are masked."""
        result = await self.db.execute(
            select(SystemSetting)
            .where(SystemSetting.use_yn == "Y")
            .order_by(SystemSetting.setting_key)
        )
        rows = result.scalars().all()
        settings = []
        for row in rows:
            value = row.setting_value
            if row.is_encrypted:
                try:
                    plain = decrypt_api_key(value)
                    value = mask_api_key(plain)
                except ValueError:
                    value = "***decryption_error***"
            settings.append(
                SystemSettingResponse(
                    setting_key=row.setting_key,
                    setting_value=value,
                    is_encrypted=row.is_encrypted,
                    description=row.description,
                )
            )
        return settings

    async def upsert_setting(
        self, admin: User, data: SystemSettingUpsert
    ) -> SystemSettingResponse:
        """Insert or update a setting. Encrypts the value if is_encrypted is True."""
        result = await self.db.execute(
            select(SystemSetting).where(
                SystemSetting.setting_key == data.setting_key,
                SystemSetting.use_yn == "Y",
            )
        )
        existing = result.scalar_one_or_none()

        stored_value = data.setting_value
        if data.is_encrypted:
            stored_value = encrypt_api_key(data.setting_value)

        if existing:
            existing.setting_value = stored_value
            existing.is_encrypted = data.is_encrypted
            existing.description = data.description
            existing.updated_by = admin.email
            await self.db.commit()
            await self.db.refresh(existing)
        else:
            new_setting = SystemSetting(
                setting_key=data.setting_key,
                setting_value=stored_value,
                is_encrypted=data.is_encrypted,
                description=data.description,
                created_by=admin.email,
                updated_by=admin.email,
            )
            self.db.add(new_setting)
            await self.db.commit()
            await self.db.refresh(new_setting)

        # Return masked value for encrypted settings
        display_value = data.setting_value
        if data.is_encrypted:
            display_value = mask_api_key(data.setting_value)

        return SystemSettingResponse(
            setting_key=data.setting_key,
            setting_value=display_value,
            is_encrypted=data.is_encrypted,
            description=data.description,
        )

    async def delete_setting(self, setting_key: str) -> None:
        """Soft delete a setting by key."""
        result = await self.db.execute(
            select(SystemSetting).where(
                SystemSetting.setting_key == setting_key,
                SystemSetting.use_yn == "Y",
            )
        )
        row = result.scalar_one_or_none()
        if row:
            row.use_yn = "N"
            await self.db.commit()
