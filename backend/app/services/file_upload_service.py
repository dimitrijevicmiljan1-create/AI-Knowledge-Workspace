import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document
from app.models.source import Source, SourceType
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.repositories.source_repository import SourceRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.upload import (
    FileUploadResponse,
    FileUploadResult,
    FileValidationErrorResponse,
    MultipleFileUploadResponse,
    UploadStatus,
    WorkspaceFileListResponse,
    WorkspaceFileResponse,
)
from app.services.checksum import compute_bytes_checksum
from app.services.document_indexing_service import DocumentIndexingService
from app.services.file_validator import validate_upload_file
from app.storage.manager import StorageManager, get_storage_manager


class FileUploadService:
    def __init__(self, db: Session, storage: StorageManager | None = None) -> None:
        self.db = db
        self.storage = storage or get_storage_manager()
        self.document_repository = DocumentRepository(db)
        self.source_repository = SourceRepository(db)
        self.workspace_repository = WorkspaceRepository(db)
        self.document_indexing_service = DocumentIndexingService(db)

    async def upload_file(self, user: User, workspace_id: uuid.UUID, file: UploadFile) -> FileUploadResponse:
        self._ensure_workspace_owner(user, workspace_id)
        result = await self._process_upload(workspace_id, file)
        if result.status == UploadStatus.failed:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": result.message or "File validation failed",
                    "errors": [error.model_dump() for error in result.errors],
                },
            )
        if result.document_id is not None and result.status in {
            UploadStatus.created,
            UploadStatus.skipped,
        }:
            self._maybe_auto_index(user, result.document_id)
        return FileUploadResponse(file=result)

    async def upload_multiple(
        self,
        user: User,
        workspace_id: uuid.UUID,
        files: list[UploadFile],
    ) -> MultipleFileUploadResponse:
        self._ensure_workspace_owner(user, workspace_id)
        results: list[FileUploadResult] = []
        for upload in files:
            result = await self._process_upload(workspace_id, upload)
            results.append(result)
            if result.document_id is not None and result.status in {
                UploadStatus.created,
                UploadStatus.skipped,
            }:
                self._maybe_auto_index(user, result.document_id)

        uploaded = sum(1 for result in results if result.status == UploadStatus.created)
        skipped = sum(1 for result in results if result.status == UploadStatus.skipped)
        failed = sum(1 for result in results if result.status == UploadStatus.failed)
        return MultipleFileUploadResponse(
            uploaded=uploaded,
            skipped=skipped,
            failed=failed,
            results=results,
        )

    def delete_file(self, user: User, document_id: uuid.UUID) -> None:
        document = self._get_owned_upload_document(user, document_id)
        storage_path = document.document_metadata.get("storage_path")
        if storage_path:
            try:
                self.storage.delete(storage_path)
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(exc),
                ) from exc
        self.document_repository.delete(document)

    def list_files(self, user: User, workspace_id: uuid.UUID) -> WorkspaceFileListResponse:
        source = self._get_local_source(user, workspace_id)
        documents = self.document_repository.list_uploaded_files(source.id)
        items = [self._to_workspace_file(document) for document in documents]
        return WorkspaceFileListResponse(items=items, total=len(items))

    async def _process_upload(self, workspace_id: uuid.UUID, file: UploadFile) -> FileUploadResult:
        filename = file.filename or "upload.bin"
        content = await file.read()

        validation = validate_upload_file(filename, content, file.content_type)
        if not validation.valid:
            return FileUploadResult(
                filename=filename,
                status=UploadStatus.failed,
                message="File validation failed",
                errors=[
                    FileValidationErrorResponse(field=error.field, message=error.message)
                    for error in validation.errors
                ],
            )

        checksum = compute_bytes_checksum(content)
        source = self._get_or_create_local_source(workspace_id)
        existing = self.document_repository.get_by_source_and_checksum(source.id, checksum)
        if existing is not None:
            return FileUploadResult(
                filename=validation.extension and Path(filename).name or filename,
                status=UploadStatus.skipped,
                document_id=existing.id,
                size=len(content),
                checksum=checksum,
                message="Duplicate file skipped",
            )

        try:
            stored_file = self.storage.save(str(workspace_id), filename, content)
        except ValueError as exc:
            return FileUploadResult(
                filename=filename,
                status=UploadStatus.failed,
                message=str(exc),
            )

        uploaded_at = datetime.now(UTC)
        metadata = {
            "filename": Path(filename).name,
            "extension": validation.extension,
            "size": len(content),
            "mime_type": validation.mime_type,
            "uploaded_at": uploaded_at.isoformat(),
            "checksum": checksum,
            "storage_path": stored_file.path,
            "upload_type": "file",
        }

        document = self.document_repository.create(
            source_id=source.id,
            title=Path(filename).stem or Path(filename).name,
            path=f"uploads/{stored_file.path}",
            checksum=checksum,
            metadata=metadata,
            indexed_at=None,
        )

        return FileUploadResult(
            filename=metadata["filename"],
            status=UploadStatus.created,
            document_id=document.id,
            size=len(content),
            checksum=checksum,
        )

    def _get_or_create_local_source(self, workspace_id: uuid.UUID) -> Source:
        source = self.source_repository.get_local_files_source(workspace_id)
        if source is not None:
            return source

        upload_directory = str(Path(settings.storage_upload_path) / str(workspace_id))
        return self.source_repository.create(
            workspace_id=workspace_id,
            name="Uploaded Files",
            source_type=SourceType.local_files,
            config={"directory_path": upload_directory},
        )

    def _get_local_source(self, user: User, workspace_id: uuid.UUID) -> Source:
        self._ensure_workspace_owner(user, workspace_id)
        source = self.source_repository.get_local_files_source(workspace_id)
        if source is None:
            return self._get_or_create_local_source(workspace_id)
        return source

    def _get_owned_upload_document(self, user: User, document_id: uuid.UUID) -> Document:
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        source = self.source_repository.get_by_id(document.source_id)
        if source is None or source.source_type != SourceType.local_files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Uploaded file not found",
            )

        self._ensure_workspace_owner(user, source.workspace_id)
        if document.document_metadata.get("upload_type") != "file":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Uploaded file not found",
            )
        return document

    def _to_workspace_file(self, document: Document) -> WorkspaceFileResponse:
        metadata = document.document_metadata
        uploaded_at_raw = metadata.get("uploaded_at")
        uploaded_at = (
            datetime.fromisoformat(uploaded_at_raw)
            if isinstance(uploaded_at_raw, str)
            else document.created_at
        )
        return WorkspaceFileResponse(
            document_id=document.id,
            filename=metadata.get("filename", document.title),
            size=int(metadata.get("size", 0)),
            uploaded_at=uploaded_at,
        )

    def _maybe_auto_index(self, user: User, document_id: uuid.UUID) -> None:
        if not self.document_indexing_service.should_auto_index(user):
            return
        self.document_indexing_service.index_document(user, document_id)

    def _ensure_workspace_owner(self, user: User, workspace_id: uuid.UUID) -> None:
        workspace = self.workspace_repository.get_by_id(workspace_id)
        if workspace is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        if workspace.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this workspace",
            )
