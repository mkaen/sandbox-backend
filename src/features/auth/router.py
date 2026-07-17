from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.features.auth import service
from src.features.auth.schemas import AuthorizedUserResponseSchema, LoginRequestSchema, RegisterRequestSchema

auth_router_v1 = APIRouter(prefix="/v1/auth", tags=["auth"])


@auth_router_v1.post("/login", status_code=200)
async def login(
    login_request: LoginRequestSchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> AuthorizedUserResponseSchema:
    return service.authenticate_user(login_request, response, db)


@auth_router_v1.post("/register", status_code=201)
async def register(
    registration_data: RegisterRequestSchema,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> AuthorizedUserResponseSchema:
    return service.register_user(registration_data, response, db)


@auth_router_v1.post("/refresh", status_code=200)
async def refresh(
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> AuthorizedUserResponseSchema:
    return service.refresh_access_token(request, response, db)


@auth_router_v1.post("/logout", status_code=204)
async def logout(
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    service.logout_user(request, response, db)
