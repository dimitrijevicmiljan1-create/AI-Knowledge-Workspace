import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.chat_message import MessageRole
from app.models.chat_session import ChatSession
from app.models.user import User
from app.rag.conversation_memory import ConversationMemoryLoader, HistoryMessage
from app.repositories.chat_message_repository import ChatMessageRepository
from app.repositories.chat_session_repository import ChatSessionRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.chat import ChatSessionCreateResponse, ChatSessionResponse


class ChatSessionService:
    DEFAULT_SESSION_TITLE = "New conversation"

    def __init__(self, db: Session) -> None:
        self.db = db
        self.chat_session_repository = ChatSessionRepository(db)
        self.chat_message_repository = ChatMessageRepository(db)
        self.workspace_repository = WorkspaceRepository(db)
        self.memory_loader = ConversationMemoryLoader()

    def create_session(
        self,
        user: User,
        workspace_id: uuid.UUID,
        *,
        title: str | None = None,
    ) -> ChatSessionCreateResponse:
        self._ensure_workspace_owner(user, workspace_id)
        session = self.chat_session_repository.create(
            user_id=user.id,
            workspace_id=workspace_id,
            title=title or self.DEFAULT_SESSION_TITLE,
        )
        return ChatSessionCreateResponse(session_id=session.id)

    def get_owned_session(self, user: User, session_id: uuid.UUID) -> ChatSession:
        session = self.chat_session_repository.get_by_id_for_user(session_id, user.id)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found",
            )
        return session

    def get_session(self, user: User, session_id: uuid.UUID) -> ChatSessionResponse:
        session = self.get_owned_session(user, session_id)
        return ChatSessionResponse.model_validate(session)

    def load_conversation_history(
        self,
        user: User,
        session_id: uuid.UUID,
    ) -> tuple[ChatSession, list[HistoryMessage]]:
        session = self.chat_session_repository.get_by_id_for_user_with_messages(
            session_id,
            user.id,
        )
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found",
            )

        history = [
            HistoryMessage(role=message.role.value, content=message.content)
            for message in session.messages
            if message.role in {MessageRole.user, MessageRole.assistant}
        ]
        return session, self.memory_loader.trim_history(history)

    def persist_exchange(
        self,
        *,
        session_id: uuid.UUID,
        user_message: str,
        assistant_message: str,
    ) -> None:
        self.chat_message_repository.create_pair(
            session_id=session_id,
            user_content=user_message,
            assistant_content=assistant_message,
        )

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
