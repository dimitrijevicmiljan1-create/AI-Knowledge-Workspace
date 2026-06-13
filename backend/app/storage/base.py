from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class StoredFile:
    path: str
    absolute_path: str


class StorageBackend(ABC):
    @abstractmethod
    def save(self, workspace_id: str, filename: str, content: bytes) -> StoredFile:
        raise NotImplementedError

    @abstractmethod
    def delete(self, path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, path: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_path(self, path: str) -> str:
        raise NotImplementedError
