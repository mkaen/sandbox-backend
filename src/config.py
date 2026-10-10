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
    R2_WORKER_URL: str
    R2_UPLOAD_KEY: str
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
    def normalize_database_url(cls, value: str) -> str:
        if _running_in_docker():
            for host in _LOCAL_DB_HOSTS:
                if host in value:
                    value = value.replace(host, _COMPOSE_DB_HOST, 1)
                    break
        # SQLAlchemy 2.0.5x treats bare postgresql:// as psycopg3; we ship psycopg2-binary.
        if value.startswith("postgresql://"):
            return "postgresql+psycopg2://" + value[len("postgresql://") :]
        if value.startswith("postgres://"):
            return "postgresql+psycopg2://" + value[len("postgres://") :]
        return value

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
