"""
File service for upload, listing, and management.
"""
import logging
import os
import uuid
from typing import List, Tuple
from uuid import UUID

import aiofiles
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.db.models import File, User
from app.schemas.file import FileResponse

logger = logging.getLogger(__name__)


class FileService:
    """Service for file operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_file(self, user: User, upload: UploadFile) -> FileResponse:
        """Upload a file."""
        # Validate file extension
        filename = upload.filename or "unknown"
        ext = os.path.splitext(filename)[1].lower()
        if ext not in settings.allowed_extensions:
            raise ValidationError(
                f"File type '{ext}' not allowed. Allowed: {settings.allowed_extensions}"
            )

        # Read file content
        content = await upload.read()
        file_size = len(content)

        # Check file size
        max_size = settings.max_file_size_mb * 1024 * 1024
        if file_size > max_size:
            raise ValidationError(
                f"File too large ({file_size / 1024 / 1024:.1f}MB). Max: {settings.max_file_size_mb}MB"
            )

        # Generate stored filename
        stored_filename = f"{uuid.uuid4().hex}{ext}"
        user_dir = os.path.join(settings.upload_dir, user.email)
        os.makedirs(user_dir, exist_ok=True)
        file_path = os.path.join(user_dir, stored_filename)

        # Save file
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        # Create database record
        file_record = File(
            user_email=user.email,
            filename=filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=upload.content_type,
            created_by=user.email,
            updated_by=user.email,
        )
        self.db.add(file_record)
        await self.db.commit()
        await self.db.refresh(file_record)

        return FileResponse.model_validate(file_record)

    async def list_files(self, user: User) -> List[FileResponse]:
        """List all files for a user."""
        result = await self.db.execute(
            select(File)
            .where(File.user_email == user.email)
            .order_by(File.created_at.desc())
        )
        files = result.scalars().all()
        return [FileResponse.model_validate(f) for f in files]

    async def get_file(self, user: User, file_id: UUID) -> FileResponse:
        """Get file details."""
        result = await self.db.execute(
            select(File).where(File.id == file_id, File.user_email == user.email)
        )
        file_record = result.scalar_one_or_none()
        if not file_record:
            raise NotFoundError(f"File not found: {file_id}")
        return FileResponse.model_validate(file_record)

    async def delete_file(self, user: User, file_id: UUID) -> None:
        """Delete a file (hard delete)."""
        result = await self.db.execute(
            select(File).where(File.id == file_id, File.user_email == user.email)
        )
        file_record = result.scalar_one_or_none()
        if not file_record:
            raise NotFoundError(f"File not found: {file_id}")

        # Delete physical file
        if os.path.exists(file_record.file_path):
            os.remove(file_record.file_path)

        await self.db.delete(file_record)
        await self.db.commit()

    async def get_file_for_download(
        self, user: User, file_id: UUID
    ) -> Tuple[str, str, str]:
        """Get file path for download."""
        result = await self.db.execute(
            select(File).where(File.id == file_id, File.user_email == user.email)
        )
        file_record = result.scalar_one_or_none()
        if not file_record:
            raise NotFoundError(f"File not found: {file_id}")

        if not os.path.exists(file_record.file_path):
            raise NotFoundError("File not found on disk")

        return file_record.file_path, file_record.filename, file_record.mime_type
