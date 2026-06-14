import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.chat_session import ChatSession


class ChatSessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
        title: str,
    ) -> ChatSession:
        session = ChatSession(
            user_id=user_id,
            workspace_id=workspace_id,
            title=title,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_id(self, session_id: uuid.UUID) -> ChatSession | None:
        statement = select(ChatSession).where(ChatSession.id == session_id)
        return self.db.scalar(statement)

    def get_by_id_for_user(self, session_id: uuid.UUID, user_id: uuid.UUID) -> ChatSession | None:
        statement = select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
        )
        return self.db.scalar(statement)

    def get_by_id_for_user_with_messages(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ChatSession | None:
        statement = (
            select(ChatSession)
            .options(joinedload(ChatSession.messages))
            .where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
            )
        )
        return self.db.scalars(statement).unique().first()
