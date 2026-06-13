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

    storage_upload_path: str = "storage/uploads"
    max_upload_size_bytes: int = 20 * 1024 * 1024

    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    embedding_batch_size: int = 100
    embedding_max_retries: int = 3
    embedding_cost_per_million_tokens: float = 0.02

    @property
    def async_database_url(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+psycopg2://")


settings = Settings()
