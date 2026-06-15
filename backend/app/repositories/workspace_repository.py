import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.chat import Chat
from app.models.document import Document
from app.models.source import Source
from app.models.workspace import Workspace


class WorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        name: str,
        owner_id: uuid.UUID,
        description: str | None = None,
    ) -> Workspace:
        workspace = Workspace(
            name=name,
            description=description,
            owner_id=owner_id,
        )
        self.db.add(workspace)
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def get_by_id(self, workspace_id: uuid.UUID) -> Workspace | None:
        return self.db.get(Workspace, workspace_id)

    def get_all_by_owner(self, owner_id: uuid.UUID) -> list[Workspace]:
        statement = (
            select(Workspace)
            .where(Workspace.owner_id == owner_id)
            .order_by(Workspace.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def update(self, workspace: Workspace, **fields: object) -> Workspace:
        for field, value in fields.items():
            if value is not None:
                setattr(workspace, field, value)
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def delete(self, workspace: Workspace) -> None:
        self.db.delete(workspace)
        self.db.commit()

    def exists(self, workspace_id: uuid.UUID) -> bool:
        statement = select(Workspace.id).where(Workspace.id == workspace_id)
        return self.db.scalar(statement) is not None

    def count_sources(self, workspace_id: uuid.UUID) -> int:
        statement = select(func.count()).select_from(Source).where(Source.workspace_id == workspace_id)
        return self.db.scalar(statement) or 0

    def count_documents(self, workspace_id: uuid.UUID) -> int:
        statement = (
            select(func.count())
            .select_from(Document)
            .join(Source, Document.source_id == Source.id)
            .where(Source.workspace_id == workspace_id)
        )
        return self.db.scalar(statement) or 0

    def get_primary_by_owner(self, owner_id: uuid.UUID) -> Workspace | None:
        statement = (
            select(Workspace)
            .where(Workspace.owner_id == owner_id)
            .order_by(Workspace.created_at.asc())
        )
        return self.db.scalars(statement).first()

    def count_chats(self, workspace_id: uuid.UUID) -> int:
        statement = (
            select(func.count())
            .select_from(Chat)
            .where(Chat.workspace_id == workspace_id)
        )
        return self.db.scalar(statement) or 0

    def count_chat_sessions(self, workspace_id: uuid.UUID) -> int:
        return self.count_chats(workspace_id)
