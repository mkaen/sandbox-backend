import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.config import settings
from src.core.security import decode_access_token
from src.db.database import get_db
from src.db.models import User
from src.features.users.repository import get_user_by_id


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated, missing token",
        )

    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token, could not decode",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token, no user id found",
        )

    user = get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
