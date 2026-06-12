from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255, examples=["Research Hub"])
    description: str | None = Field(default=None, examples=["Primary workspace for AI research documents"])


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255, examples=["Updated Workspace"])
    description: str | None = Field(default=None, examples=["Updated description"])


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    owner_id: UUID
    created_at: datetime
    updated_at: datetime


class WorkspaceListResponse(BaseModel):
    items: list[WorkspaceResponse]
    total: int


class WorkspaceStatsResponse(BaseModel):
    workspace_id: UUID
    document_count: int
    source_count: int
    chat_count: int
    created_at: datetime
