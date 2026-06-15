from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.settings import (
    IntegrationStatusResponse,
    UsageStatsResponse,
    UserSettingsResponse,
    UserSettingsUpdate,
)
from app.schemas.workspace import WorkspaceResponse, WorkspaceStatsResponse
from app.services.settings_service import SettingsService
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/profile/workspace", response_model=WorkspaceResponse)
def get_profile_workspace(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> WorkspaceResponse:
    workspace = WorkspaceService(db).get_user_workspace(current_user)
    return WorkspaceResponse.model_validate(workspace)


@router.get("/ai", response_model=UserSettingsResponse)
def get_ai_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserSettingsResponse:
    return SettingsService(db).get_settings(current_user)


@router.patch("/ai", response_model=UserSettingsResponse)
def update_ai_settings(
    settings_in: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserSettingsResponse:
    return SettingsService(db).update_settings(current_user, settings_in)


@router.get("/knowledge", response_model=UserSettingsResponse)
def get_knowledge_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserSettingsResponse:
    return SettingsService(db).get_settings(current_user)


@router.patch("/knowledge", response_model=UserSettingsResponse)
def update_knowledge_settings(
    settings_in: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserSettingsResponse:
    return SettingsService(db).update_settings(current_user, settings_in)


@router.get("/integrations", response_model=IntegrationStatusResponse)
def get_integrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> IntegrationStatusResponse:
    return SettingsService(db).get_integrations(current_user)


@router.get("/usage", response_model=UsageStatsResponse)
def get_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UsageStatsResponse:
    return SettingsService(db).get_usage(current_user)


@router.get("/usage/workspace-stats", response_model=WorkspaceStatsResponse)
def get_workspace_usage_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> WorkspaceStatsResponse:
    workspace = WorkspaceService(db).get_user_workspace(current_user)
    return WorkspaceService(db).get_workspace_stats(current_user, workspace.id)
