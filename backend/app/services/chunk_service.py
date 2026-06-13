import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.chunking.base import ChunkConfig, ChunkStrategyName
from app.chunking.extractors import extract_text_from_file
from app.chunking.manager import ChunkingManager
from app.chunking.tokenizer import estimate_token_count
from app.core.config import settings
from app.models.document import Document
from app.models.user import User
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.source_repository import SourceRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.chunk import ChunkOperationResponse, ChunkPreviewResponse, ChunkRequest, ChunkStatsResponse
from app.schemas.document import ChunkListResponse, ChunkResponse
from app.storage.manager import StorageManager, get_storage_manager


class ChunkService:
    def __init__(
        self,
        db: Session,
        storage: StorageManager | None = None,
        chunking_manager: ChunkingManager | None = None,
    ) -> None:
        self.db = db
        self.storage = storage or get_storage_manager()
        self.chunking_manager = chunking_manager or ChunkingManager()
        self.chunk_repository = ChunkRepository(db)
        self.document_repository = DocumentRepository(db)
        self.source_repository = SourceRepository(db)
        self.workspace_repository = WorkspaceRepository(db)

    def chunk_document(
        self,
        user: User,
        document_id: uuid.UUID,
        chunk_request: ChunkRequest | None = None,
    ) -> ChunkOperationResponse:
        document = self._get_owned_document(user, document_id)
        if self.chunk_repository.count_by_document(document.id) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document already has chunks. Use rechunk to replace them.",
            )
        return self._chunk_and_persist(document, chunk_request)

    def rechunk_document(
        self,
        user: User,
        document_id: uuid.UUID,
        chunk_request: ChunkRequest | None = None,
    ) -> ChunkOperationResponse:
        document = self._get_owned_document(user, document_id)
        self.chunk_repository.delete_by_document(document.id)
        return self._chunk_and_persist(document, chunk_request)

    def delete_chunks(self, user: User, document_id: uuid.UUID) -> None:
        document = self._get_owned_document(user, document_id)
        self.chunk_repository.delete_by_document(document.id)

    def list_chunks(self, user: User, document_id: uuid.UUID) -> ChunkListResponse:
        document = self._get_owned_document(user, document_id)
        chunks = self.chunk_repository.list_by_document(document.id)
        items = [ChunkResponse.model_validate(chunk) for chunk in chunks]
        return ChunkListResponse(items=items, total=len(items))

    def get_chunk_preview(self, user: User, chunk_id: uuid.UUID) -> ChunkPreviewResponse:
        chunk = self.chunk_repository.get_by_id(chunk_id)
        if chunk is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chunk not found",
            )
        self._get_owned_document(user, chunk.document_id)
        return ChunkPreviewResponse(
            id=chunk.id,
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            token_count=chunk.token_count,
        )

    def get_chunk_stats(self, user: User, document_id: uuid.UUID) -> ChunkStatsResponse:
        document = self._get_owned_document(user, document_id)
        chunks = self.chunk_repository.list_by_document(document.id)
        total_chunks = len(chunks)
        total_tokens = self.chunk_repository.sum_tokens_by_document(document.id)
        avg_chunk_size = (total_tokens / total_chunks) if total_chunks else 0.0
        return ChunkStatsResponse(
            document_id=document.id,
            total_chunks=total_chunks,
            total_tokens=total_tokens,
            avg_chunk_size=round(avg_chunk_size, 2),
        )

    def _chunk_and_persist(
        self,
        document: Document,
        chunk_request: ChunkRequest | None,
    ) -> ChunkOperationResponse:
        config = self._build_config(chunk_request)
        text = self._resolve_document_text(document)
        text_chunks = self.chunking_manager.chunk(text, config)
        if not text_chunks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No chunks generated from document text",
            )

        payload = [
            {
                "chunk_index": index,
                "content": chunk_content,
                "token_count": estimate_token_count(chunk_content),
            }
            for index, chunk_content in enumerate(text_chunks)
        ]
        self.chunk_repository.create_batch(document_id=document.id, chunks=payload)
        total_tokens = sum(item["token_count"] for item in payload)
        self.document_repository.update(document, indexed_at=datetime.now(UTC))

        return ChunkOperationResponse(
            document_id=document.id,
            chunk_count=len(payload),
            strategy=config.strategy,
            total_tokens=total_tokens,
        )

    def _build_config(self, chunk_request: ChunkRequest | None) -> ChunkConfig:
        request = chunk_request or ChunkRequest()
        return ChunkConfig(
            chunk_size=request.chunk_size or settings.chunk_size,
            chunk_overlap=request.chunk_overlap or settings.chunk_overlap,
            strategy=request.strategy,
        )

    def _resolve_document_text(self, document: Document) -> str:
        metadata = document.document_metadata
        storage_path = metadata.get("storage_path")
        if storage_path:
            try:
                absolute_path = self.storage.get_path(storage_path)
                extension = metadata.get("extension") or Path(metadata.get("filename", "")).suffix
                return extract_text_from_file(absolute_path, extension)
            except (ValueError, OSError) as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Failed to read uploaded file: {exc}",
                ) from exc

        content = metadata.get("content")
        if isinstance(content, str) and content.strip():
            return content

        existing_chunks = self.chunk_repository.list_by_document(document.id)
        if existing_chunks:
            return "\n\n".join(chunk.content for chunk in existing_chunks)

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No text source available for chunking",
        )

    def _get_owned_document(self, user: User, document_id: uuid.UUID) -> Document:
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        source = self.source_repository.get_by_id(document.source_id)
        if source is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found",
            )

        workspace = self.workspace_repository.get_by_id(source.workspace_id)
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
        return document
