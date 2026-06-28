import logging
import threading
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.obsidian_sync_job import ObsidianSyncJob, ObsidianSyncJobStatus
from app.models.obsidian_vault import ObsidianVaultSyncStatus
from app.models.source import SourceStatus
from app.models.user import User
from app.obsidian.filters import should_index_obsidian_path
from app.obsidian.parser import ObsidianNoteParser
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.repositories.obsidian_sync_job_repository import ObsidianSyncJobRepository
from app.repositories.obsidian_vault_repository import ObsidianVaultRepository
from app.repositories.source_repository import SourceRepository
from app.repositories.user_repository import UserRepository
from app.schemas.document import DocumentIngestRequest, IngestionStatus
from app.services.checksum import compute_checksum
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ObsidianVaultFile:
    relative_path: str
    content: str


@dataclass
class ObsidianSyncStats:
    markdown_files_discovered: int = 0
    markdown_files_indexed: int = 0
    chunks_created: int = 0
    embeddings_stored: int = 0
    documents_created: int = 0
    documents_updated: int = 0
    documents_deleted: int = 0
    file_errors: list[str] | None = None


class ObsidianSyncService:
    """Synchronize Obsidian vault markdown notes into the knowledge base."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.vault_repository = ObsidianVaultRepository(db)
        self.sync_job_repository = ObsidianSyncJobRepository(db)
        self.source_repository = SourceRepository(db)
        self.document_repository = DocumentRepository(db)
        self.chunk_repository = ChunkRepository(db)
        self.embedding_repository = EmbeddingRepository(db)
        self.user_repository = UserRepository(db)
        self.parser = ObsidianNoteParser()

    def start_sync(
        self,
        vault_id: uuid.UUID,
        user: User,
        files: list[ObsidianVaultFile],
    ) -> ObsidianSyncJob:
        vault = self.vault_repository.get_by_id_for_user(vault_id, user.id)
        if vault is None:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Obsidian vault not found",
            )

        if vault.sync_status == ObsidianVaultSyncStatus.syncing:
            active_job = self.sync_job_repository.get_active_for_vault(vault.id)
            if active_job is not None:
                return active_job

        logger.info(
            "Starting Obsidian sync vault_id=%s source_id=%s markdown_files=%d",
            vault.id,
            vault.source_id,
            len(files),
        )

        job = self.sync_job_repository.create(vault_id=vault.id)
        self.vault_repository.update(vault, sync_status=ObsidianVaultSyncStatus.syncing)
        self.source_repository.update(vault.source, status=SourceStatus.syncing)

        serialized_files = [(item.relative_path, item.content) for item in files]
        worker = threading.Thread(
            target=self._run_sync_job,
            args=(job.id, vault.id, user.id, serialized_files),
            daemon=True,
            name=f"obsidian-sync-{vault.id}",
        )
        worker.start()
        return job

    def get_latest_job(self, vault_id: uuid.UUID):
        return self.sync_job_repository.get_latest_for_vault(vault_id)

    def execute_sync(
        self,
        job_id: uuid.UUID,
        vault_id: uuid.UUID,
        user_id: uuid.UUID,
        files: list[tuple[str, str]],
    ) -> None:
        job = self.sync_job_repository.get_by_id(job_id)
        vault = self.vault_repository.get_by_id(vault_id)
        user = self.user_repository.get_by_id(user_id)
        if job is None or vault is None or user is None:
            return

        self.sync_job_repository.update(
            job,
            status=ObsidianSyncJobStatus.processing,
            started_at=datetime.now(UTC),
        )

        stats = ObsidianSyncStats()
        file_errors: list[str] = []

        try:
            markdown_candidates = [
                (path, content)
                for path, content in files
                if path.lower().endswith(".md") and content.strip()
            ]
            indexable_files = [
                (path, content)
                for path, content in markdown_candidates
                if should_index_obsidian_path(path)
            ]

            stats.markdown_files_discovered = len(indexable_files)
            logger.info(
                "Obsidian sync vault_id=%s discovered=%d indexable=%d (from %d uploaded)",
                vault_id,
                len(markdown_candidates),
                len(indexable_files),
                len(files),
            )

            remote_paths = {path for path, _ in indexable_files}
            existing_documents = {
                document.path: document
                for document in self.document_repository.list_by_source(vault.source_id)
            }

            document_service = DocumentService(self.db)
            embedding_service = EmbeddingService(self.db)

            for relative_path, raw_content in indexable_files:
                try:
                    file_stats = self._index_note(
                        user=user,
                        vault=vault,
                        relative_path=relative_path,
                        raw_content=raw_content,
                        existing_documents=existing_documents,
                        document_service=document_service,
                        embedding_service=embedding_service,
                    )
                    stats.markdown_files_indexed += 1
                    stats.chunks_created += file_stats["chunks_created"]
                    stats.embeddings_stored += file_stats["embeddings_stored"]
                    if file_stats["documents_created"]:
                        stats.documents_created += 1
                    if file_stats["documents_updated"]:
                        stats.documents_updated += 1
                except Exception as error:
                    message = f"{relative_path}: {error}"
                    logger.exception("Failed to index Obsidian note %s", relative_path)
                    file_errors.append(message)

            for path, document in existing_documents.items():
                if path not in remote_paths:
                    self.embedding_repository.delete_by_document(document.id)
                    self.document_repository.delete(document)
                    stats.documents_deleted += 1

            total_embeddings = self.embedding_repository.count_by_source(vault.source_id)
            stats.embeddings_stored = total_embeddings

            logger.info(
                "Obsidian sync vault_id=%s markdown_indexed=%d chunks_created=%d embeddings_total=%d",
                vault_id,
                stats.markdown_files_indexed,
                stats.chunks_created,
                stats.embeddings_stored,
            )

            if stats.markdown_files_discovered > 0 and stats.embeddings_stored == 0:
                raise RuntimeError(
                    "Markdown files were discovered but no embeddings were stored. "
                    f"Errors: {'; '.join(file_errors) if file_errors else 'none'}"
                )

            if file_errors and stats.embeddings_stored == 0:
                raise RuntimeError("; ".join(file_errors))

            synced_at = datetime.now(UTC)
            self.vault_repository.update(
                vault,
                last_synced_at=synced_at,
                sync_status=ObsidianVaultSyncStatus.ready,
            )
            self.source_repository.update(
                vault.source,
                status=SourceStatus.ready,
                last_sync_at=synced_at,
            )
            self.sync_job_repository.update(
                job,
                status=ObsidianSyncJobStatus.completed,
                completed_at=synced_at,
                files_scanned=stats.markdown_files_discovered,
                documents_created=stats.documents_created,
                documents_updated=stats.documents_updated,
                documents_deleted=stats.documents_deleted,
                error_message="; ".join(file_errors[:3]) if file_errors else None,
            )
        except Exception as error:
            logger.exception("Obsidian sync failed for vault %s", vault_id)
            self.vault_repository.update(vault, sync_status=ObsidianVaultSyncStatus.failed)
            if stats.embeddings_stored > 0:
                self.source_repository.update(
                    vault.source,
                    status=SourceStatus.ready,
                    last_sync_at=datetime.now(UTC),
                )
            else:
                self.source_repository.update(vault.source, status=SourceStatus.failed)
            self.sync_job_repository.update(
                job,
                status=ObsidianSyncJobStatus.failed,
                completed_at=datetime.now(UTC),
                files_scanned=stats.markdown_files_discovered,
                documents_created=stats.documents_created,
                documents_updated=stats.documents_updated,
                documents_deleted=stats.documents_deleted,
                error_message=str(error),
            )

    def _index_note(
        self,
        *,
        user: User,
        vault,
        relative_path: str,
        raw_content: str,
        existing_documents: dict,
        document_service: DocumentService,
        embedding_service: EmbeddingService,
    ) -> dict[str, int]:
        parsed = self.parser.parse(
            path=relative_path,
            content=raw_content,
            vault_name=vault.vault_name,
        )
        content_checksum = compute_checksum(raw_content)
        metadata = self.parser.build_document_metadata(
            parsed,
            content_checksum=content_checksum,
            workspace_id=vault.workspace_id,
            vault_id=vault.id,
        )
        metadata["indexed_at"] = datetime.now(UTC).isoformat()

        existing = existing_documents.get(relative_path)
        chunks_before = (
            self.chunk_repository.count_by_document(existing.id) if existing is not None else 0
        )

        ingest_result = document_service.ingest_document(
            user,
            DocumentIngestRequest(
                source_id=vault.source_id,
                title=parsed.title,
                path=parsed.path,
                content=parsed.content,
                metadata=metadata,
            ),
        )
        document = ingest_result.document

        documents_created = 1 if ingest_result.ingestion_status == IngestionStatus.created else 0
        documents_updated = 1 if ingest_result.ingestion_status == IngestionStatus.updated else 0

        chunks_after = self.chunk_repository.count_by_document(document.id)
        chunks_created = chunks_after if chunks_before == 0 else max(chunks_after - chunks_before, 0)

        embedding_service.embed_document(user, document.id)
        embeddings_stored = self.embedding_repository.count_by_document(document.id)

        if chunks_after > 0 and embeddings_stored == 0:
            raise RuntimeError(
                f"Created {chunks_after} chunks but stored 0 embeddings for {relative_path}"
            )

        existing_documents[relative_path] = document
        return {
            "documents_created": documents_created,
            "documents_updated": documents_updated,
            "chunks_created": chunks_created,
            "embeddings_stored": embeddings_stored,
        }

    def _run_sync_job(
        self,
        job_id: uuid.UUID,
        vault_id: uuid.UUID,
        user_id: uuid.UUID,
        files: list[tuple[str, str]],
    ) -> None:
        db = SessionLocal()
        try:
            ObsidianSyncService(db).execute_sync(job_id, vault_id, user_id, files)
        finally:
            db.close()
