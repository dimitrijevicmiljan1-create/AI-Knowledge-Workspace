import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document
from app.models.source import Source, SourceStatus
from app.models.user import User
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.source_repository import SourceRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.document import (
    ChunkListResponse,
    ChunkResponse,
    DocumentIngestRequest,
    DocumentIngestResponse,
    DocumentListResponse,
    DocumentResponse,
    DocumentStatsResponse,
    DocumentUpdate,
    IngestionStatus,
)
from app.services.checksum import compute_checksum
from app.services.text_chunker import chunk_text, estimate_token_count


class DocumentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.document_repository = DocumentRepository(db)
        self.chunk_repository = ChunkRepository(db)
        self.source_repository = SourceRepository(db)
        self.workspace_repository = WorkspaceRepository(db)

    def ingest_document(self, user: User, ingest_in: DocumentIngestRequest) -> DocumentIngestResponse:
        source = self._get_owned_source(user, ingest_in.source_id)
        checksum = compute_checksum(ingest_in.content)
        existing = self.document_repository.get_by_source_and_path(source.id, ingest_in.path)

        if existing is not None and existing.checksum == checksum:
            chunk_count = self.chunk_repository.count_by_document(existing.id)
            if chunk_count == 0:
                if ingest_in.metadata:
                    existing = self.document_repository.update(
                        existing,
                        title=ingest_in.title,
                        document_metadata=ingest_in.metadata,
                    )
                chunk_count = self._create_chunks(existing, ingest_in.content)
                indexed_at = datetime.now(UTC)
                self._mark_source_ready(source, indexed_at)
                return DocumentIngestResponse(
                    document=DocumentResponse.model_validate(existing),
                    chunk_count=chunk_count,
                    ingestion_status=IngestionStatus.updated,
                )

            if ingest_in.metadata is not None or ingest_in.title != existing.title:
                existing = self.document_repository.update(
                    existing,
                    title=ingest_in.title,
                    document_metadata=ingest_in.metadata
                    if ingest_in.metadata is not None
                    else existing.document_metadata,
                )
            return DocumentIngestResponse(
                document=DocumentResponse.model_validate(existing),
                chunk_count=chunk_count,
                ingestion_status=IngestionStatus.unchanged,
            )

        indexed_at = datetime.now(UTC)
        if existing is None:
            document = self.document_repository.create(
                source_id=source.id,
                title=ingest_in.title,
                path=ingest_in.path,
                checksum=checksum,
                metadata=ingest_in.metadata,
                indexed_at=indexed_at,
            )
            ingestion_status = IngestionStatus.created
        else:
            document = self.document_repository.update(
                existing,
                title=ingest_in.title,
                checksum=checksum,
                document_metadata=ingest_in.metadata,
                indexed_at=indexed_at,
            )
            self.chunk_repository.delete_by_document(document.id)
            ingestion_status = IngestionStatus.updated

        chunk_count = self._create_chunks(document, ingest_in.content)
        self._mark_source_ready(source, indexed_at)

        return DocumentIngestResponse(
            document=DocumentResponse.model_validate(document),
            chunk_count=chunk_count,
            ingestion_status=ingestion_status,
        )

    def get_document(self, user: User, document_id: uuid.UUID) -> DocumentResponse:
        document = self._get_owned_document(user, document_id)
        return DocumentResponse.model_validate(document)

    def list_documents(self, user: User, source_id: uuid.UUID) -> DocumentListResponse:
        self._get_owned_source(user, source_id)
        documents = self.document_repository.list_by_source(source_id)
        items = [DocumentResponse.model_validate(document) for document in documents]
        return DocumentListResponse(items=items, total=len(items))

    def update_document(
        self,
        user: User,
        document_id: uuid.UUID,
        document_in: DocumentUpdate,
    ) -> DocumentResponse:
        document = self._get_owned_document(user, document_id)
        update_data = document_in.model_dump(exclude_unset=True)
        if "metadata" in update_data:
            update_data["document_metadata"] = update_data.pop("metadata")
        updated_document = self.document_repository.update(document, **update_data)
        return DocumentResponse.model_validate(updated_document)

    def delete_document(self, user: User, document_id: uuid.UUID) -> None:
        document = self._get_owned_document(user, document_id)
        self.document_repository.delete(document)

    def list_chunks(self, user: User, document_id: uuid.UUID) -> ChunkListResponse:
        document = self._get_owned_document(user, document_id)
        chunks = self.chunk_repository.list_by_document(document.id)
        items = [ChunkResponse.model_validate(chunk) for chunk in chunks]
        return ChunkListResponse(items=items, total=len(items))

    def get_document_stats(self, user: User, document_id: uuid.UUID) -> DocumentStatsResponse:
        document = self._get_owned_document(user, document_id)
        return DocumentStatsResponse(
            document_id=document.id,
            chunk_count=self.chunk_repository.count_by_document(document.id),
            indexed_at=document.indexed_at,
            checksum=document.checksum,
        )

    def _create_chunks(self, document: Document, content: str) -> int:
        text_chunks = chunk_text(
            content,
            chunk_size=settings.ingestion_chunk_size,
            chunk_overlap=settings.ingestion_chunk_overlap,
        )
        if not text_chunks:
            return 0

        chunk_payload = [
            {
                "chunk_index": index,
                "content": chunk_content,
                "token_count": estimate_token_count(chunk_content),
            }
            for index, chunk_content in enumerate(text_chunks)
        ]
        self.chunk_repository.create_batch(document_id=document.id, chunks=chunk_payload)
        return len(chunk_payload)

    def _mark_source_ready(self, source: Source, indexed_at: datetime) -> None:
        self.source_repository.update(
            source,
            status=SourceStatus.ready,
            last_sync_at=indexed_at,
        )

    def _get_owned_source(self, user: User, source_id: uuid.UUID) -> Source:
        source = self.source_repository.get_by_id(source_id)
        if source is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found",
            )
        self._ensure_workspace_owner(user, source.workspace_id)
        return source

    def _get_owned_document(self, user: User, document_id: uuid.UUID) -> Document:
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        self._get_owned_source(user, document.source_id)
        return document

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
