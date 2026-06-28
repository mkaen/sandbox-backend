from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core.middleware import register_middleware
from src.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application is starting up...")
    yield
    print("Application is shutting down...")


def create_app():

    app = FastAPI(lifespan=lifespan)

    register_middleware(app)
    _register_routers(app)
    

    return app


def _register_routers(app: FastAPI):
    app.include_router(api_router)


app = create_app()


