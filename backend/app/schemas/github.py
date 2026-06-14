from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.github_repository import GitHubRepositorySyncStatus
from app.models.github_sync_job import GitHubSyncJobStatus


class GitHubConnectResponse(BaseModel):
    authorization_url: str = Field(
        examples=["https://github.com/login/oauth/authorize?client_id=...&state=..."]
    )


class GitHubOAuthCallbackResponse(BaseModel):
    success: bool
    github_username: str
    connected_at: datetime


class GitHubConnectionResponse(BaseModel):
    github_username: str
    connected_at: datetime


class GitHubDiscoveredRepository(BaseModel):
    github_repo_id: int
    owner: str
    name: str
    full_name: str
    default_branch: str
    visibility: str
    description: str | None = None
    updated_at: str
    private: bool


class GitHubRepositoryDiscoveryResponse(BaseModel):
    items: list[GitHubDiscoveredRepository]
    page: int
    per_page: int
    total: int


class GitHubRepositoryAddRequest(BaseModel):
    workspace_id: UUID
    github_repo_id: int
    owner: str = Field(min_length=1)
    name: str = Field(min_length=1)


class GitHubRepositoryResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    source_id: UUID
    github_repo_id: int
    repository_owner: str
    repository_name: str
    default_branch: str
    last_commit_sha: str | None = None
    last_synced_at: datetime | None = None
    sync_status: GitHubRepositorySyncStatus
    created_at: datetime
    updated_at: datetime


class GitHubRepositorySyncResponse(BaseModel):
    job_id: UUID
    repository_id: UUID
    status: GitHubSyncJobStatus


class GitHubSyncJobResponse(BaseModel):
    id: UUID
    repository_id: UUID
    status: GitHubSyncJobStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    files_scanned: int
    documents_created: int
    documents_updated: int
    documents_deleted: int
    error_message: str | None = None
    created_at: datetime
