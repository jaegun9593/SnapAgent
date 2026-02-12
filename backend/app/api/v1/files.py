"""
File API endpoints - Upload, list, get, delete, download.
"""
from uuid import UUID

from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import FileResponse

from app.api.deps import CurrentUser, DBSession
from app.schemas.file import FileDeleteResponse, FileListResponse, FileResponse as FileSchemaResponse
from app.services.file_service import FileService


router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload", response_model=FileSchemaResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    current_user: CurrentUser,
    db: DBSession,
):
    """Upload a file for RAG processing."""
    service = FileService(db)
    file_record = await service.upload_file(current_user, file)
    return file_record


@router.get("/", response_model=FileListResponse)
async def list_files(
    current_user: CurrentUser,
    db: DBSession,
):
    """List all files for the current user."""
    service = FileService(db)
    files = await service.list_files(current_user)
    return FileListResponse(files=files, total=len(files))


@router.get("/{file_id}", response_model=FileSchemaResponse)
async def get_file(
    file_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """Get file details by ID."""
    service = FileService(db)
    file_record = await service.get_file(current_user, file_id)
    return file_record


@router.delete("/{file_id}", response_model=FileDeleteResponse)
async def delete_file(
    file_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """Delete a file."""
    service = FileService(db)
    await service.delete_file(current_user, file_id)
    return FileDeleteResponse(message="File deleted successfully")


@router.get("/{file_id}/download")
async def download_file(
    file_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    """Download a file."""
    service = FileService(db)
    file_path, filename, mime_type = await service.get_file_for_download(current_user, file_id)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=mime_type or "application/octet-stream",
    )
