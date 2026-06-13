from app.chunking.base import ChunkConfig, ChunkingStrategy


class FixedSizeChunking(ChunkingStrategy):
    def chunk(self, text: str, config: ChunkConfig) -> list[str]:
        if not text:
            return []

        chunk_size = config.chunk_size
        overlap = max(0, min(config.chunk_overlap, chunk_size - 1))
        chunks: list[str] = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + chunk_size, text_length)
            piece = text[start:end].strip()
            if piece:
                chunks.append(piece)

            if end >= text_length:
                break

            start = end - overlap if overlap else end

        return chunks


class RecursiveChunking(ChunkingStrategy):
    _SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def chunk(self, text: str, config: ChunkConfig) -> list[str]:
        if not text:
            return []

        pieces = self._split_text(text, config.chunk_size, self._SEPARATORS)
        return self._merge_with_overlap(pieces, config.chunk_size, config.chunk_overlap)

    def _split_text(self, text: str, chunk_size: int, separators: list[str]) -> list[str]:
        if len(text) <= chunk_size:
            stripped = text.strip()
            return [stripped] if stripped else []

        separator = separators[0]
        remaining_separators = separators[1:]
        if separator:
            splits = text.split(separator)
            chunks: list[str] = []
            current = ""
            for index, split in enumerate(splits):
                piece = split if index == len(splits) - 1 else split + separator
                candidate = f"{current}{piece}" if current else piece
                if len(candidate) <= chunk_size:
                    current = candidate
                    continue
                if current.strip():
                    chunks.append(current.strip())
                if len(piece) > chunk_size and remaining_separators:
                    chunks.extend(self._split_text(piece, chunk_size, remaining_separators))
                    current = ""
                else:
                    current = piece
            if current.strip():
                chunks.append(current.strip())
            return chunks

        return FixedSizeChunking().chunk(text, config)

    def _merge_with_overlap(self, pieces: list[str], chunk_size: int, overlap: int) -> list[str]:
        if not pieces:
            return []

        merged: list[str] = []
        current = pieces[0]
        for piece in pieces[1:]:
            candidate = f"{current}\n\n{piece}" if current else piece
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                merged.append(current)
                current = piece
        if current:
            merged.append(current)

        if overlap <= 0 or len(merged) <= 1:
            return merged

        overlapped: list[str] = [merged[0]]
        for index in range(1, len(merged)):
            previous_tail = merged[index - 1][-overlap:]
            overlapped.append(f"{previous_tail}{merged[index]}")
        return overlapped


class ParagraphChunking(ChunkingStrategy):
    def chunk(self, text: str, config: ChunkConfig) -> list[str]:
        paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
        if not paragraphs:
            return []

        chunks: list[str] = []
        current = ""
        for paragraph in paragraphs:
            candidate = f"{current}\n\n{paragraph}" if current else paragraph
            if len(candidate) <= config.chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                if len(paragraph) > config.chunk_size:
                    chunks.extend(FixedSizeChunking().chunk(paragraph, config))
                    current = ""
                else:
                    current = paragraph
        if current:
            chunks.append(current)
        return chunks
