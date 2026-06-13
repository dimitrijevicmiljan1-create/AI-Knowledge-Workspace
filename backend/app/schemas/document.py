from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IngestionStatus(str, Enum):
    created = "created"
    updated = "updated"
    unchanged = "unchanged"


class DocumentIngestRequest(BaseModel):
    source_id: UUID = Field(examples=["3fa85f64-5717-4562-b3fc-2c963f66afa7"])
    title: str = Field(min_length=1, max_length=512, examples=["Getting Started Guide"])
    path: str = Field(min_length=1, max_length=1024, examples=["docs/getting-started.md"])
    content: str = Field(min_length=1, examples=["# Getting Started\n\nWelcome to the knowledge workspace."])
    metadata: dict[str, Any] = Field(default_factory=dict, examples=[{"format": "markdown"}])


class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=512)
    metadata: dict[str, Any] | None = Field(default=None)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    source_id: UUID
    title: str
    path: str
    checksum: str
    metadata: dict[str, Any] = Field(validation_alias="document_metadata")
    indexed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int


class ChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    token_count: int | None
    embedding_model: str | None
    created_at: datetime


class ChunkListResponse(BaseModel):
    items: list[ChunkResponse]
    total: int


class DocumentIngestResponse(BaseModel):
    document: DocumentResponse
    chunk_count: int
    ingestion_status: IngestionStatus


class DocumentStatsResponse(BaseModel):
    document_id: UUID
    chunk_count: int
    indexed_at: datetime | None
    checksum: str
