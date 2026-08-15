from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Host-mapped local Compose Postgres → service DNS inside the compose network.
_LOCAL_DB_HOSTS = ("127.0.0.1:5433", "localhost:5433", "[::1]:5433")
_COMPOSE_DB_HOST = "db:5432"


def _running_in_docker() -> bool:
    return Path("/.dockerenv").exists()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "sandbox-backend"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str
    SECRET_KEY: str
    CORS_ORIGINS: list[str] = ["http://localhost:8080"]
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_SIGNING_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_COOKIE_NAME: str = "access_token"
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"
    COOKIE_SECURE: bool = False  # True on HTTPS (production)
    COOKIE_SAMESITE: str = "lax"
    POOL_PRE_PING: bool = False
    DB_ECHO: bool = True
    LOGGER_NAME: str = 'sandbox-backend'
    LOG_LEVEL: str = 'INFO'
    LOG_JSON: bool = True
    TIMEZONE: str = "Europe/Tallinn"

    @field_validator("DATABASE_URL")
    @classmethod
    def rewrite_local_compose_db_host(cls, value: str) -> str:
        if not _running_in_docker():
            return value
        for host in _LOCAL_DB_HOSTS:
            if host in value:
                return value.replace(host, _COMPOSE_DB_HOST, 1)
        return value

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
