import os
from dotenv import load_dotenv
from src.config import settings
import jwt
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from fastapi import Response

load_dotenv()

SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
ALGORITHM = os.getenv("ALGORITHM")

password_hash = PasswordHash.recommended()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, ALGORITHM)


def set_access_token_cookie(response: Response, access_token: str):
    response.set_cookie(key="mk_sanbox_access_token",
                        value=access_token,
                        httponly=True,
                        secure=True, 
                        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                        samesite="lax")


# def hash_and_salt_password(password: str) -> str:
#     return PasswordHash(password, algorythm)

# def verify_password(password: str, hashed_password: str) -> bool:   
#     return PasswordHash(password).verify(hashed_password)

