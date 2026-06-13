from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class SearchFilters:
    workspace_id: UUID | None = None
    source_id: UUID | None = None
    document_id: UUID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None

    def apply_workspace(self, workspace_id: UUID) -> "SearchFilters":
        return SearchFilters(
            workspace_id=workspace_id,
            source_id=self.source_id,
            document_id=self.document_id,
            date_from=self.date_from,
            date_to=self.date_to,
        )

    def apply_source(self, source_id: UUID) -> "SearchFilters":
        return SearchFilters(
            workspace_id=self.workspace_id,
            source_id=source_id,
            document_id=self.document_id,
            date_from=self.date_from,
            date_to=self.date_to,
        )

    def apply_document(self, document_id: UUID) -> "SearchFilters":
        return SearchFilters(
            workspace_id=self.workspace_id,
            source_id=self.source_id,
            document_id=document_id,
            date_from=self.date_from,
            date_to=self.date_to,
        )
