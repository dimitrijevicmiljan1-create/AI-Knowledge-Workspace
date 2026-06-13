import hashlib


def compute_checksum(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def compute_bytes_checksum(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
