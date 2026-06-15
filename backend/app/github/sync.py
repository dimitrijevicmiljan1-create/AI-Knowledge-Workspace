import logging
import threading
import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.github.auth import GitHubAuthService
from app.github.client import GitHubClient
from app.github.exceptions import GitHubAPIError
from app.github.filters import should_index_file
from app.github.parser import RepositoryFileParser
from app.models.github_repository import GitHubRepository, GitHubRepositorySyncStatus
from app.models.github_sync_job import GitHubSyncJob, GitHubSyncJobStatus
from app.models.source import SourceStatus
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.repositories.github_connection_repository import GitHubConnectionRepository
from app.repositories.github_repository_repository import GitHubRepositoryRepository
from app.repositories.github_sync_job_repository import GitHubSyncJobRepository
from app.repositories.source_repository import SourceRepository
from app.repositories.user_repository import UserRepository
from app.schemas.document import DocumentIngestRequest, IngestionStatus
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class RepositorySyncProvider(ABC):
    """Abstraction for repository sync providers (GitHub today, webhooks later)."""

    @abstractmethod
    def start_sync(self, repository_id: uuid.UUID, user: User) -> GitHubSyncJob:
        raise NotImplementedError

    @abstractmethod
    def get_latest_job(self, repository_id: uuid.UUID) -> GitHubSyncJob | None:
        raise NotImplementedError


class GitHubSyncService(RepositorySyncProvider):
    """Synchronize GitHub repository content into the knowledge base."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository_repository = GitHubRepositoryRepository(db)
        self.sync_job_repository = GitHubSyncJobRepository(db)
        self.connection_repository = GitHubConnectionRepository(db)
        self.source_repository = SourceRepository(db)
        self.document_repository = DocumentRepository(db)
        self.embedding_repository = EmbeddingRepository(db)
        self.user_repository = UserRepository(db)
        self.auth_service = GitHubAuthService(self.connection_repository)
        self.parser = RepositoryFileParser()

    def start_sync(self, repository_id: uuid.UUID, user: User) -> GitHubSyncJob:
        repository = self.repository_repository.get_by_id_for_user(repository_id, user.id)
        if repository is None:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GitHub repository not found",
            )

        if repository.sync_status == GitHubRepositorySyncStatus.syncing:
            active_job = self.sync_job_repository.get_active_for_repository(repository.id)
            if active_job is not None:
                return active_job

        job = self.sync_job_repository.create(repository_id=repository.id)
        self.repository_repository.update(
            repository,
            sync_status=GitHubRepositorySyncStatus.syncing,
        )
        self.source_repository.update(repository.source, status=SourceStatus.syncing)

        worker = threading.Thread(
            target=self._run_sync_job,
            args=(job.id, repository.id, user.id),
            daemon=True,
            name=f"github-sync-{repository.id}",
        )
        worker.start()
        return job

    def get_latest_job(self, repository_id: uuid.UUID) -> GitHubSyncJob | None:
        return self.sync_job_repository.get_latest_for_repository(repository_id)

    def execute_sync(self, job_id: uuid.UUID, repository_id: uuid.UUID, user_id: uuid.UUID) -> None:
        job = self.sync_job_repository.get_by_id(job_id)
        repository = self.repository_repository.get_by_id(repository_id)
        user = self.user_repository.get_by_id(user_id)
        if job is None or repository is None or user is None:
            return

        self.sync_job_repository.update(
            job,
            status=GitHubSyncJobStatus.processing,
            started_at=datetime.now(UTC),
        )

        documents_created = 0
        documents_updated = 0
        documents_deleted = 0
        files_scanned = 0

        try:
            connection = self.connection_repository.get_by_id(repository.connection_id)
            if connection is None:
                raise GitHubAPIError("GitHub connection not found")

            client = self.auth_service.get_client_for_connection(connection)
            owner = repository.repository_owner
            name = repository.repository_name
            branch = repository.default_branch

            commit_sha = client.get_branch_commit_sha(owner, name, branch)
            tree_entries = client.get_recursive_tree(owner, name, commit_sha)
            indexable_entries = [entry for entry in tree_entries if should_index_file(entry.path)]
            files_scanned = len(indexable_entries)

            remote_paths = {entry.path for entry in indexable_entries}
            existing_documents = {
                document.path: document
                for document in self.document_repository.list_by_source(repository.source_id)
            }

            document_service = DocumentService(self.db)
            embedding_service = EmbeddingService(self.db)

            for entry in indexable_entries:
                existing = existing_documents.get(entry.path)
                existing_blob_sha = None
                if existing is not None and existing.document_metadata:
                    existing_blob_sha = existing.document_metadata.get("blob_sha")

                if existing is not None and existing_blob_sha == entry.sha:
                    continue

                file_content = client.get_file_content(owner, name, entry.path, ref=branch)
                parsed = self.parser.parse(
                    path=entry.path,
                    content=file_content.content,
                    blob_sha=entry.sha,
                    commit_sha=commit_sha,
                    repository_owner=owner,
                    repository_name=name,
                )
                if not parsed.content.strip():
                    logger.info(
                        "Skipping empty file during GitHub sync: %s/%s@%s",
                        repository.repository_owner,
                        entry.path,
                        commit_sha,
                    )
                    continue

                metadata = self.parser.build_document_metadata(parsed)
                metadata["indexed_at"] = datetime.now(UTC).isoformat()

                ingest_result = document_service.ingest_document(
                    user,
                    DocumentIngestRequest(
                        source_id=repository.source_id,
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
            self.repository_repository.update(
                repository,
                last_commit_sha=commit_sha,
                last_synced_at=synced_at,
                sync_status=GitHubRepositorySyncStatus.ready,
            )
            self.source_repository.update(
                repository.source,
                status=SourceStatus.ready,
                last_sync_at=synced_at,
            )
            self.sync_job_repository.update(
                job,
                status=GitHubSyncJobStatus.completed,
                completed_at=synced_at,
                files_scanned=files_scanned,
                documents_created=documents_created,
                documents_updated=documents_updated,
                documents_deleted=documents_deleted,
                error_message=None,
            )
        except Exception as error:
            logger.exception("GitHub sync failed for repository %s", repository_id)
            self.repository_repository.update(
                repository,
                sync_status=GitHubRepositorySyncStatus.failed,
            )
            self.source_repository.update(repository.source, status=SourceStatus.failed)
            self.sync_job_repository.update(
                job,
                status=GitHubSyncJobStatus.failed,
                completed_at=datetime.now(UTC),
                files_scanned=files_scanned,
                documents_created=documents_created,
                documents_updated=documents_updated,
                documents_deleted=documents_deleted,
                error_message=str(error),
            )

    def _run_sync_job(self, job_id: uuid.UUID, repository_id: uuid.UUID, user_id: uuid.UUID) -> None:
        db = SessionLocal()
        try:
            GitHubSyncService(db).execute_sync(job_id, repository_id, user_id)
        finally:
            db.close()
