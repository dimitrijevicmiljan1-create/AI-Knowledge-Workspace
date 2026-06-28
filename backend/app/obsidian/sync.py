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


class ObsidianSyncService:
    """Synchronize Obsidian vault markdown notes into the knowledge base."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.vault_repository = ObsidianVaultRepository(db)
        self.sync_job_repository = ObsidianSyncJobRepository(db)
        self.source_repository = SourceRepository(db)
        self.document_repository = DocumentRepository(db)
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

        documents_created = 0
        documents_updated = 0
        documents_deleted = 0
        files_scanned = 0

        try:
            indexable_files = [
                (path, content)
                for path, content in files
                if should_index_obsidian_path(path) and content.strip()
            ]
            files_scanned = len(indexable_files)
            remote_paths = {path for path, _ in indexable_files}

            existing_documents = {
                document.path: document
                for document in self.document_repository.list_by_source(vault.source_id)
            }

            document_service = DocumentService(self.db)
            embedding_service = EmbeddingService(self.db)

            for relative_path, raw_content in indexable_files:
                content_checksum = compute_checksum(raw_content)
                existing = existing_documents.get(relative_path)
                existing_checksum = None
                if existing is not None and existing.document_metadata:
                    existing_checksum = existing.document_metadata.get("content_checksum")

                if existing is not None and existing_checksum == content_checksum:
                    embedding_service.embed_document(user, existing.id)
                    continue

                parsed = self.parser.parse(
                    path=relative_path,
                    content=raw_content,
                    vault_name=vault.vault_name,
                )
                metadata = self.parser.build_document_metadata(
                    parsed,
                    content_checksum=content_checksum,
                    workspace_id=vault.workspace_id,
                    vault_id=vault.id,
                )
                metadata["indexed_at"] = datetime.now(UTC).isoformat()

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
                embedding_service.embed_document(user, ingest_result.document.id)

                if ingest_result.ingestion_status == IngestionStatus.created:
                    documents_created += 1
                elif ingest_result.ingestion_status == IngestionStatus.updated:
                    documents_updated += 1

            for path, document in existing_documents.items():
                if path not in remote_paths:
                    self.embedding_repository.delete_by_document(document.id)
                    self.document_repository.delete(document)
                    documents_deleted += 1

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
                files_scanned=files_scanned,
                documents_created=documents_created,
                documents_updated=documents_updated,
                documents_deleted=documents_deleted,
                error_message=None,
            )
        except Exception as error:
            logger.exception("Obsidian sync failed for vault %s", vault_id)
            self.vault_repository.update(vault, sync_status=ObsidianVaultSyncStatus.failed)
            self.source_repository.update(vault.source, status=SourceStatus.failed)
            self.sync_job_repository.update(
                job,
                status=ObsidianSyncJobStatus.failed,
                completed_at=datetime.now(UTC),
                files_scanned=files_scanned,
                documents_created=documents_created,
                documents_updated=documents_updated,
                documents_deleted=documents_deleted,
                error_message=str(error),
            )

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
