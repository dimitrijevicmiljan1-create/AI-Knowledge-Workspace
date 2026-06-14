from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class ParsedRepositoryFile:
    path: str
    title: str
    file_name: str
    file_extension: str
    content: str
    blob_sha: str
    commit_sha: str
    repository_owner: str
    repository_name: str


class RepositoryFileParser:
    """Convert repository files into document-ready structures."""

    def parse(
        self,
        *,
        path: str,
        content: str,
        blob_sha: str,
        commit_sha: str,
        repository_owner: str,
        repository_name: str,
    ) -> ParsedRepositoryFile:
        posix_path = PurePosixPath(path)
        file_name = posix_path.name
        file_extension = posix_path.suffix.lower().lstrip(".")
        title = self._build_title(file_name, content)

        return ParsedRepositoryFile(
            path=path,
            title=title,
            file_name=file_name,
            file_extension=file_extension,
            content=content,
            blob_sha=blob_sha,
            commit_sha=commit_sha,
            repository_owner=repository_owner,
            repository_name=repository_name,
        )

    def build_document_metadata(self, parsed: ParsedRepositoryFile) -> dict:
        return {
            "source_type": "github",
            "repository_name": parsed.repository_name,
            "repository_owner": parsed.repository_owner,
            "relative_path": parsed.path,
            "file_name": parsed.file_name,
            "file_extension": parsed.file_extension,
            "last_commit_sha": parsed.commit_sha,
            "blob_sha": parsed.blob_sha,
            "format": parsed.file_extension or "text",
        }

    def _build_title(self, file_name: str, content: str) -> str:
        if file_name.lower().startswith("readme"):
            for line in content.splitlines():
                stripped = line.strip()
                if stripped.startswith("#"):
                    return stripped.lstrip("#").strip() or file_name
        return file_name
