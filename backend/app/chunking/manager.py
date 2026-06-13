from app.chunking.base import ChunkConfig, ChunkStrategyName, ChunkingStrategy
from app.chunking.strategies import FixedSizeChunking, ParagraphChunking, RecursiveChunking


class ChunkingManager:
    def __init__(self) -> None:
        self._strategies: dict[ChunkStrategyName, ChunkingStrategy] = {
            ChunkStrategyName.fixed: FixedSizeChunking(),
            ChunkStrategyName.recursive: RecursiveChunking(),
            ChunkStrategyName.paragraph: ParagraphChunking(),
        }

    def chunk(self, text: str, config: ChunkConfig) -> list[str]:
        strategy = self._strategies.get(config.strategy)
        if strategy is None:
            raise ValueError(f"Unsupported chunking strategy: {config.strategy}")
        return strategy.chunk(text, config)

    def get_strategy(self, name: ChunkStrategyName) -> ChunkingStrategy:
        strategy = self._strategies.get(name)
        if strategy is None:
            raise ValueError(f"Unsupported chunking strategy: {name}")
        return strategy
