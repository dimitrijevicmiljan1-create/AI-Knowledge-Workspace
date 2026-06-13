from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.search import SearchRequest, SearchResponse, SearchStatsResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.post(
    "/workspace/{workspace_id}",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search across a workspace",
    responses={
        200: {
            "description": "Semantic search results",
            "content": {
                "application/json": {
                    "example": {
                        "query": "How do I configure authentication?",
                        "top_k": 5,
                        "total_results": 2,
                        "search_id": "3fa85f64-5717-4562-b3fc-2c963f66afb0",
                        "results": [
                            {
                                "chunk_id": "3fa85f64-5717-4562-b3fc-2c963f66afa9",
                                "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa8",
                                "document_title": "Auth Guide",
                                "chunk_content": "Configure JWT authentication...",
                                "similarity_score": 0.92,
                                "source_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                                "workspace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            }
                        ],
                    }
                }
            },
        },
        401: {"description": "Unauthorized"},
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Workspace not found"},
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "query": "How do I configure authentication?",
                        "top_k": 5,
                    }
                }
            }
        }
    },
)
def search_workspace(
    workspace_id: UUID,
    search_in: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SearchResponse:
    return SearchService(db).search_workspace(current_user, workspace_id, search_in)


@router.post(
    "/document/{document_id}",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search within a document",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Document not found"},
    },
)
def search_document(
    document_id: UUID,
    search_in: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SearchResponse:
    return SearchService(db).search_document(current_user, document_id, search_in)


@router.post(
    "/source/{source_id}",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search within a source",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Source not found"},
    },
)
def search_source(
    source_id: UUID,
    search_in: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SearchResponse:
    return SearchService(db).search_source(current_user, source_id, search_in)


@router.get(
    "/stats",
    response_model=SearchStatsResponse,
    summary="Get search statistics",
    responses={
        200: {
            "description": "Search analytics for the current user",
            "content": {
                "application/json": {
                    "example": {
                        "total_searches": 42,
                        "avg_results": 4.5,
                        "most_active_workspace": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "recent_queries_count": 12,
                    }
                }
            },
        },
        401: {"description": "Unauthorized"},
    },
)
def get_search_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SearchStatsResponse:
    return SearchService(db).get_search_stats(current_user)
