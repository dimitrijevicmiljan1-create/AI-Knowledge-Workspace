from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, Token, UserLogin, UserRegister
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
def register(
    user_in: UserRegister,
    db: Session = Depends(get_db),
) -> UserResponse:
    return AuthService(db).register_user(user_in)


@router.post(
    "/login",
    response_model=Token,
    responses={401: {"description": "Incorrect email or password"}},
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
) -> Token:
    return AuthService(db).login_user(credentials)


@router.post("/refresh", response_model=Token)
def refresh_token(
    body: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> Token:
    return AuthService(db).refresh_access_token(body.refresh_token)


@router.get("/me", response_model=UserResponse)
def get_auth_me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)
