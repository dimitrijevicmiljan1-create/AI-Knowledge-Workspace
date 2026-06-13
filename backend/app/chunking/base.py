from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class ChunkStrategyName(str, Enum):
    fixed = "fixed"
    recursive = "recursive"
    paragraph = "paragraph"


@dataclass
class ChunkConfig:
    chunk_size: int = 1000
    chunk_overlap: int = 200
    strategy: ChunkStrategyName = ChunkStrategyName.recursive


class ChunkingStrategy(ABC):
    @abstractmethod
    def chunk(self, text: str, config: ChunkConfig) -> list[str]:
        raise NotImplementedError
