from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ObsidianVaultCreateRequest(BaseModel):
    workspace_id: UUID
    vault_name: str = Field(min_length=1, max_length=255)


class ObsidianVaultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    source_id: UUID
    vault_name: str
    last_synced_at: datetime | None
    sync_status: str
    created_at: datetime
    updated_at: datetime


class ObsidianVaultListResponse(BaseModel):
    items: list[ObsidianVaultResponse]
    total: int


class ObsidianVaultSyncResponse(BaseModel):
    job_id: UUID
    vault_id: UUID
    status: str


class ObsidianSyncJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    vault_id: UUID
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    files_scanned: int
    documents_created: int
    documents_updated: int
    documents_deleted: int
    error_message: str | None
    created_at: datetime


class ObsidianIndexStatsResponse(BaseModel):
    vault_id: UUID
    source_id: UUID
    workspace_id: UUID
    source_status: str
    markdown_files_discovered: int
    documents_indexed: int
    chunks_created: int
    embeddings_stored: int
    vector_chunks_for_source: int
    metadata_source: str = "obsidian"


class ObsidianVectorChunkSample(BaseModel):
    chunk_id: UUID
    document_id: UUID
    document_title: str
    document_path: str
    chunk_content: str
    metadata: dict = Field(default_factory=dict)
    source_type: str | None = None


class ObsidianVectorStoreDebugResponse(BaseModel):
    workspace_id: UUID
    metadata_source: str = "obsidian"
    total_documents: int
    total_chunks: int
    sample_chunks: list[ObsidianVectorChunkSample]
    indexed_paths: list[str] = Field(default_factory=list)
