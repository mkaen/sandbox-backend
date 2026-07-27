from typing import Annotated

from fastapi import Depends, HTTPException, status

from src.constants import UserRoles
from src.db.models import User
from src.features.auth.dependencies import get_current_user


def require_self_or_admin(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.id != user_id and current_user.role != UserRoles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User {current_user.id} is unauthorized to access user {user_id}",
        )
    return current_user
