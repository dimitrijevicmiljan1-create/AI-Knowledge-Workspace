from app.db.base import Base
from app.db.database import engine
from app.models import (  # noqa: F401
    ChatMessage,
    ChatSession,
    Chunk,
    Document,
    Embedding,
    SearchHistory,
    Source,
    User,
    Workspace,
)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
