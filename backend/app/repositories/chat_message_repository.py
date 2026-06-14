import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage, MessageRole


class ChatMessageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        session_id: uuid.UUID,
        role: MessageRole,
        content: str,
    ) -> ChatMessage:
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def create_pair(
        self,
        *,
        session_id: uuid.UUID,
        user_content: str,
        assistant_content: str,
    ) -> tuple[ChatMessage, ChatMessage]:
        user_message = ChatMessage(
            session_id=session_id,
            role=MessageRole.user,
            content=user_content,
        )
        assistant_message = ChatMessage(
            session_id=session_id,
            role=MessageRole.assistant,
            content=assistant_content,
        )
        self.db.add_all([user_message, assistant_message])
        self.db.commit()
        self.db.refresh(user_message)
        self.db.refresh(assistant_message)
        return user_message, assistant_message

    def list_by_session(self, session_id: uuid.UUID) -> list[ChatMessage]:
        statement = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        return list(self.db.scalars(statement).all())
