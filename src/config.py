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

settings = Settings()

# Here, you create a Settings class that reads variables from a .env file. This way, you keep secrets and 
# environment-specific settings (like your database URL or secret keys) outside your codebase, improving 
# security and flexibility.

# You can then import settings anywhere in your app without duplicating environment handling code. 
# If you deploy to staging or production, you only need to swap .env files or environment variables.

# You might also add a security.py file here for reusable helpers, like JWT token management or OAuth scopes, 
# keeping all security-related configuration in one place.
