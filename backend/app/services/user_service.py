from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse, UserUpdate


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)

    def get_me(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    def update_me(self, user: User, user_in: UserUpdate) -> UserResponse:
        update_data = user_in.model_dump(exclude_unset=True)

        if "email" in update_data and update_data["email"] != user.email:
            existing_user = self.user_repository.get_by_email(update_data["email"])
            if existing_user is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this email already exists",
                )

        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        updated_user = self.user_repository.update(user, **update_data)
        return UserResponse.model_validate(updated_user)

    def delete_me(self, user: User) -> None:
        self.user_repository.delete(user)
