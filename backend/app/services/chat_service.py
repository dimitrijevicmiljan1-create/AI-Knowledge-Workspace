import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.chat import Chat
from app.models.chat_message import MessageRole
from app.models.user import User
from app.rag.conversation_memory import ConversationMemoryLoader, HistoryMessage
from app.repositories.chat_message_repository import ChatMessageRepository
from app.repositories.chat_repository import ChatRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.chat import (
    ChatCreateResponse,
    ChatListResponse,
    ChatMessageListResponse,
    ChatMessageResponse,
    ChatSessionCreateResponse,
    ChatSummaryResponse,
    ChatUpdateRequest,
)
from app.services.workspace_service import WorkspaceService


class ChatService:
    DEFAULT_CHAT_TITLE = "New chat"

    def __init__(self, db: Session) -> None:
        self.db = db
        self.chat_repository = ChatRepository(db)
        self.chat_message_repository = ChatMessageRepository(db)
        self.workspace_repository = WorkspaceRepository(db)
        self.workspace_service = WorkspaceService(db)
        self.memory_loader = ConversationMemoryLoader()

    def create_chat(
        self,
        user: User,
        *,
        title: str | None = None,
        workspace_id: uuid.UUID | None = None,
    ) -> ChatCreateResponse:
        workspace = (
            self.workspace_service.get_owned_workspace(user, workspace_id)
            if workspace_id is not None
            else self.workspace_service.get_user_workspace(user)
        )
        chat = self.chat_repository.create(
            user_id=user.id,
            workspace_id=workspace.id,
            title=title or self.DEFAULT_CHAT_TITLE,
        )
        return ChatCreateResponse(id=chat.id)

    def create_session(
        self,
        user: User,
        workspace_id: uuid.UUID,
        *,
        title: str | None = None,
    ) -> ChatSessionCreateResponse:
        response = self.create_chat(user, title=title, workspace_id=workspace_id)
        return ChatSessionCreateResponse(session_id=response.id)

    def list_chats(self, user: User) -> ChatListResponse:
        workspace = self.workspace_service.get_user_workspace(user)
        chats = self.chat_repository.list_by_workspace_for_user(workspace.id, user.id)
        items = [ChatSummaryResponse.model_validate(chat) for chat in chats]
        return ChatListResponse(items=items, total=len(items))

    def get_chat(self, user: User, chat_id: uuid.UUID) -> ChatSummaryResponse:
        chat = self.get_owned_chat(user, chat_id)
        return ChatSummaryResponse.model_validate(chat)

    def get_messages(self, user: User, chat_id: uuid.UUID) -> ChatMessageListResponse:
        self.get_owned_chat(user, chat_id)
        messages = self.chat_message_repository.list_by_chat(chat_id)
        items = [
            ChatMessageResponse(
                id=message.id,
                role=message.role.value,
                content=message.content,
                created_at=message.created_at,
            )
            for message in messages
            if message.role in {MessageRole.user, MessageRole.assistant}
        ]
        return ChatMessageListResponse(items=items, total=len(items))

    def update_chat(
        self,
        user: User,
        chat_id: uuid.UUID,
        chat_in: ChatUpdateRequest,
    ) -> ChatSummaryResponse:
        chat = self.get_owned_chat(user, chat_id)
        updated = self.chat_repository.update(chat, title=chat_in.title)
        return ChatSummaryResponse.model_validate(updated)

    def delete_chat(self, user: User, chat_id: uuid.UUID) -> None:
        chat = self.get_owned_chat(user, chat_id)
        self.chat_repository.delete(chat)

    def get_owned_chat(self, user: User, chat_id: uuid.UUID) -> Chat:
        chat = self.chat_repository.get_by_id_for_user(chat_id, user.id)
        if chat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )
        return chat

    def get_owned_session(self, user: User, session_id: uuid.UUID) -> Chat:
        return self.get_owned_chat(user, session_id)

    def load_conversation_history(
        self,
        user: User,
        chat_id: uuid.UUID,
    ) -> tuple[Chat, list[HistoryMessage]]:
        chat = self.chat_repository.get_by_id_for_user_with_messages(chat_id, user.id)
        if chat is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        history = [
            HistoryMessage(role=message.role.value, content=message.content)
            for message in chat.messages
            if message.role in {MessageRole.user, MessageRole.assistant}
        ]
        return chat, self.memory_loader.trim_history(history)

    def persist_exchange(
        self,
        *,
        chat_id: uuid.UUID,
        user_message: str,
        assistant_message: str,
    ) -> None:
        chat = self.chat_repository.get_by_id(chat_id)
        if chat is None:
            return

        self.chat_message_repository.create_pair(
            chat_id=chat_id,
            user_content=user_message,
            assistant_content=assistant_message,
        )

        if chat.title == self.DEFAULT_CHAT_TITLE:
            title = user_message.strip().splitlines()[0][:80] or self.DEFAULT_CHAT_TITLE
            self.chat_repository.update(chat, title=title)


# Backward-compatible aliases.
ChatSessionService = ChatService
