from uuid import UUID

from pydantic import BaseModel, Field

from app.chunking.base import ChunkStrategyName


class ChunkRequest(BaseModel):
    strategy: ChunkStrategyName = Field(
        default=ChunkStrategyName.recursive,
        examples=["recursive"],
    )
    chunk_size: int | None = Field(default=None, ge=100, le=10000, examples=[1000])
    chunk_overlap: int | None = Field(default=None, ge=0, le=5000, examples=[200])


class ChunkOperationResponse(BaseModel):
    document_id: UUID
    chunk_count: int
    strategy: ChunkStrategyName
    total_tokens: int


class ChunkStatsResponse(BaseModel):
    document_id: UUID
    total_chunks: int
    total_tokens: int
    avg_chunk_size: float


class ChunkPreviewResponse(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    token_count: int | None
