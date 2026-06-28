from dataclasses import dataclass
from uuid import UUID


@dataclass
class SearchHit:
    chunk_id: UUID
    document_id: UUID
    document_title: str
    document_path: str
    chunk_content: str
    similarity_score: float
    source_id: UUID
    workspace_id: UUID
    source_type: str | None = None
    repository_name: str | None = None
    file_path: str | None = None
    vault_name: str | None = None


def normalize_scores(hits: list[SearchHit]) -> list[SearchHit]:
    if not hits:
        return hits

    scores = [hit.similarity_score for hit in hits]
    min_score = min(scores)
    max_score = max(scores)
    if max_score == min_score:
        return [
            SearchHit(
                chunk_id=hit.chunk_id,
                document_id=hit.document_id,
                document_title=hit.document_title,
                document_path=hit.document_path,
                chunk_content=hit.chunk_content,
                similarity_score=1.0,
                source_id=hit.source_id,
                workspace_id=hit.workspace_id,
                source_type=hit.source_type,
                repository_name=hit.repository_name,
                file_path=hit.file_path,
                vault_name=hit.vault_name,
            )
            for hit in hits
        ]

    normalized: list[SearchHit] = []
    for hit in hits:
        normalized_score = (hit.similarity_score - min_score) / (max_score - min_score)
        normalized.append(
            SearchHit(
                chunk_id=hit.chunk_id,
                document_id=hit.document_id,
                document_title=hit.document_title,
                document_path=hit.document_path,
                chunk_content=hit.chunk_content,
                similarity_score=round(normalized_score, 6),
                source_id=hit.source_id,
                workspace_id=hit.workspace_id,
                source_type=hit.source_type,
                repository_name=hit.repository_name,
                file_path=hit.file_path,
                vault_name=hit.vault_name,
            )
        )
    return normalized


def rank_hits(hits: list[SearchHit], *, normalize: bool = True) -> list[SearchHit]:
    """Sort by relevance and optionally normalize scores for display."""
    ranked = sorted(hits, key=lambda hit: hit.similarity_score, reverse=True)
    if normalize:
        return normalize_scores(ranked)
    return ranked


def prepare_for_reranking(hits: list[SearchHit]) -> list[SearchHit]:
    """Return ranked hits prepared for a future cross-encoder reranking stage."""
    return rank_hits(hits, normalize=False)
