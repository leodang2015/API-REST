from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Biblioteca API"
    database_url: str = "postgresql+psycopg://biblioteca:biblioteca@localhost:5432/biblioteca"
    test_database_url: str = "postgresql+psycopg://biblioteca:biblioteca@localhost:5432/biblioteca_test"
    secret_key: str = Field(min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=15, gt=0)
    refresh_token_expire_days: int = Field(default=7, gt=0)
    max_failed_login_attempts: int = Field(default=5, gt=0)
    account_lock_minutes: int = Field(default=15, gt=0)
    cors_origins: list[str] = Field(default_factory=list)
    environment: Literal["dev", "test", "prod"] = "dev"
    cloudinary_url: SecretStr | None = None
    cloudinary_cloud_name: str | None = None
    cloudinary_api_key: str | None = None
    cloudinary_api_secret: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
