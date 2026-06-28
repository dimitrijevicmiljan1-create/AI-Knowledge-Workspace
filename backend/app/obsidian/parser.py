from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class ParsedObsidianNote:
    path: str
    title: str
    file_name: str
    content: str
    vault_name: str


class ObsidianNoteParser:
    """Convert Obsidian markdown notes into document-ready structures."""

    def parse(
        self,
        *,
        path: str,
        content: str,
        vault_name: str,
    ) -> ParsedObsidianNote:
        normalized_path = path.replace("\\", "/").strip("/")
        file_name = PurePosixPath(normalized_path).name
        title = self._build_title(file_name, content)

        return ParsedObsidianNote(
            path=normalized_path,
            title=title,
            file_name=file_name,
            content=content,
            vault_name=vault_name,
        )

    def build_document_metadata(self, parsed: ParsedObsidianNote, *, content_checksum: str) -> dict:
        return {
            "source_type": "obsidian",
            "vault_name": parsed.vault_name,
            "relative_path": parsed.path,
            "file_name": parsed.file_name,
            "file_extension": "md",
            "content_checksum": content_checksum,
            "format": "markdown",
        }

    def _build_title(self, file_name: str, content: str) -> str:
        stem = PurePosixPath(file_name).stem
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                heading = stripped.lstrip("#").strip()
                if heading:
                    return heading
        return stem or file_name
