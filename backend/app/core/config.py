"""Central application configuration (Pydantic Settings)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "AstroSynth"
    APP_ENV: str = "development"
    API_VERSION: str = "v1"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000"

    DATABASE_URL: str = "postgresql+psycopg://astrosynth:astrosynth_dev_pw@localhost:5432/astrosynth"

    JWT_SECRET: str = "change-me-to-a-32-char-minimum-secret!!"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "astrosynth"

    ML_MODEL_REGISTRY_DIR: str = "ml/artifacts"
    RATE_LIMIT_PER_MINUTE: int = 60

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
