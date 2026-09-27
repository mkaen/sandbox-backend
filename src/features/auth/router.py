from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from src.features.auth.dependencies import get_current_user
from src.db.models import User
from src.core.logger import logger
from src.db.database import get_db
from src.features.auth import service
from src.features.auth.schemas import LoginRequestSchema, RegisterRequestSchema
from src.features.users.schemas import UserResponseSchema

auth_router_v1 = APIRouter(prefix="/v1/auth", tags=["auth"])


@auth_router_v1.post("/login", status_code=200, summary="Login user")
async def login(
    login_request: LoginRequestSchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponseSchema:
    logger.info(f"Got request to login user with e-mail {login_request.email}")
    return service.authenticate_user(login_request, response, db)


@auth_router_v1.post("/register", status_code=201, summary="Register new user")
async def register(
    registration_data: RegisterRequestSchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponseSchema:
    logger.info("Got request to create new user.")
    return service.register_user(registration_data, response, db)


@auth_router_v1.post("/refresh", status_code=200, summary="Refresh access and refresh token")
async def refresh(
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponseSchema:
    logger.info("Got request to refresh token.")
    return service.refresh_access_token(request, response, db)


@auth_router_v1.post("/logout", status_code=204, summary="Logout user")
async def logout(
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    logger.info(f"Got request to log out user {current_user.id}")
    service.logout_user(request, response, db)
