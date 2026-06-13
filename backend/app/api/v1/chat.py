from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.rag.rag_service import RAGService
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "/workspace/{workspace_id}",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question across a workspace",
    responses={
        200: {
            "description": "RAG answer with citations",
            "content": {
                "application/json": {
                    "example": {
                        "answer": "JWT authentication is configured using a secret key stored in JWT_SECRET_KEY [1].",
                        "citations": [
                            {
                                "chunk_id": "3fa85f64-5717-4562-b3fc-2c963f66afa9",
                                "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa8",
                                "source_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                                "document_title": "Auth Guide",
                            }
                        ],
                        "retrieved_chunks": [],
                        "processing_time": 1.234,
                        "exchange_id": "3fa85f64-5717-4562-b3fc-2c963f66afb1",
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
                        "question": "How do I configure JWT authentication?",
                        "top_k": 5,
                    }
                }
            }
        }
    },
)
def chat_workspace(
    workspace_id: UUID,
    chat_in: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ChatResponse:
    return RAGService(db).chat_workspace(current_user, workspace_id, chat_in)


@router.post(
    "/source/{source_id}",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question within a source",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Source not found"},
    },
)
def chat_source(
    source_id: UUID,
    chat_in: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ChatResponse:
    return RAGService(db).chat_source(current_user, source_id, chat_in)


@router.post(
    "/document/{document_id}",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question within a document",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Document not found"},
    },
)
def chat_document(
    document_id: UUID,
    chat_in: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ChatResponse:
    return RAGService(db).chat_document(current_user, document_id, chat_in)
