from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatCreateRequest,
    ChatCreateResponse,
    ChatListResponse,
    ChatMessageListResponse,
    ChatSummaryResponse,
    ChatUpdateRequest,
    SessionMessageRequest,
    SessionMessageResponse,
)
from app.rag.rag_service import RAGService
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get(
    "",
    response_model=ChatListResponse,
    summary="List chats for the current user's workspace",
)
def list_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ChatListResponse:
    return ChatService(db).list_chats(current_user)


@router.post(
    "",
    response_model=ChatCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat",
)
def create_chat(
    chat_in: ChatCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ChatCreateResponse:
    return ChatService(db).create_chat(current_user, title=chat_in.title)


@router.get(
    "/{chat_id}",
    response_model=ChatSummaryResponse,
    summary="Get chat metadata",
)
def get_chat(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ChatSummaryResponse:
    return ChatService(db).get_chat(current_user, chat_id)


@router.patch(
    "/{chat_id}",
    response_model=ChatSummaryResponse,
    summary="Update chat metadata",
)
def update_chat(
    chat_id: UUID,
    chat_in: ChatUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ChatSummaryResponse:
    return ChatService(db).update_chat(current_user, chat_id, chat_in)


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a chat",
)
def delete_chat(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    ChatService(db).delete_chat(current_user, chat_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{chat_id}/messages",
    response_model=ChatMessageListResponse,
    summary="List messages in a chat",
)
def list_chat_messages(
    chat_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ChatMessageListResponse:
    return ChatService(db).get_messages(current_user, chat_id)


@router.post(
    "/{chat_id}/messages",
    response_model=SessionMessageResponse,
    summary="Send a message in a chat",
)
def send_chat_message(
    chat_id: UUID,
    message_in: SessionMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SessionMessageResponse:
    return RAGService(db).chat_message(current_user, chat_id, message_in)
