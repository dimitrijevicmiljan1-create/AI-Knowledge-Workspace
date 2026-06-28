from pathlib import PurePosixPath

SKIP_DIRECTORY_NAMES = {
    ".obsidian",
    ".git",
    ".trash",
    "node_modules",
    "__pycache__",
}

SKIP_FILE_PREFIXES = (".",)


def should_index_obsidian_path(path: str) -> bool:
    normalized = path.replace("\\", "/").strip("/")
    if not normalized:
        return False

    parts = PurePosixPath(normalized).parts
    for part in parts:
        if part in SKIP_DIRECTORY_NAMES:
            return False
        if part.startswith(SKIP_FILE_PREFIXES) and part not in {".", ".."}:
            return False

    return PurePosixPath(normalized).suffix.lower() == ".md"
