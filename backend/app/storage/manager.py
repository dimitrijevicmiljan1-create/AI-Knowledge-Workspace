from functools import lru_cache

from app.storage.base import StorageBackend
from app.storage.local import LocalStorageBackend


class StorageManager:
    def __init__(self, backend: StorageBackend | None = None) -> None:
        self.backend = backend or LocalStorageBackend()

    def save(self, workspace_id: str, filename: str, content: bytes):
        return self.backend.save(workspace_id, filename, content)

    def delete(self, path: str) -> None:
        self.backend.delete(path)

    def exists(self, path: str) -> bool:
        return self.backend.exists(path)

    def get_path(self, path: str) -> str:
        return self.backend.get_path(path)


@lru_cache
def get_storage_manager() -> StorageManager:
    return StorageManager()
