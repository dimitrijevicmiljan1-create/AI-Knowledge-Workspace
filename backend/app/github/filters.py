import fnmatch
from pathlib import PurePosixPath

SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".md",
        ".txt",
        ".rst",
        ".adoc",
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".go",
        ".rs",
        ".cpp",
        ".c",
        ".cs",
        ".php",
        ".rb",
        ".yml",
        ".yaml",
        ".json",
    }
)

IGNORED_DIRECTORY_NAMES: frozenset[str] = frozenset(
    {
        "node_modules",
        "dist",
        "build",
        "target",
        "vendor",
        ".git",
        "coverage",
    }
)

IGNORED_FILE_PATTERNS: tuple[str, ...] = (
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.pdf",
    "*.zip",
)


def should_index_file(path: str) -> bool:
    """Return True when a repository file should be indexed as a document."""
    normalized = path.strip("/")
    if not normalized:
        return False

    posix_path = PurePosixPath(normalized)
    if any(part in IGNORED_DIRECTORY_NAMES for part in posix_path.parts):
        return False

    extension = posix_path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        return False

    filename = posix_path.name
    for pattern in IGNORED_FILE_PATTERNS:
        if fnmatch.fnmatch(filename.lower(), pattern):
            return False

    return True
