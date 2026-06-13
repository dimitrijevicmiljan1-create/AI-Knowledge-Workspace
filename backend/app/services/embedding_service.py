import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.base import EmbeddingProvider
from app.ai.factory import get_embedding_provider
from app.ai.openai.exceptions import EmbeddingDimensionError, OpenAIClientError
from app.core.config import settings
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.user import User
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.repositories.source_repository import SourceRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.embedding import (
    DeleteEmbeddingsResponse,
    EmbedDocumentResponse,
    EmbeddingJobStatus,
    EmbeddingPreviewResponse,
    EmbeddingStatsResponse,
    EmbedWorkspaceResponse,
    ReembedDocumentResponse,
)
from app.services.embedding_job_tracker import embedding_job_tracker


class EmbeddingService:
    COST_PER_TOKEN = settings.embedding_cost_per_million_tokens / 1_000_000

    def __init__(
        self,
        db: Session,
        provider: EmbeddingProvider | None = None,
    ) -> None:
        self.db = db
        self.provider = provider or get_embedding_provider()
        self.embedding_repository = EmbeddingRepository(db)
        self.chunk_repository = ChunkRepository(db)
        self.document_repository = DocumentRepository(db)
        self.source_repository = SourceRepository(db)
        self.workspace_repository = WorkspaceRepository(db)

    def embed_chunk(self, user: User, chunk_id: uuid.UUID) -> EmbedDocumentResponse:
        chunk = self._get_owned_chunk(user, chunk_id)
        return self._embed_document_chunks(
            document=chunk.document,
            chunks=[chunk],
            force=False,
        )

    def embed_document(self, user: User, document_id: uuid.UUID) -> EmbedDocumentResponse:
        document = self._get_owned_document(user, document_id)
        chunks = self.chunk_repository.list_by_document(document.id)
        return self._embed_document_chunks(document=document, chunks=chunks, force=False)

    def embed_workspace(self, user: User, workspace_id: uuid.UUID) -> EmbedWorkspaceResponse:
        self._ensure_workspace_owner(user, workspace_id)
        job_key = f"workspace:{workspace_id}"
        embedding_job_tracker.set_status(job_key, EmbeddingJobStatus.processing)

        documents = self.document_repository.list_by_workspace(workspace_id)
        chunks_total = 0
        chunks_embedded = 0
        chunks_skipped = 0
        chunks_failed = 0
        estimated_tokens = 0
        documents_embedded = 0

        try:
            for document in documents:
                document_chunks = self.chunk_repository.list_by_document(document.id)
                chunks_total += len(document_chunks)
                result = self._embed_document_chunks(
                    document=document,
                    chunks=document_chunks,
                    force=False,
                )
                if result.chunks_embedded > 0:
                    documents_embedded += 1
                chunks_embedded += result.chunks_embedded
                chunks_skipped += result.chunks_skipped
                chunks_failed += result.chunks_failed
                estimated_tokens += result.estimated_tokens

            final_status = self._resolve_status(chunks_total, chunks_embedded, chunks_failed)
            embedding_job_tracker.set_status(job_key, final_status)
            return EmbedWorkspaceResponse(
                workspace_id=workspace_id,
                status=final_status,
                documents_total=len(documents),
                documents_embedded=documents_embedded,
                chunks_total=chunks_total,
                chunks_embedded=chunks_embedded,
                chunks_skipped=chunks_skipped,
                chunks_failed=chunks_failed,
                estimated_tokens=estimated_tokens,
                estimated_cost=self._estimate_cost(estimated_tokens),
                embedding_model=self.provider.model_name,
            )
        except Exception:
            embedding_job_tracker.set_status(job_key, EmbeddingJobStatus.failed)
            raise

    def reembed_document(self, user: User, document_id: uuid.UUID) -> ReembedDocumentResponse:
        document = self._get_owned_document(user, document_id)
        chunks = self.chunk_repository.list_by_document(document.id)
        self.embedding_repository.delete_by_document(document.id)
        result = self._embed_document_chunks(document=document, chunks=chunks, force=True)
        return ReembedDocumentResponse(
            document_id=document.id,
            status=result.status,
            chunks_total=result.chunks_total,
            chunks_embedded=result.chunks_embedded,
            chunks_failed=result.chunks_failed,
            estimated_tokens=result.estimated_tokens,
            estimated_cost=result.estimated_cost,
            embedding_model=result.embedding_model,
        )

    def delete_embeddings(self, user: User, document_id: uuid.UUID) -> DeleteEmbeddingsResponse:
        document = self._get_owned_document(user, document_id)
        deleted_count = self.embedding_repository.delete_by_document(document.id)
        chunks = self.chunk_repository.list_by_document(document.id)
        for chunk in chunks:
            chunk.embedding_model = None
        self.db.commit()
        return DeleteEmbeddingsResponse(document_id=document.id, embeddings_deleted=deleted_count)

    def get_chunk_embedding_preview(
        self,
        user: User,
        chunk_id: uuid.UUID,
    ) -> EmbeddingPreviewResponse:
        chunk = self._get_owned_chunk(user, chunk_id)
        embedding = self.embedding_repository.get_by_chunk_id(chunk.id)
        if embedding is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Embedding not found for chunk",
            )
        return EmbeddingPreviewResponse(
            chunk_id=chunk.id,
            dimension=len(embedding.vector),
            created_at=embedding.created_at,
        )

    def get_embedding_stats(self, user: User) -> EmbeddingStatsResponse:
        total_embeddings = self.embedding_repository.count_all()
        total_tokens = self.embedding_repository.get_total_tokens_embedded()
        return EmbeddingStatsResponse(
            total_embeddings=total_embeddings,
            total_chunks_embedded=total_embeddings,
            estimated_cost=self._estimate_cost(total_tokens),
            last_embedding_time=self.embedding_repository.get_last_created_at(),
        )

    def _embed_document_chunks(
        self,
        *,
        document: Document,
        chunks: list[Chunk],
        force: bool,
    ) -> EmbedDocumentResponse:
        job_key = f"document:{document.id}"
        embedding_job_tracker.set_status(job_key, EmbeddingJobStatus.processing)

        chunks_to_embed = self._select_chunks_for_embedding(chunks, force=force)
        chunks_skipped = len(chunks) - len(chunks_to_embed)
        chunks_failed = 0
        chunks_embedded = 0
        estimated_tokens = 0

        if not chunks_to_embed:
            status_value = EmbeddingJobStatus.completed
            embedding_job_tracker.set_status(job_key, status_value)
            return EmbedDocumentResponse(
                document_id=document.id,
                status=status_value,
                chunks_total=len(chunks),
                chunks_embedded=0,
                chunks_skipped=chunks_skipped,
                chunks_failed=0,
                estimated_tokens=0,
                estimated_cost=0.0,
                embedding_model=self.provider.model_name,
            )

        try:
            texts = [chunk.content for chunk in chunks_to_embed]
            vectors = self.provider.generate_embeddings(texts)
            if len(vectors) != len(chunks_to_embed):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Embedding provider returned an unexpected number of vectors",
                )
            self._validate_vector_dimensions(vectors)

            embedding_payload = [
                {"chunk_id": chunk.id, "vector": vector}
                for chunk, vector in zip(chunks_to_embed, vectors, strict=True)
            ]
            self.embedding_repository.create_batch(embedding_payload)
            chunk_ids = [chunk.id for chunk in chunks_to_embed]
            self.chunk_repository.update_embedding_models(chunk_ids, self.provider.model_name)

            chunks_embedded = len(chunks_to_embed)
            estimated_tokens = sum(chunk.token_count or 0 for chunk in chunks_to_embed)
            status_value = EmbeddingJobStatus.completed
            embedding_job_tracker.set_status(job_key, status_value)
        except (OpenAIClientError, EmbeddingDimensionError) as error:
            chunks_failed = len(chunks_to_embed)
            status_value = EmbeddingJobStatus.failed
            embedding_job_tracker.set_status(job_key, status_value)
            if isinstance(error, EmbeddingDimensionError):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=str(error),
                ) from error
            raise
        except Exception:
            chunks_failed = len(chunks_to_embed)
            embedding_job_tracker.set_status(job_key, EmbeddingJobStatus.failed)
            raise

        return EmbedDocumentResponse(
            document_id=document.id,
            status=status_value,
            chunks_total=len(chunks),
            chunks_embedded=chunks_embedded,
            chunks_skipped=chunks_skipped,
            chunks_failed=chunks_failed,
            estimated_tokens=estimated_tokens,
            estimated_cost=self._estimate_cost(estimated_tokens),
            embedding_model=self.provider.model_name,
        )

    def _select_chunks_for_embedding(self, chunks: list[Chunk], *, force: bool) -> list[Chunk]:
        if force:
            return chunks

        selected: list[Chunk] = []
        for chunk in chunks:
            existing = self.embedding_repository.get_by_chunk_id(chunk.id)
            if existing is not None and chunk.embedding_model == self.provider.model_name:
                continue
            selected.append(chunk)
        return selected

    def _resolve_status(
        self,
        chunks_total: int,
        chunks_embedded: int,
        chunks_failed: int,
    ) -> EmbeddingJobStatus:
        if chunks_failed > 0 and chunks_embedded == 0:
            return EmbeddingJobStatus.failed
        if chunks_embedded == 0 and chunks_total == 0:
            return EmbeddingJobStatus.completed
        if chunks_failed > 0:
            return EmbeddingJobStatus.failed
        return EmbeddingJobStatus.completed

    def _estimate_cost(self, token_count: int) -> float:
        return round(token_count * self.COST_PER_TOKEN, 6)

    def _validate_vector_dimensions(self, vectors: list[list[float]]) -> None:
        for vector in vectors:
            if len(vector) != settings.embedding_dimensions:
                raise EmbeddingDimensionError(settings.embedding_dimensions, len(vector))

    def _get_owned_document(self, user: User, document_id: uuid.UUID) -> Document:
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        self._get_owned_source(user, document.source_id)
        return document

    def _get_owned_chunk(self, user: User, chunk_id: uuid.UUID) -> Chunk:
        chunk = self.chunk_repository.get_by_id(chunk_id)
        if chunk is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chunk not found",
            )
        self._get_owned_document(user, chunk.document_id)
        return chunk

    def _get_owned_source(self, user: User, source_id: uuid.UUID):
        source = self.source_repository.get_by_id(source_id)
        if source is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found",
            )
        self._ensure_workspace_owner(user, source.workspace_id)
        return source

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
