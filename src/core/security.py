import secrets

import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Response

from src.config import settings


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, settings.JWT_SIGNING_ALGORITHM)


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def set_access_token_cookie(response: Response, access_token: str):
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )


def set_refresh_token_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
    )


def clear_auth_cookies(response: Response):
    response.delete_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
    )
    response.delete_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
    )


def decode_access_token(token: str):
    return jwt.decode(token, settings.SECRET_KEY, settings.JWT_SIGNING_ALGORITHM)
