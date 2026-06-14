import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.github_connection import GitHubConnection


class GitHubConnectionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: uuid.UUID,
        github_user_id: int,
        github_username: str,
        access_token_encrypted: str,
        connected_at: datetime,
    ) -> GitHubConnection:
        connection = GitHubConnection(
            user_id=user_id,
            github_user_id=github_user_id,
            github_username=github_username,
            access_token_encrypted=access_token_encrypted,
            connected_at=connected_at,
        )
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        return connection

    def get_by_id(self, connection_id: uuid.UUID) -> GitHubConnection | None:
        return self.db.get(GitHubConnection, connection_id)

    def get_by_user_id(self, user_id: uuid.UUID) -> GitHubConnection | None:
        statement = select(GitHubConnection).where(GitHubConnection.user_id == user_id)
        return self.db.scalar(statement)

    def update(self, connection: GitHubConnection, **fields: object) -> GitHubConnection:
        for field, value in fields.items():
            if value is not None:
                setattr(connection, field, value)
        self.db.commit()
        self.db.refresh(connection)
        return connection

    def delete(self, connection: GitHubConnection) -> None:
        self.db.delete(connection)
        self.db.commit()
