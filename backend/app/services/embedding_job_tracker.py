import uuid
from dataclasses import dataclass, field

from app.schemas.embedding import EmbeddingJobStatus


@dataclass
class EmbeddingJobTracker:
    """In-memory job tracker prepared for future queue workers."""

    _jobs: dict[str, EmbeddingJobStatus] = field(default_factory=dict)

    def set_status(self, job_key: str, status: EmbeddingJobStatus) -> None:
        self._jobs[job_key] = status

    def get_status(self, job_key: str) -> EmbeddingJobStatus | None:
        return self._jobs.get(job_key)

    def clear_status(self, job_key: str) -> None:
        self._jobs.pop(job_key, None)


embedding_job_tracker = EmbeddingJobTracker()
