import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        source_id: uuid.UUID,
        title: str,
        path: str,
        checksum: str,
        metadata: dict,
        indexed_at: object = None,
    ) -> Document:
        document = Document(
            source_id=source_id,
            title=title,
            path=path,
            checksum=checksum,
            document_metadata=metadata,
            indexed_at=indexed_at,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        return self.db.get(Document, document_id)

    def get_by_source_and_path(self, source_id: uuid.UUID, path: str) -> Document | None:
        statement = select(Document).where(
            Document.source_id == source_id,
            Document.path == path,
        )
        return self.db.scalar(statement)

    def list_by_source(self, source_id: uuid.UUID) -> list[Document]:
        statement = (
            select(Document)
            .where(Document.source_id == source_id)
            .order_by(Document.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def update(self, document: Document, **fields: object) -> Document:
        for field, value in fields.items():
            if value is not None:
                setattr(document, field, value)
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete(self, document: Document) -> None:
        self.db.delete(document)
        self.db.commit()

    def exists(self, document_id: uuid.UUID) -> bool:
        statement = select(Document.id).where(Document.id == document_id)
        return self.db.scalar(statement) is not None

    def count_by_source(self, source_id: uuid.UUID) -> int:
        statement = select(func.count()).select_from(Document).where(Document.source_id == source_id)
        return self.db.scalar(statement) or 0
