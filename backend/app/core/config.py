from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@postgres:5432/ai_knowledge_workspace"

    jwt_secret_key: str = "change-me-in-production"
    jwt_refresh_secret_key: str = "change-me-refresh-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    ingestion_chunk_size: int = 1000
    ingestion_chunk_overlap: int = 100

    chunk_size: int = 1000
    chunk_overlap: int = 200
    default_chunk_strategy: str = "recursive"

    storage_upload_path: str = "storage/uploads"
    max_upload_size_bytes: int = 20 * 1024 * 1024

    @property
    def async_database_url(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+psycopg2://")


settings = Settings()
