from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.source import SourceStatus, SourceType


class SourceCreate(BaseModel):
    workspace_id: UUID = Field(examples=["3fa85f64-5717-4562-b3fc-2c963f66afa6"])
    name: str = Field(min_length=1, max_length=255, examples=["Engineering Docs"])
    source_type: SourceType
    config: dict[str, Any] = Field(default_factory=dict)


class SourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255, examples=["Updated Source"])
    config: dict[str, Any] | None = Field(default=None)


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    name: str
    source_type: SourceType
    config: dict[str, Any]
    status: SourceStatus
    last_sync_at: datetime | None
    created_at: datetime
    updated_at: datetime


class SourceListResponse(BaseModel):
    items: list[SourceResponse]
    total: int


class SourceValidationError(BaseModel):
    field: str
    message: str


class SourceValidationResult(BaseModel):
    valid: bool
    errors: list[SourceValidationError] = Field(default_factory=list)


class SourceStatsResponse(BaseModel):
    source_id: UUID
    document_count: int
    chunk_count: int
    last_sync_at: datetime | None
    status: SourceStatus
