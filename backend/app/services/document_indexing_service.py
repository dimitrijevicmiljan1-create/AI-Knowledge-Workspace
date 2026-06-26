import logging
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.source import SourceStatus
from app.models.user import User
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.repositories.source_repository import SourceRepository
from app.repositories.user_settings_repository import UserSettingsRepository
from app.services.chunk_service import ChunkService
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class DocumentIndexingService:
    """Orchestrates chunking and embedding for uploaded documents."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.document_repository = DocumentRepository(db)
        self.chunk_repository = ChunkRepository(db)
        self.embedding_repository = EmbeddingRepository(db)
        self.source_repository = SourceRepository(db)
        self.user_settings_repository = UserSettingsRepository(db)

    def should_auto_index(self, user: User) -> bool:
        settings = self.user_settings_repository.get_or_create(user.id)
        return settings.auto_index_uploads

    def is_document_indexed(self, document_id: uuid.UUID) -> bool:
        chunk_count = self.chunk_repository.count_by_document(document_id)
        if chunk_count == 0:
            return False
        embedding_count = self.embedding_repository.count_by_document(document_id)
        return embedding_count > 0

    def index_document(self, user: User, document_id: uuid.UUID) -> bool:
        if self.is_document_indexed(document_id):
            return True

        document = self.document_repository.get_by_id(document_id)
        if document is None:
            return False

        try:
            chunk_service = ChunkService(self.db)
            embedding_service = EmbeddingService(self.db)

            if self.chunk_repository.count_by_document(document_id) == 0:
                chunk_service.chunk_document(user, document_id, None)

            embed_result = embedding_service.embed_document(user, document_id)
            if embed_result.chunks_embedded == 0 and embed_result.chunks_total > 0:
                if self.embedding_repository.count_by_document(document_id) == 0:
                    logger.warning(
                        "Document %s chunking succeeded but embedding produced no vectors",
                        document_id,
                    )
                    return False

            self._mark_source_ready(document)
            return self.is_document_indexed(document_id)
        except HTTPException:
            logger.exception("Failed to index document %s", document_id)
            return False
        except Exception:
            logger.exception("Unexpected error indexing document %s", document_id)
            return False

    def _mark_source_ready(self, document: Document) -> None:
        source = self.source_repository.get_by_id(document.source_id)
        if source is None:
            return
        indexed_at = document.indexed_at
        if indexed_at is None:
            return
        self.source_repository.update(
            source,
            status=SourceStatus.ready,
            last_sync_at=indexed_at,
        )
