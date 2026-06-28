from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=255, examples=["Research notes"])


class ChatCreateResponse(BaseModel):
    id: UUID


class ChatSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class ChatListResponse(BaseModel):
    items: list[ChatSummaryResponse]
    total: int


class ChatUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    created_at: datetime


class ChatMessageListResponse(BaseModel):
    items: list[ChatMessageResponse]
    total: int


# Legacy session schemas kept for backward compatibility.
class ChatSessionCreateRequest(BaseModel):
    workspace_id: UUID
    title: str | None = Field(default=None, max_length=255, examples=["JWT authentication questions"])


class ChatSessionCreateResponse(BaseModel):
    session_id: UUID


class ChatSessionResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    title: str

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, examples=["How do I configure JWT authentication?"])
    top_k: int = Field(default=5, ge=1, le=50, examples=[5])


class SessionMessageRequest(BaseModel):
    message: str = Field(min_length=1, examples=["How is JWT configured?"])
    top_k: int = Field(default=5, ge=1, le=50, examples=[5])


class SessionMessageResponse(BaseModel):
    answer: str
    citations: list["Citation"]


class Citation(BaseModel):
    chunk_id: UUID
    document_id: UUID
    source_id: UUID
    document_title: str
    file_path: str | None = None
    repository_name: str | None = None
    vault_name: str | None = None
    source_type: str | None = None


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
