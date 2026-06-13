import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.search_history import SearchHistory


class SearchHistoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        user_id: uuid.UUID,
        workspace_id: uuid.UUID,
        query: str,
        result_count: int,
    ) -> SearchHistory:
        record = SearchHistory(
            user_id=user_id,
            workspace_id=workspace_id,
            query=query,
            result_count=result_count,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def count_by_user(self, user_id: uuid.UUID) -> int:
        statement = select(func.count()).select_from(SearchHistory).where(SearchHistory.user_id == user_id)
        return self.db.scalar(statement) or 0

    def average_results_by_user(self, user_id: uuid.UUID) -> float:
        statement = select(func.avg(SearchHistory.result_count)).where(SearchHistory.user_id == user_id)
        value = self.db.scalar(statement)
        return round(float(value or 0.0), 2)

    def most_active_workspace(self, user_id: uuid.UUID) -> uuid.UUID | None:
        statement = (
            select(SearchHistory.workspace_id, func.count().label("search_count"))
            .where(SearchHistory.user_id == user_id)
            .group_by(SearchHistory.workspace_id)
            .order_by(func.count().desc())
            .limit(1)
        )
        row = self.db.execute(statement).first()
        return row.workspace_id if row else None

    def recent_queries_count(self, user_id: uuid.UUID, *, days: int) -> int:
        cutoff = datetime.now(UTC) - timedelta(days=days)
        statement = (
            select(func.count())
            .select_from(SearchHistory)
            .where(SearchHistory.user_id == user_id, SearchHistory.created_at >= cutoff)
        )
        return self.db.scalar(statement) or 0

    def list_recent_by_user(self, user_id: uuid.UUID, *, limit: int = 10) -> list[SearchHistory]:
        statement = (
            select(SearchHistory)
            .where(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(statement).all())
