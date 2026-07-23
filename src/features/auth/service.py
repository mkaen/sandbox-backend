from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, Response
from sqlalchemy.orm import Session

from features.auth.utils import verify_password
from src.config import settings
from src.core.security import (
    clear_auth_cookies,
    create_access_token,
    generate_refresh_token,
    set_access_token_cookie,
    set_refresh_token_cookie,
)
from src.db.models import User
from src.features.auth.repository import create_refresh_token, get_refresh_token, revoke_refresh_token
from src.features.auth.schemas import LoginRequestSchema, RegisterRequestSchema
from src.features.users.repository import create_user, get_user_by_email, get_user_by_id
from src.features.users.schemas import UserResponseSchema


def _user_response(user: User) -> UserResponseSchema:
    return UserResponseSchema(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        email=user.email,
        image_reference=user.image_reference,
        role=user.role,
    )


def _issue_auth_tokens(response: Response, db: Session, user_id: int) -> None:
    access_token = create_access_token({"sub": str(user_id)})
    set_access_token_cookie(response, access_token)

    refresh_token = generate_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    create_refresh_token(db, user_id, refresh_token, expires_at)
    set_refresh_token_cookie(response, refresh_token)


def register_user(registration_data: RegisterRequestSchema, response: Response, db: Session):
    if get_user_by_email(db, registration_data.email):
        raise HTTPException(status_code=400, detail="User with this email already exists")

    new_user = create_user(db, registration_data)

    if not new_user:
        raise HTTPException(status_code=500, detail="Failed to create user")

    _issue_auth_tokens(response, db, new_user.id)
    return _user_response(new_user)


def authenticate_user(data: LoginRequestSchema, response: Response, db: Session):
    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=401, detail="User with this email does not exist")
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Password is incorrect")

    _issue_auth_tokens(response, db, user.id)
    return _user_response(user)


def refresh_access_token(request: Request, response: Response, db: Session):
    token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated, missing refresh token")

    stored_token = get_refresh_token(db, token)
    if not stored_token or stored_token.revoked:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    expires_at = stored_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token has expired")

    user = get_user_by_id(db, stored_token.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    revoke_refresh_token(db, token)
    _issue_auth_tokens(response, db, user.id)
    return _user_response(user)


def logout_user(request: Request, response: Response, db: Session):
    token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)
    if token:
        revoke_refresh_token(db, token)

    clear_auth_cookies(response)
