from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, examples=["How do I configure authentication?"])
    top_k: int = Field(default=5, ge=1, le=50, examples=[5])
    source_id: UUID | None = Field(default=None, examples=["3fa85f64-5717-4562-b3fc-2c963f66afa7"])
    document_id: UUID | None = Field(default=None, examples=["3fa85f64-5717-4562-b3fc-2c963f66afa8"])
    date_from: datetime | None = Field(default=None, examples=["2026-01-01T00:00:00Z"])
    date_to: datetime | None = Field(default=None, examples=["2026-12-31T23:59:59Z"])


class SearchResult(BaseModel):
    chunk_id: UUID
    document_id: UUID
    document_title: str
    document_path: str
    chunk_content: str
    similarity_score: float = Field(ge=0.0, le=1.0)
    source_id: UUID
    workspace_id: UUID
    repository_name: str | None = None
    file_path: str | None = None


class SearchResponse(BaseModel):
    query: str
    top_k: int
    total_results: int
    results: list[SearchResult]
    search_id: UUID | None = None


class SearchStatsResponse(BaseModel):
    total_searches: int = Field(examples=[42])
    avg_results: float = Field(examples=[4.5])
    most_active_workspace: UUID | None = Field(examples=["3fa85f64-5717-4562-b3fc-2c963f66afa7"])
    recent_queries_count: int = Field(examples=[12])
