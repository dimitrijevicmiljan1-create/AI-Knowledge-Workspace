def estimate_token_count(text: str) -> int:
    return max(1, len(text.split()))


def chunk_text(
    text: str,
    *,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
) -> list[str]:
    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    overlap = max(0, min(chunk_overlap, chunk_size - 1))
    chunks: list[str] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap if overlap else end

    return chunks
