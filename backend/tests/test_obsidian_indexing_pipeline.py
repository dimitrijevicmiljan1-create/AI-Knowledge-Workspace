"""Obsidian indexing pipeline unit tests."""

from uuid import uuid4

from app.obsidian.parser import ObsidianNoteParser
from app.obsidian.sync import ObsidianSyncStats
from app.services.retrieval_source_service import RETRIEVAL_SOURCE_TYPES
from app.models.source import SourceType


def test_obsidian_metadata_contains_required_fields() -> None:
    parsed = ObsidianNoteParser().parse(
        path="notes/project.md",
        content="# Project Alpha\n\nSecret project details.",
        vault_name="Research",
    )
    workspace_id = uuid4()
    vault_id = uuid4()
    metadata = ObsidianNoteParser().build_document_metadata(
        parsed,
        content_checksum="abc123",
        workspace_id=workspace_id,
        vault_id=vault_id,
    )

    assert metadata["source"] == "obsidian"
    assert metadata["workspace_id"] == str(workspace_id)
    assert metadata["vault_id"] == str(vault_id)
    assert metadata["path"] == "notes/project.md"
    assert metadata["title"] == "Project Alpha"


def test_retrieval_includes_obsidian_source_type() -> None:
    assert SourceType.obsidian in RETRIEVAL_SOURCE_TYPES


def test_sync_stats_defaults() -> None:
    stats = ObsidianSyncStats()
    assert stats.markdown_files_discovered == 0
    assert stats.chunks_created == 0
    assert stats.embeddings_stored == 0
