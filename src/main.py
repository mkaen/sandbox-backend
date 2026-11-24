from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.exception_handlers import register_exception_handlers
from src.core.middleware import register_middleware
from src.api.router import api_router
from src.config import settings
from src.core.exception_handlers import register_exception_handlers
from src.core.logger import configure_logging, logger
from src.core.middleware import register_middleware
from src.core.redis import create_redis_client
from src.providers.coingecko.client import CoinGeckoClient, create_http_client


configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application is starting up...")
    coingecko_http = create_http_client()
    app.state.coingecko_http = coingecko_http
    app.state.coingecko_client = CoinGeckoClient(coingecko_http)
    app.state.redis = create_redis_client(settings.REDIS_URL)
    try:
        yield
    finally:
        await coingecko_http.aclose()
        await app.state.redis.aclose()
        logger.info("Application is shutting down...")


def create_app():
    is_prod = settings.ENVIRONMENT == "production"
    app = FastAPI(
        lifespan=lifespan,
        docs_url=None if is_prod else "/docs",
        redoc_url=None if is_prod else "/redoc",
        openapi_url=None if is_prod else "/openapi.json",
    )
    register_exception_handlers(app)
    register_middleware(app)
    app.include_router(api_router)
    return app


app = create_app()
