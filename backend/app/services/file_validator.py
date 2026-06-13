import mimetypes
from dataclasses import dataclass
from pathlib import Path

from app.core.config import settings

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
BLOCKED_EXTENSIONS = {
    ".exe",
    ".sh",
    ".bat",
    ".cmd",
    ".ps1",
    ".py",
    ".js",
    ".ts",
    ".rb",
    ".php",
    ".jar",
    ".dll",
    ".msi",
    ".app",
    ".dmg",
    ".deb",
    ".rpm",
    ".vbs",
    ".com",
    ".scr",
    ".html",
    ".htm",
    ".svg",
}
ALLOWED_MIME_TYPES = {
    ".txt": {"text/plain"},
    ".md": {"text/plain", "text/markdown", "text/x-markdown"},
    ".pdf": {"application/pdf"},
    ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
}


@dataclass
class FileValidationError:
    field: str
    message: str


@dataclass
class FileValidationResult:
    valid: bool
    errors: list[FileValidationError]
    extension: str = ""
    mime_type: str = "application/octet-stream"


def validate_upload_file(filename: str, content: bytes, content_type: str | None = None) -> FileValidationResult:
    errors: list[FileValidationError] = []
    safe_filename = _sanitize_filename(filename)

    if safe_filename is None:
        errors.append(FileValidationError(field="filename", message="Invalid or unsafe filename"))
        return FileValidationResult(valid=False, errors=errors)

    extension = Path(safe_filename).suffix.lower()
    if extension in BLOCKED_EXTENSIONS:
        errors.append(
            FileValidationError(
                field="filename",
                message=f"File type '{extension}' is not allowed for security reasons",
            )
        )

    if extension not in ALLOWED_EXTENSIONS:
        errors.append(
            FileValidationError(
                field="filename",
                message=f"Unsupported file type '{extension or 'unknown'}'. Allowed: .txt, .md, .pdf, .docx",
            )
        )

    if len(content) == 0:
        errors.append(FileValidationError(field="file", message="File cannot be empty"))

    if len(content) > settings.max_upload_size_bytes:
        max_mb = settings.max_upload_size_bytes // (1024 * 1024)
        errors.append(
            FileValidationError(
                field="file",
                message=f"File exceeds maximum size of {max_mb} MB",
            )
        )

    mime_type = _resolve_mime_type(safe_filename, content_type)
    allowed_mimes = ALLOWED_MIME_TYPES.get(extension, set())
    if extension in ALLOWED_EXTENSIONS and allowed_mimes and mime_type not in allowed_mimes:
        if mime_type != "application/octet-stream":
            errors.append(
                FileValidationError(
                    field="mime_type",
                    message=f"MIME type '{mime_type}' does not match extension '{extension}'",
                )
            )

    return FileValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        extension=extension,
        mime_type=mime_type,
    )


def _sanitize_filename(filename: str) -> str | None:
    if not filename or not filename.strip():
        return None

    basename = Path(filename).name
    if not basename or basename in {".", ".."}:
        return None

    if ".." in filename or "/" in filename or "\\" in filename:
        return None

    return basename


def _resolve_mime_type(filename: str, content_type: str | None) -> str:
    if content_type:
        return content_type.split(";")[0].strip().lower()

    guessed_type, _ = mimetypes.guess_type(filename)
    return guessed_type or "application/octet-stream"
