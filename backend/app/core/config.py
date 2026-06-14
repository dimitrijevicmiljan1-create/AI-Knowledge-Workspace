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

    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    embedding_batch_size: int = 100
    embedding_max_retries: int = 3
    embedding_cost_per_million_tokens: float = 0.02

    search_default_top_k: int = 5
    search_max_top_k: int = 50
    search_recent_days: int = 7
    search_min_similarity: float = 0.70

    openai_chat_model: str = "gpt-4.1-mini"

    chat_max_history_messages: int = 10
    chat_max_history_tokens: int = 4000

    github_client_id: str = ""
    github_client_secret: str = ""
    github_oauth_redirect_uri: str = "http://localhost:8000/github/callback"
    github_oauth_scopes: str = "read:user repo"
    github_token_encryption_key: str = ""

    @property
    def async_database_url(self) -> str:
        return self.database_url.replace("postgresql://", "postgresql+psycopg2://")


settings = Settings()
