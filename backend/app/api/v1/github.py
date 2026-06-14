from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.github import (
    GitHubConnectionResponse,
    GitHubConnectResponse,
    GitHubOAuthCallbackResponse,
    GitHubRepositoryAddRequest,
    GitHubRepositoryDiscoveryResponse,
    GitHubRepositoryResponse,
    GitHubRepositorySyncResponse,
    GitHubSyncJobResponse,
)
from app.services.github_service import GitHubService

router = APIRouter(prefix="/github", tags=["github"])


@router.post(
    "/connect",
    response_model=GitHubConnectResponse,
    status_code=status.HTTP_200_OK,
    summary="Initiate GitHub OAuth connection",
    description=(
        "Returns a GitHub authorization URL. Redirect the user to this URL to authorize "
        "the application. After authorization, GitHub redirects to `/github/callback`."
    ),
    responses={
        401: {"description": "Unauthorized"},
    },
)
def connect_github(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> GitHubConnectResponse:
    return GitHubService(db).initiate_connect(current_user)


@router.get(
    "/callback",
    response_model=GitHubOAuthCallbackResponse,
    summary="GitHub OAuth callback",
    description=(
        "Handles the GitHub OAuth redirect, exchanges the authorization code for an access "
        "token, encrypts the token, and stores the GitHub connection."
    ),
    responses={
        400: {"description": "Invalid OAuth state or authorization code"},
    },
)
def github_callback(
    code: str = Query(..., description="Authorization code from GitHub"),
    state: str = Query(..., description="Signed OAuth state token"),
    db: Session = Depends(get_db),
) -> GitHubOAuthCallbackResponse:
    return GitHubService(db).complete_oauth(code=code, state=state)


@router.get(
    "/connection",
    response_model=GitHubConnectionResponse,
    summary="Get connected GitHub account",
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "GitHub account is not connected"},
    },
)
def get_github_connection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> GitHubConnectionResponse:
    return GitHubService(db).get_connection(current_user)


@router.get(
    "/repositories",
    response_model=GitHubRepositoryDiscoveryResponse,
    summary="Discover GitHub repositories",
    description=(
        "Lists repositories accessible to the connected GitHub account, including private "
        "and public repositories with pagination support."
    ),
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "GitHub account is not connected"},
    },
)
def list_github_repositories(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> GitHubRepositoryDiscoveryResponse:
    return GitHubService(db).list_discovered_repositories(
        current_user,
        page=page,
        per_page=per_page,
    )


@router.post(
    "/repositories",
    response_model=GitHubRepositoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a GitHub repository to a workspace",
    description=(
        "Selects a GitHub repository for indexing. Creates a GitHub source and tracked "
        "repository record linked to the workspace."
    ),
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "User is not the workspace owner"},
        404: {"description": "GitHub account or workspace not found"},
    },
)
def add_github_repository(
    repository_in: GitHubRepositoryAddRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> GitHubRepositoryResponse:
    return GitHubService(db).add_repository(current_user, repository_in)


@router.get(
    "/repositories/{repository_id}",
    response_model=GitHubRepositoryResponse,
    summary="Get tracked GitHub repository",
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "GitHub repository not found"},
    },
)
def get_github_repository(
    repository_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> GitHubRepositoryResponse:
    return GitHubService(db).get_repository(current_user, repository_id)


@router.post(
    "/repositories/{repository_id}/sync",
    response_model=GitHubRepositorySyncResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start repository sync",
    description=(
        "Starts an asynchronous repository sync job. The API returns immediately with "
        "job tracking information while indexing runs in the background."
    ),
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "GitHub repository not found"},
    },
)
def sync_github_repository(
    repository_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> GitHubRepositorySyncResponse:
    return GitHubService(db).start_sync(current_user, repository_id)


@router.get(
    "/repositories/{repository_id}/status",
    response_model=GitHubSyncJobResponse,
    summary="Get repository sync status",
    description="Returns the latest sync job status and progress counters for a repository.",
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "GitHub repository or sync job not found"},
    },
)
def get_github_repository_status(
    repository_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> GitHubSyncJobResponse:
    return GitHubService(db).get_sync_status(current_user, repository_id)


@router.delete(
    "/repositories/{repository_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove tracked GitHub repository",
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "GitHub repository not found"},
    },
)
def delete_github_repository(
    repository_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    GitHubService(db).delete_repository(current_user, repository_id)
