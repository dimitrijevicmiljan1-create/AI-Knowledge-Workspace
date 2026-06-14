import base64
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.github.exceptions import GitHubAPIError, GitHubAuthError, GitHubNotFoundError, GitHubRateLimitError

GITHUB_API_BASE = "https://api.github.com"
GITHUB_OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_OAUTH_TOKEN_URL = "https://github.com/login/oauth/access_token"
DEFAULT_PER_PAGE = 100
MAX_RETRIES = 5


@dataclass(frozen=True)
class GitHubRepositoryInfo:
    id: int
    owner: str
    name: str
    full_name: str
    default_branch: str
    visibility: str
    description: str | None
    updated_at: str
    private: bool


@dataclass(frozen=True)
class GitHubTreeEntry:
    path: str
    sha: str
    type: str
    size: int | None = None


@dataclass(frozen=True)
class GitHubFileContent:
    path: str
    content: str
    sha: str
    size: int


class GitHubClient:
    """Production GitHub REST API client with rate-limit handling."""

    def __init__(self, access_token: str, *, timeout: float = 30.0) -> None:
        self._access_token = access_token
        self._timeout = timeout

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def list_repositories(
        self,
        *,
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> list[GitHubRepositoryInfo]:
        params = {
            "affiliation": "owner,collaborator,organization_member",
            "sort": "updated",
            "direction": "desc",
            "page": page,
            "per_page": per_page,
        }
        payload = self._request("GET", "/user/repos", params=params)
        return [self._parse_repository(item) for item in payload]

    def get_repository(self, owner: str, name: str) -> GitHubRepositoryInfo:
        payload = self._request("GET", f"/repos/{owner}/{name}")
        return self._parse_repository(payload)

    def get_branch_commit_sha(self, owner: str, name: str, branch: str) -> str:
        payload = self._request("GET", f"/repos/{owner}/{name}/commits/{branch}")
        return payload["sha"]

    def get_recursive_tree(self, owner: str, name: str, tree_sha: str) -> list[GitHubTreeEntry]:
        payload = self._request(
            "GET",
            f"/repos/{owner}/{name}/git/trees/{tree_sha}",
            params={"recursive": "1"},
        )
        entries: list[GitHubTreeEntry] = []
        for item in payload.get("tree", []):
            if item.get("type") != "blob":
                continue
            entries.append(
                GitHubTreeEntry(
                    path=item["path"],
                    sha=item["sha"],
                    type=item["type"],
                    size=item.get("size"),
                )
            )
        return entries

    def get_file_content(self, owner: str, name: str, path: str, *, ref: str) -> GitHubFileContent:
        payload = self._request(
            "GET",
            f"/repos/{owner}/{name}/contents/{path}",
            params={"ref": ref},
        )
        if isinstance(payload, list):
            raise GitHubAPIError(f"Expected file but directory was returned for {path}")

        encoding = payload.get("encoding")
        raw_content = payload.get("content", "")
        if encoding == "base64":
            decoded = base64.b64decode(raw_content).decode("utf-8", errors="replace")
        else:
            decoded = raw_content

        return GitHubFileContent(
            path=path,
            content=decoded,
            sha=payload["sha"],
            size=payload.get("size", len(decoded.encode("utf-8"))),
        )

    def get_authenticated_user(self) -> dict[str, Any]:
        return self._request("GET", "/user")

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{GITHUB_API_BASE}{path}"
        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES):
            try:
                with httpx.Client(timeout=self._timeout) as client:
                    response = client.request(
                        method,
                        url,
                        headers=self.headers,
                        params=params,
                        json=json,
                    )

                if response.status_code == 401:
                    raise GitHubAuthError("GitHub authentication failed")
                if response.status_code == 404:
                    raise GitHubNotFoundError(f"GitHub resource not found: {path}")
                if response.status_code in {403, 429}:
                    retry_after = self._parse_retry_after(response)
                    if attempt < MAX_RETRIES - 1:
                        sleep_seconds = retry_after or min(2**attempt, 60)
                        time.sleep(sleep_seconds)
                        continue
                    raise GitHubRateLimitError(
                        "GitHub API rate limit exceeded",
                        retry_after=retry_after,
                    )
                if response.status_code >= 400:
                    raise GitHubAPIError(
                        f"GitHub API request failed with status {response.status_code}",
                        status_code=response.status_code,
                    )

                if response.status_code == 204:
                    return {}
                return response.json()
            except (GitHubAuthError, GitHubNotFoundError):
                raise
            except GitHubRateLimitError as error:
                last_error = error
                if attempt < MAX_RETRIES - 1:
                    time.sleep(error.retry_after or min(2**attempt, 60))
                    continue
                raise
            except httpx.HTTPError as error:
                last_error = error
                if attempt < MAX_RETRIES - 1:
                    time.sleep(min(2**attempt, 30))
                    continue
                raise GitHubAPIError("GitHub API network error") from error

        if last_error:
            raise last_error
        raise GitHubAPIError("GitHub API request failed")

    def _parse_retry_after(self, response: httpx.Response) -> float | None:
        retry_after = response.headers.get("Retry-After")
        if retry_after is not None:
            try:
                return float(retry_after)
            except ValueError:
                return None

        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining == "0":
            reset = response.headers.get("X-RateLimit-Reset")
            if reset is not None:
                try:
                    return max(float(reset) - time.time(), 1.0)
                except ValueError:
                    return None
        return None

    def _parse_repository(self, payload: dict[str, Any]) -> GitHubRepositoryInfo:
        return GitHubRepositoryInfo(
            id=payload["id"],
            owner=payload["owner"]["login"],
            name=payload["name"],
            full_name=payload["full_name"],
            default_branch=payload.get("default_branch") or "main",
            visibility=payload.get("visibility") or ("private" if payload.get("private") else "public"),
            description=payload.get("description"),
            updated_at=payload["updated_at"],
            private=bool(payload.get("private")),
        )


class GitHubOAuthClient:
    """GitHub OAuth authorization and token exchange."""

    def build_authorization_url(self, *, state: str) -> str:
        params = {
            "client_id": settings.github_client_id,
            "redirect_uri": settings.github_oauth_redirect_uri,
            "scope": settings.github_oauth_scopes,
            "state": state,
        }
        return f"{GITHUB_OAUTH_AUTHORIZE_URL}?{urlencode(params)}"

    def exchange_code_for_token(self, code: str) -> str:
        payload = {
            "client_id": settings.github_client_id,
            "client_secret": settings.github_client_secret,
            "code": code,
            "redirect_uri": settings.github_oauth_redirect_uri,
        }
        headers = {"Accept": "application/json"}
        with httpx.Client(timeout=30.0) as client:
            response = client.post(GITHUB_OAUTH_TOKEN_URL, json=payload, headers=headers)

        if response.status_code >= 400:
            raise GitHubAuthError("Failed to exchange GitHub authorization code")

        data = response.json()
        access_token = data.get("access_token")
        if not access_token:
            error = data.get("error_description") or data.get("error") or "Missing access token"
            raise GitHubAuthError(str(error))

        return access_token
