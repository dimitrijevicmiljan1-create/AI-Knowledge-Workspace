from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EmbeddingJobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class EmbedDocumentResponse(BaseModel):
    document_id: UUID
    status: EmbeddingJobStatus
    chunks_total: int
    chunks_embedded: int
    chunks_skipped: int
    chunks_failed: int
    estimated_tokens: int
    estimated_cost: float
    embedding_model: str


class EmbedWorkspaceResponse(BaseModel):
    workspace_id: UUID
    status: EmbeddingJobStatus
    documents_total: int
    documents_embedded: int
    chunks_total: int
    chunks_embedded: int
    chunks_skipped: int
    chunks_failed: int
    estimated_tokens: int
    estimated_cost: float
    embedding_model: str


class ReembedDocumentResponse(BaseModel):
    document_id: UUID
    status: EmbeddingJobStatus
    chunks_total: int
    chunks_embedded: int
    chunks_failed: int
    estimated_tokens: int
    estimated_cost: float
    embedding_model: str


class DeleteEmbeddingsResponse(BaseModel):
    document_id: UUID
    embeddings_deleted: int


class EmbeddingPreviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    chunk_id: UUID
    dimension: int
    created_at: datetime


class EmbeddingStatsResponse(BaseModel):
    total_embeddings: int = Field(examples=[128])
    total_chunks_embedded: int = Field(examples=[128])
    estimated_cost: float = Field(examples=[0.0024])
    last_embedding_time: datetime | None = Field(examples=["2026-06-13T12:00:00Z"])
