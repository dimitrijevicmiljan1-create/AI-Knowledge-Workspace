import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.base import EmbeddingProvider
from app.ai.factory import get_embedding_provider
from app.core.config import settings
from app.models.document import Document
from app.models.source import Source
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.repositories.search_history_repository import SearchHistoryRepository
from app.repositories.source_repository import SourceRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.search import SearchRequest, SearchResponse, SearchResult, SearchStatsResponse
from app.search.filters import SearchFilters
from app.search.ranking import SearchHit
from app.search.vector_search import VectorSearchEngine
from app.services.retrieval_source_service import RetrievalSourceService


class SearchService:
    def __init__(
        self,
        db: Session,
        provider: EmbeddingProvider | None = None,
    ) -> None:
        self.db = db
        self.provider = provider or get_embedding_provider()
        self.vector_search = VectorSearchEngine(db)
        self.search_history_repository = SearchHistoryRepository(db)
        self.workspace_repository = WorkspaceRepository(db)
        self.source_repository = SourceRepository(db)
        self.document_repository = DocumentRepository(db)
        self.retrieval_source_service = RetrievalSourceService(db)

    def search_workspace(
        self,
        user: User,
        workspace_id: uuid.UUID,
        search_in: SearchRequest,
    ) -> SearchResponse:
        self._ensure_workspace_owner(user, workspace_id)
        filters = self._build_filters(search_in).apply_workspace(workspace_id)
        retrieval_source_ids = self.retrieval_source_service.list_retrieval_source_ids(workspace_id)
        filters = filters.with_source_ids(retrieval_source_ids)
        return self._execute_search(
            user=user,
            workspace_id=workspace_id,
            search_in=search_in,
            filters=filters,
        )

    def search_document(
        self,
        user: User,
        document_id: uuid.UUID,
        search_in: SearchRequest,
    ) -> SearchResponse:
        document = self._get_owned_document(user, document_id)
        source = self.source_repository.get_by_id(document.source_id)
        assert source is not None
        filters = self._build_filters(search_in).apply_document(document_id)
        filters = SearchFilters(
            workspace_id=source.workspace_id,
            source_id=filters.source_id,
            document_id=document_id,
            date_from=filters.date_from,
            date_to=filters.date_to,
        )
        return self._execute_search(
            user=user,
            workspace_id=source.workspace_id,
            search_in=search_in,
            filters=filters,
        )

    def search_source(
        self,
        user: User,
        source_id: uuid.UUID,
        search_in: SearchRequest,
    ) -> SearchResponse:
        source = self._get_owned_source(user, source_id)
        filters = self._build_filters(search_in).apply_source(source_id)
        filters = SearchFilters(
            workspace_id=source.workspace_id,
            source_id=source_id,
            document_id=filters.document_id,
            date_from=filters.date_from,
            date_to=filters.date_to,
        )
        return self._execute_search(
            user=user,
            workspace_id=source.workspace_id,
            search_in=search_in,
            filters=filters,
        )

    def similar_chunks(
        self,
        user: User,
        chunk_id: uuid.UUID,
        *,
        top_k: int | None = None,
    ) -> SearchResponse:
        from app.repositories.chunk_repository import ChunkRepository

        chunk_repository = ChunkRepository(self.db)
        chunk = chunk_repository.get_by_id(chunk_id)
        if chunk is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chunk not found")

        document = self._get_owned_document(user, chunk.document_id)
        source = self.source_repository.get_by_id(document.source_id)
        assert source is not None

        effective_top_k = self._resolve_top_k(top_k)
        filters = SearchFilters(workspace_id=source.workspace_id)
        retrieval_source_ids = self.retrieval_source_service.list_retrieval_source_ids(source.workspace_id)
        filters = filters.with_source_ids(retrieval_source_ids)
        hits = self.vector_search.similar_to_chunk(
            chunk_id,
            filters=filters,
            top_k=effective_top_k,
        )
        return SearchResponse(
            query=f"similar:{chunk_id}",
            top_k=effective_top_k,
            total_results=len(hits),
            results=[self._to_search_result(hit) for hit in hits],
        )

    def get_search_stats(self, user: User) -> SearchStatsResponse:
        return SearchStatsResponse(
            total_searches=self.search_history_repository.count_by_user(user.id),
            avg_results=self.search_history_repository.average_results_by_user(user.id),
            most_active_workspace=self.search_history_repository.most_active_workspace(user.id),
            recent_queries_count=self.search_history_repository.recent_queries_count(
                user.id,
                days=settings.search_recent_days,
            ),
        )

    def _execute_search(
        self,
        *,
        user: User,
        workspace_id: uuid.UUID,
        search_in: SearchRequest,
        filters: SearchFilters,
    ) -> SearchResponse:
        top_k = self._resolve_top_k(search_in.top_k)
        query_vector = self.provider.generate_embedding(search_in.query)
        hits = self.vector_search.search(query_vector, filters=filters, top_k=top_k)
        history = self.search_history_repository.create(
            user_id=user.id,
            workspace_id=workspace_id,
            query=search_in.query,
            result_count=len(hits),
        )
        return SearchResponse(
            query=search_in.query,
            top_k=top_k,
            total_results=len(hits),
            results=[self._to_search_result(hit) for hit in hits],
            search_id=history.id,
        )

    def _build_filters(self, search_in: SearchRequest) -> SearchFilters:
        return SearchFilters(
            source_id=search_in.source_id,
            document_id=search_in.document_id,
            date_from=search_in.date_from,
            date_to=search_in.date_to,
        )

    def _resolve_top_k(self, top_k: int | None) -> int:
        if top_k is None:
            return settings.search_default_top_k
        return min(top_k, settings.search_max_top_k)

    def _to_search_result(self, hit: SearchHit) -> SearchResult:
        return SearchResult(
            chunk_id=hit.chunk_id,
            document_id=hit.document_id,
            document_title=hit.document_title,
            document_path=hit.document_path,
            chunk_content=hit.chunk_content,
            similarity_score=hit.similarity_score,
            source_id=hit.source_id,
            workspace_id=hit.workspace_id,
            source_type=hit.source_type,
            repository_name=hit.repository_name,
            file_path=hit.file_path,
            vault_name=hit.vault_name,
        )

    def _get_owned_source(self, user: User, source_id: uuid.UUID) -> Source:
        source = self.source_repository.get_by_id(source_id)
        if source is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
        self._ensure_workspace_owner(user, source.workspace_id)
        return source

    def _get_owned_document(self, user: User, document_id: uuid.UUID) -> Document:
        document = self.document_repository.get_by_id(document_id)
        if document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
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
