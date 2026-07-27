from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.constants import UserRoles
from src.db.models import User
from src.features.users import repository
from src.features.users.schemas import UserResponseSchema


def get_user_by_id(db: Session, current_user: User, user_id: int) -> UserResponseSchema:
    if current_user.id != user_id and current_user.role != UserRoles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not allowed user id:{current_user.id} to request user id {user_id} data",
        )
    user = repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User by id {user_id} not found")
    return UserResponseSchema.model_validate(user)
