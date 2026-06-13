import re
from typing import Any
from urllib.parse import urlparse

from app.models.source import SourceType
from app.schemas.source import SourceValidationError, SourceValidationResult

_GITHUB_URL_PATTERN = re.compile(
    r"^https?://(www\.)?github\.com/[\w.-]+/[\w.-]+/?$",
    re.IGNORECASE,
)


def validate_source_config(source_type: SourceType, config: dict[str, Any]) -> SourceValidationResult:
    errors: list[SourceValidationError] = []

    if source_type == SourceType.github:
        repository_url = config.get("repository_url", "")
        if not isinstance(repository_url, str) or not repository_url.strip():
            errors.append(
                SourceValidationError(
                    field="config.repository_url",
                    message="GitHub repository URL is required",
                )
            )
        elif not _is_valid_github_url(repository_url.strip()):
            errors.append(
                SourceValidationError(
                    field="config.repository_url",
                    message="Must be a valid GitHub repository URL",
                )
            )

        branch = config.get("branch", "main")
        if branch is not None and not isinstance(branch, str):
            errors.append(
                SourceValidationError(
                    field="config.branch",
                    message="Branch must be a string",
                )
            )

    elif source_type == SourceType.obsidian:
        vault_name = config.get("vault_name", "")
        if not isinstance(vault_name, str) or not vault_name.strip():
            errors.append(
                SourceValidationError(
                    field="config.vault_name",
                    message="Obsidian vault name is required",
                )
            )

        vault_path = config.get("vault_path", "")
        if vault_path is not None and not isinstance(vault_path, str):
            errors.append(
                SourceValidationError(
                    field="config.vault_path",
                    message="Vault path must be a string",
                )
            )

    elif source_type == SourceType.local_files:
        directory_path = config.get("directory_path", "")
        if not isinstance(directory_path, str) or not directory_path.strip():
            errors.append(
                SourceValidationError(
                    field="config.directory_path",
                    message="Directory path is required",
                )
            )

    elif source_type == SourceType.manual:
        description = config.get("description", "")
        if description is not None and not isinstance(description, str):
            errors.append(
                SourceValidationError(
                    field="config.description",
                    message="Description must be a string",
                )
            )

    return SourceValidationResult(valid=len(errors) == 0, errors=errors)


def _is_valid_github_url(url: str) -> bool:
    if _GITHUB_URL_PATTERN.match(url):
        return True

    parsed = urlparse(url)
    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        return False

    path_parts = [part for part in parsed.path.split("/") if part]
    return len(path_parts) >= 2
