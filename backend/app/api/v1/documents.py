from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.document import (
    ChunkListResponse,
    DocumentIngestRequest,
    DocumentIngestResponse,
    DocumentListResponse,
    DocumentResponse,
    DocumentStatsResponse,
    DocumentUpdate,
)
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "/ingest",
    response_model=DocumentIngestResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest document content",
    responses={
        201: {
            "description": "Document ingested successfully",
            "content": {
                "application/json": {
                    "example": {
                        "document": {
                            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa8",
                            "source_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                            "title": "Getting Started Guide",
                            "path": "docs/getting-started.md",
                            "checksum": "a3f2c1...",
                            "metadata": {"format": "markdown"},
                            "indexed_at": "2026-06-13T12:00:00Z",
                            "created_at": "2026-06-13T12:00:00Z",
                            "updated_at": "2026-06-13T12:00:00Z",
                        },
                        "chunk_count": 3,
                        "ingestion_status": "created",
                    }
                }
            },
        },
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Source not found"},
        422: {"description": "Validation error"},
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "source_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                        "title": "Getting Started Guide",
                        "path": "docs/getting-started.md",
                        "content": "# Getting Started\n\nWelcome to the knowledge workspace.",
                        "metadata": {"format": "markdown"},
                    }
                }
            }
        }
    },
)
def ingest_document(
    ingest_in: DocumentIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DocumentIngestResponse:
    return DocumentService(db).ingest_document(current_user, ingest_in)


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List documents by source",
    responses={
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Source not found"},
    },
)
def list_documents(
    source_id: UUID = Query(..., description="Source identifier"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DocumentListResponse:
    return DocumentService(db).list_documents(current_user, source_id)


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document details",
    responses={
        404: {"description": "Document or source not found"},
        403: {"description": "User is not the workspace owner"},
    },
)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DocumentResponse:
    return DocumentService(db).get_document(current_user, document_id)


@router.patch(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Update document metadata",
    responses={
        404: {"description": "Document or source not found"},
        403: {"description": "User is not the workspace owner"},
    },
)
def update_document(
    document_id: UUID,
    document_in: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DocumentResponse:
    return DocumentService(db).update_document(current_user, document_id, document_in)


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
    responses={
        404: {"description": "Document or source not found"},
        403: {"description": "User is not the workspace owner"},
    },
)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    DocumentService(db).delete_document(current_user, document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{document_id}/chunks",
    response_model=ChunkListResponse,
    summary="List document chunks",
    responses={
        404: {"description": "Document or source not found"},
        403: {"description": "User is not the workspace owner"},
    },
)
def list_document_chunks(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ChunkListResponse:
    return DocumentService(db).list_chunks(current_user, document_id)


@router.get(
    "/{document_id}/stats",
    response_model=DocumentStatsResponse,
    summary="Get document statistics",
    responses={
        404: {"description": "Document or source not found"},
        403: {"description": "User is not the workspace owner"},
        200: {
            "description": "Document statistics",
            "content": {
                "application/json": {
                    "example": {
                        "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa8",
                        "chunk_count": 5,
                        "indexed_at": "2026-06-13T12:00:00Z",
                        "checksum": "a3f2c1...",
                    }
                }
            },
        },
    },
)
def get_document_stats(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DocumentStatsResponse:
    return DocumentService(db).get_document_stats(current_user, document_id)
