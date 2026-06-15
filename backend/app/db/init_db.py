from app.db.base import Base
from app.db.database import engine
from app.models import (  # noqa: F401
    Chat,
    ChatMessage,
    ChatExchange,
    Chunk,
    Document,
    Embedding,
    SearchHistory,
    Source,
    User,
    UserSettings,
    Workspace,
)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
