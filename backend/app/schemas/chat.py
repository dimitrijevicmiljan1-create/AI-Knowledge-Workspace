from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, examples=["How do I configure JWT authentication?"])
    top_k: int = Field(default=5, ge=1, le=50, examples=[5])


class Citation(BaseModel):
    chunk_id: UUID
    document_id: UUID
    source_id: UUID
    document_title: str


class RetrievedChunk(BaseModel):
    chunk_id: UUID
    document_id: UUID
    source_id: UUID
    document_title: str
    content: str
    similarity_score: float = Field(ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    answer: str = Field(examples=["JWT authentication is configured using a secret key..."])
    citations: list[Citation]
    retrieved_chunks: list[RetrievedChunk]
    processing_time: float = Field(examples=[1.234])
    exchange_id: UUID | None = None
