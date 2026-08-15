from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core.middleware import register_middleware
from src.api.router import api_router
from src.config import settings
from src.core.logger import configure_logging, logger


configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application is starting up...")
    yield
    logger.info("Application is shutting down...")


def create_app():
    is_prod = settings.ENVIRONMENT == "production"
    app = FastAPI(
        lifespan=lifespan,
        docs_url=None if is_prod else "/docs",
        redoc_url=None if is_prod else "/redoc",
        openapi_url=None if is_prod else "/openapi.json",
    )
    register_middleware(app)
    app.include_router(api_router)
    return app


app = create_app()
