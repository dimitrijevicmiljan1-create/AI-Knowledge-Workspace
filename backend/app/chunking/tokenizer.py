def estimate_token_count(text: str) -> int:
    if not text or not text.strip():
        return 0
    return max(1, len(text.split()))


def estimate_total_tokens(chunks: list[str]) -> int:
    return sum(estimate_token_count(chunk) for chunk in chunks)
