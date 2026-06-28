from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "sandbox-backend"
    DATABASE_URL: str
    SECRET_KEY: str
    CORS_ORIGINS: list[str] = ["http://localhost:8080"]
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    JWT_SIGNING_ALGORITHM: str = "HS256"
    COOKIE_NAME: str = "mk_access_token"
    COOKIE_SECURE: bool = False  # True production-is
    DB_ECHO: bool = True

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
