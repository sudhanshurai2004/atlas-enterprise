from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    app_env: str = "local"
    app_port: int = 8080
    gcp_project_id: str = "atlas-demo"
    gcp_region: str = "asia-south1"
    google_api_key: str | None = None
    google_genai_model: str = "gemini-2.5-flash"
    google_embedding_model: str = "gemini-embedding-001"
    api_username: str | None = None
    api_password: str | None = None
    database_url: str = "postgresql://atlas:atlas_dev@localhost:5432/atlas"
    gcs_bucket: str | None = None
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "atlas-local-secret"
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

if settings.google_api_key:
    os.environ.setdefault("GOOGLE_API_KEY", settings.google_api_key)
