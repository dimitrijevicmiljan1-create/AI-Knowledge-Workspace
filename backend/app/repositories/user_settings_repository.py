import uuid

from sqlalchemy.orm import Session

from app.models.user_settings import UserSettings


class UserSettingsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user_id(self, user_id: uuid.UUID) -> UserSettings | None:
        return self.db.get(UserSettings, user_id)

    def create_defaults(self, user_id: uuid.UUID) -> UserSettings:
        settings = UserSettings(user_id=user_id)
        self.db.add(settings)
        self.db.commit()
        self.db.refresh(settings)
        return settings

    def get_or_create(self, user_id: uuid.UUID) -> UserSettings:
        settings = self.get_by_user_id(user_id)
        if settings is None:
            return self.create_defaults(user_id)
        return settings

    def update(self, settings: UserSettings, **fields: object) -> UserSettings:
        for field, value in fields.items():
            if value is not None:
                setattr(settings, field, value)
        self.db.commit()
        self.db.refresh(settings)
        return settings
