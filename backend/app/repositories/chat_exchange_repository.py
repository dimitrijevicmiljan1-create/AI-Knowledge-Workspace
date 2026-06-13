import uuid

from sqlalchemy.orm import Session

from app.models.chat_exchange import ChatExchange


class ChatExchangeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
        question: str,
        answer: str,
        source_id: uuid.UUID | None = None,
        document_id: uuid.UUID | None = None,
    ) -> ChatExchange:
        exchange = ChatExchange(
            user_id=user_id,
            workspace_id=workspace_id,
            source_id=source_id,
            document_id=document_id,
            question=question,
            answer=answer,
        )
        self.db.add(exchange)
        self.db.commit()
        self.db.refresh(exchange)
        return exchange
