"""Typed source configuration schemas for sync workers and validation."""

from pydantic import BaseModel, Field


class GitHubSourceConfig(BaseModel):
    repository_url: str = Field(examples=["https://github.com/owner/repo"])
    branch: str = Field(default="main", examples=["main"])


class ObsidianSourceConfig(BaseModel):
    vault_name: str = Field(examples=["My Vault"])
    vault_path: str = Field(default="", examples=["/path/to/vault"])


class LocalFilesSourceConfig(BaseModel):
    directory_path: str = Field(examples=["/data/documents"])


class ManualSourceConfig(BaseModel):
    description: str = Field(default="", examples=["Curated notes and references"])
