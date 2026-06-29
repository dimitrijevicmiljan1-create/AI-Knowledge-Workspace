"""Obsidian vault query intent tests."""

from app.obsidian.query_intent import is_vault_content_query


def test_is_vault_content_query_detects_common_phrases() -> None:
    assert is_vault_content_query("What is inside my Obsidian vault?")
    assert is_vault_content_query("Show me my vault contents")
    assert is_vault_content_query("What notes are in my vault?")


def test_is_vault_content_query_ignores_unrelated_questions() -> None:
    assert not is_vault_content_query("How does authentication work?")
    assert not is_vault_content_query("")
