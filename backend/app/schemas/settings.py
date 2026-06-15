from pydantic import BaseModel, Field


class UserSettingsResponse(BaseModel):
    default_model: str
    temperature: float
    response_length: str
    chunk_size: int
    chunk_overlap: int
    auto_index_uploads: bool

    model_config = {"from_attributes": True}


class UserSettingsUpdate(BaseModel):
    default_model: str | None = Field(default=None, max_length=128)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    response_length: str | None = Field(default=None, pattern="^(short|medium|long)$")
    chunk_size: int | None = Field(default=None, ge=128, le=4096)
    chunk_overlap: int | None = Field(default=None, ge=0, le=1024)
    auto_index_uploads: bool | None = None


class IntegrationStatusResponse(BaseModel):
    github_connected: bool
    github_username: str | None = None
    notion_connected: bool = False
    google_drive_connected: bool = False


class UsageStatsResponse(BaseModel):
    documents: int
    chunks: int
    storage_bytes: int
    queries: int
