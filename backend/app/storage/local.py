import re
import uuid
from pathlib import Path

from app.core.config import settings
from app.storage.base import StorageBackend, StoredFile

_SAFE_FILENAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


class LocalStorageBackend(StorageBackend):
    def __init__(self, base_path: str | None = None) -> None:
        self.base_path = Path(base_path or settings.storage_upload_path)

    def save(self, workspace_id: str, filename: str, content: bytes) -> StoredFile:
        safe_name = self._build_unique_filename(filename)
        relative_path = f"{workspace_id}/{safe_name}"
        absolute_path = self.base_path / relative_path
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        absolute_path.write_bytes(content)
        return StoredFile(path=relative_path, absolute_path=str(absolute_path))

    def delete(self, path: str) -> None:
        file_path = self._resolve_path(path)
        if file_path.exists():
            file_path.unlink()

    def exists(self, path: str) -> bool:
        return self._resolve_path(path).exists()

    def get_path(self, path: str) -> str:
        return str(self._resolve_path(path))

    def _resolve_path(self, path: str) -> Path:
        normalized = Path(path)
        if normalized.is_absolute():
            raise ValueError("Absolute storage paths are not allowed")

        resolved = (self.base_path / normalized).resolve()
        base_resolved = self.base_path.resolve()
        if not str(resolved).startswith(str(base_resolved)):
            raise ValueError("Path traversal detected")
        return resolved

    def _build_unique_filename(self, filename: str) -> str:
        basename = Path(filename).name
        if not basename or basename in {".", ".."}:
            raise ValueError("Invalid filename")

        stem = Path(basename).stem
        suffix = Path(basename).suffix.lower()
        sanitized_stem = _SAFE_FILENAME_PATTERN.sub("_", stem).strip("._") or "file"
        return f"{uuid.uuid4()}_{sanitized_stem}{suffix}"
