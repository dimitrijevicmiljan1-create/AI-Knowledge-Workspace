from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.embedding import (
    DeleteEmbeddingsResponse,
    EmbedDocumentResponse,
    EmbeddingPreviewResponse,
    EmbeddingStatsResponse,
    EmbedWorkspaceResponse,
    ReembedDocumentResponse,
)
from app.services.embedding_service import EmbeddingService

router = APIRouter(tags=["embeddings"])


@router.post(
    "/documents/{document_id}/embed",
    response_model=EmbedDocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Embed document chunks",
    responses={
        200: {
            "description": "Document embedding completed",
            "content": {
                "application/json": {
                    "example": {
                        "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa8",
                        "status": "completed",
                        "chunks_total": 5,
                        "chunks_embedded": 5,
                        "chunks_skipped": 0,
                        "chunks_failed": 0,
                        "estimated_tokens": 1200,
                        "estimated_cost": 0.000024,
                        "embedding_model": "text-embedding-3-small",
                    }
                }
            },
        },
        401: {"description": "Unauthorized"},
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Document not found"},
    },
)
def embed_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> EmbedDocumentResponse:
    return EmbeddingService(db).embed_document(current_user, document_id)


@router.post(
    "/workspaces/{workspace_id}/embed",
    response_model=EmbedWorkspaceResponse,
    status_code=status.HTTP_200_OK,
    summary="Embed all documents in a workspace",
    responses={
        200: {
            "description": "Workspace embedding completed",
            "content": {
                "application/json": {
                    "example": {
                        "workspace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                        "status": "completed",
                        "documents_total": 3,
                        "documents_embedded": 3,
                        "chunks_total": 15,
                        "chunks_embedded": 15,
                        "chunks_skipped": 0,
                        "chunks_failed": 0,
                        "estimated_tokens": 3600,
                        "estimated_cost": 0.000072,
                        "embedding_model": "text-embedding-3-small",
                    }
                }
            },
        },
        401: {"description": "Unauthorized"},
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Workspace not found"},
    },
)
def embed_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> EmbedWorkspaceResponse:
    return EmbeddingService(db).embed_workspace(current_user, workspace_id)


@router.post(
    "/documents/{document_id}/reembed",
    response_model=ReembedDocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Re-embed all document chunks",
    responses={
        200: {
            "description": "Document re-embedding completed",
            "content": {
                "application/json": {
                    "example": {
                        "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa8",
                        "status": "completed",
                        "chunks_total": 5,
                        "chunks_embedded": 5,
                        "chunks_failed": 0,
                        "estimated_tokens": 1200,
                        "estimated_cost": 0.000024,
                        "embedding_model": "text-embedding-3-small",
                    }
                }
            },
        },
        401: {"description": "Unauthorized"},
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Document not found"},
    },
)
def reembed_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ReembedDocumentResponse:
    return EmbeddingService(db).reembed_document(current_user, document_id)


@router.delete(
    "/documents/{document_id}/embeddings",
    response_model=DeleteEmbeddingsResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete document embeddings",
    responses={
        200: {
            "description": "Embeddings deleted",
            "content": {
                "application/json": {
                    "example": {
                        "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa8",
                        "embeddings_deleted": 5,
                    }
                }
            },
        },
        401: {"description": "Unauthorized"},
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Document not found"},
    },
)
def delete_document_embeddings(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DeleteEmbeddingsResponse:
    return EmbeddingService(db).delete_embeddings(current_user, document_id)


@router.get(
    "/chunks/{chunk_id}/embedding",
    response_model=EmbeddingPreviewResponse,
    summary="Get chunk embedding preview",
    responses={
        200: {
            "description": "Embedding preview metadata",
            "content": {
                "application/json": {
                    "example": {
                        "chunk_id": "3fa85f64-5717-4562-b3fc-2c963f66afa9",
                        "dimension": 1536,
                        "created_at": "2026-06-13T12:00:00Z",
                    }
                }
            },
        },
        401: {"description": "Unauthorized"},
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Chunk or embedding not found"},
    },
)
def get_chunk_embedding_preview(
    chunk_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> EmbeddingPreviewResponse:
    return EmbeddingService(db).get_chunk_embedding_preview(current_user, chunk_id)


@router.get(
    "/embeddings/stats",
    response_model=EmbeddingStatsResponse,
    summary="Get embedding statistics",
    responses={
        200: {
            "description": "Global embedding statistics",
            "content": {
                "application/json": {
                    "example": {
                        "total_embeddings": 128,
                        "total_chunks_embedded": 128,
                        "estimated_cost": 0.0024,
                        "last_embedding_time": "2026-06-13T12:00:00Z",
                    }
                }
            },
        },
        401: {"description": "Unauthorized"},
    },
)
def get_embedding_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> EmbeddingStatsResponse:
    return EmbeddingService(db).get_embedding_stats(current_user)
