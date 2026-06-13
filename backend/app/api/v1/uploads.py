from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.upload import (
    FileUploadResponse,
    MultipleFileUploadResponse,
    WorkspaceFileListResponse,
)
from app.services.file_upload_service import FileUploadService

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post(
    "",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a single file",
    responses={
        201: {"description": "File uploaded or duplicate skipped"},
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Workspace not found"},
        422: {"description": "Validation failed"},
    },
)
async def upload_file(
    workspace_id: UUID = Form(..., description="Target workspace identifier"),
    file: UploadFile = File(..., description="File to upload (.txt, .md, .pdf, .docx)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FileUploadResponse:
    return await FileUploadService(db).upload_file(current_user, workspace_id, file)


@router.post(
    "/multiple",
    response_model=MultipleFileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload multiple files",
    responses={
        201: {"description": "Upload summary for all files"},
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Workspace not found"},
    },
)
async def upload_multiple_files(
    workspace_id: UUID = Form(..., description="Target workspace identifier"),
    files: list[UploadFile] = File(..., description="Files to upload"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> MultipleFileUploadResponse:
    return await FileUploadService(db).upload_multiple(current_user, workspace_id, files)


@router.get(
    "",
    response_model=WorkspaceFileListResponse,
    summary="List uploaded files (upload history)",
    responses={
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Workspace not found"},
    },
)
def list_uploads(
    workspace_id: UUID = Query(..., description="Workspace identifier"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> WorkspaceFileListResponse:
    return FileUploadService(db).list_files(current_user, workspace_id)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete uploaded file",
    responses={
        404: {"description": "Uploaded file not found"},
        403: {"description": "User is not the workspace owner"},
    },
)
def delete_upload(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    FileUploadService(db).delete_file(current_user, document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
