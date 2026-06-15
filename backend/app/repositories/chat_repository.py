import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.chat import Chat


class ChatRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
        title: str,
    ) -> Chat:
        chat = Chat(
            user_id=user_id,
            workspace_id=workspace_id,
            title=title,
        )
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def get_by_id(self, chat_id: uuid.UUID) -> Chat | None:
        statement = select(Chat).where(Chat.id == chat_id)
        return self.db.scalar(statement)

    def get_by_id_for_user(self, chat_id: uuid.UUID, user_id: uuid.UUID) -> Chat | None:
        statement = select(Chat).where(
            Chat.id == chat_id,
            Chat.user_id == user_id,
        )
        return self.db.scalar(statement)

    def get_by_id_for_user_with_messages(
        self,
        chat_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Chat | None:
        statement = (
            select(Chat)
            .options(joinedload(Chat.messages))
            .where(
                Chat.id == chat_id,
                Chat.user_id == user_id,
            )
        )
        return self.db.scalars(statement).unique().first()

    def list_by_workspace_for_user(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> list[Chat]:
        statement = (
            select(Chat)
            .where(
                Chat.workspace_id == workspace_id,
                Chat.user_id == user_id,
            )
            .order_by(Chat.updated_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def update(self, chat: Chat, **fields: object) -> Chat:
        for field, value in fields.items():
            if value is not None:
                setattr(chat, field, value)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def delete(self, chat: Chat) -> None:
        self.db.delete(chat)
        self.db.commit()


# Backward-compatible alias.
ChatSessionRepository = ChatRepository
