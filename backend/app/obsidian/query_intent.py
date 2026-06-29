"""Detect when a user question is about their Obsidian vault contents."""

VAULT_CONTENT_PHRASES: tuple[str, ...] = (
    "obsidian vault",
    "my vault",
    "inside my vault",
    "what is inside my",
    "what's in my vault",
    "whats in my vault",
    "notes in my vault",
    "vault contain",
    "vault contents",
)


def is_vault_content_query(query: str) -> bool:
    normalized = query.strip().lower()
    if not normalized:
        return False
    return any(phrase in normalized for phrase in VAULT_CONTENT_PHRASES)
