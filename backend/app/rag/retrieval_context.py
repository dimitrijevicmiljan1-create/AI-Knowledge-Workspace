from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True)
class ContextChunk:
    chunk_id: UUID
    document_id: UUID
    source_id: UUID
    document_title: str
    content: str
    similarity_score: float
    file_path: str | None = None
    repository_name: str | None = None


@dataclass
class RetrievalContext:
    chunks: list[ContextChunk] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return len(self.chunks) == 0
