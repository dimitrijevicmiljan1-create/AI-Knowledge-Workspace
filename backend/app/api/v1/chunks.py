from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chunk import ChunkPreviewResponse
from app.services.chunk_service import ChunkService

router = APIRouter(prefix="/chunks", tags=["chunks"])


@router.get(
    "/{chunk_id}",
    response_model=ChunkPreviewResponse,
    summary="Preview chunk content",
    responses={
        404: {"description": "Chunk not found"},
        403: {"description": "User is not the workspace owner"},
        200: {
            "description": "Chunk preview",
            "content": {
                "application/json": {
                    "example": {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa9",
                        "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa8",
                        "chunk_index": 0,
                        "content": "Sample chunk text",
                        "token_count": 12,
                    }
                }
            },
        },
    },
)
def get_chunk_preview(
    chunk_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ChunkPreviewResponse:
    return ChunkService(db).get_chunk_preview(current_user, chunk_id)
