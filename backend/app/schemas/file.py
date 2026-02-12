"""
Pydantic schemas for file endpoints.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FileResponse(BaseModel):
    """Response schema for file."""

    id: UUID
    filename: str
    stored_filename: str
    file_path: str
    file_size: Optional[int]
    mime_type: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """Response schema for file list."""

    files: List[FileResponse]
    total: int


class FileDeleteResponse(BaseModel):
    """Response schema for file deletion."""

    message: str = Field(default="File deleted successfully")
