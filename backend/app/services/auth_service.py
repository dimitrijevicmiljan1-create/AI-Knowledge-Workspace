import uuid

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_password_hash,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.repositories.user_settings_repository import UserSettingsRepository
from app.schemas.auth import Token, UserLogin, UserRegister
from app.schemas.user import UserResponse
from app.services.workspace_service import WorkspaceService


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)

    def register_user(self, user_in: UserRegister) -> UserResponse:
        existing_user = self.user_repository.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists",
            )

        user = self.user_repository.create(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
        )
        WorkspaceService(self.db).ensure_user_workspace(user)
        UserSettingsRepository(self.db).create_defaults(user.id)
        return UserResponse.model_validate(user)

    def login_user(self, credentials: UserLogin) -> Token:
        user = self.user_repository.get_by_email(credentials.email)
        if user is None or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account",
            )

        return self._create_token_pair(user.id)

    def refresh_access_token(self, refresh_token: str) -> Token:
        try:
            payload = decode_refresh_token(refresh_token)
            user_id = uuid.UUID(payload["sub"])
        except (JWTError, ValueError, KeyError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account",
            )

        return self._create_token_pair(user.id)

    def get_current_user(self, user_id: uuid.UUID) -> UserResponse:
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return UserResponse.model_validate(user)

    def _create_token_pair(self, user_id: uuid.UUID) -> Token:
        return Token(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )
