from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class UploadStatus(str, Enum):
    created = "created"
    skipped = "skipped"
    failed = "failed"


class FileValidationErrorResponse(BaseModel):
    field: str
    message: str


class FileUploadResult(BaseModel):
    filename: str
    status: UploadStatus
    document_id: UUID | None = None
    size: int | None = None
    checksum: str | None = None
    message: str | None = None
    errors: list[FileValidationErrorResponse] = Field(default_factory=list)


class FileUploadResponse(BaseModel):
    file: FileUploadResult


class MultipleFileUploadResponse(BaseModel):
    uploaded: int
    skipped: int
    failed: int
    results: list[FileUploadResult]


class WorkspaceFileResponse(BaseModel):
    document_id: UUID
    filename: str
    size: int
    uploaded_at: datetime


class WorkspaceFileListResponse(BaseModel):
    items: list[WorkspaceFileResponse]
    total: int
