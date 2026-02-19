"""
aitema|RIS - Application Configuration
Centralized settings management using pydantic-settings.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "aitema|RIS"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"
    secret_key: str = "dev-secret-key-change-in-production"
    cors_origins: str = "http://localhost:3000"

    # --- Database ---
    database_url: str = "postgresql+asyncpg://ris:ris_dev_password@localhost:5432/ris"
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_echo: bool = False

    # --- Redis ---
    redis_url: str = "redis://:redis_dev_password@localhost:6379/0"
    redis_cache_ttl: int = 300  # seconds

    # --- Elasticsearch ---
    elasticsearch_url: str = "http://localhost:9200"
    es_password: str = ""
    es_index_prefix: str = "ris"

    # --- MinIO ---
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minio_dev"
    minio_secret_key: str = "minio_dev_password"
    minio_secure: bool = False
    minio_bucket: str = "ris-documents"

    # --- Keycloak ---
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "ris"
    keycloak_client_id: str = "ris-backend"

    # --- DMS Bridge ---
    dms_type: Literal["none", "dvelop", "enaio", "custom"] = "none"
    dms_dvelop_base_url: str = ""
    dms_dvelop_api_key: str = ""

    # --- Sentry ---
    sentry_dsn: str = ""

    # --- OParl ---
    oparl_base_url: str = "http://localhost:8000/api/v1/oparl"
    oparl_version: str = "https://schema.oparl.org/1.1/"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str) -> str:
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def sync_database_url(self) -> str:
        return self.database_url.replace("+asyncpg", "")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
