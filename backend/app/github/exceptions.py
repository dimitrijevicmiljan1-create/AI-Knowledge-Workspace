class GitHubAPIError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class GitHubRateLimitError(GitHubAPIError):
    def __init__(self, message: str, *, retry_after: float | None = None) -> None:
        super().__init__(message, status_code=403)
        self.retry_after = retry_after


class GitHubAuthError(GitHubAPIError):
    pass


class GitHubNotFoundError(GitHubAPIError):
    pass
