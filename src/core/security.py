from src.config import settings
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Response


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, settings.JWT_SIGNING_ALGORITHM)


def set_access_token_cookie(response: Response, access_token: str):
    response.set_cookie(key=settings.COOKIE_NAME,
                        value=access_token,
                        httponly=True,
                        secure=settings.COOKIE_SECURE,
                        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                        samesite="lax")


def decode_access_token(token: str):
    return jwt.decode(token, settings.SECRET_KEY, settings.JWT_SIGNING_ALGORITHM)
