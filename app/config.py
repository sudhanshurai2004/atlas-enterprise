from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    app_port: int = 8080
    gcp_project_id: str = "atlas-demo"
    gcp_region: str = "asia-south1"
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
