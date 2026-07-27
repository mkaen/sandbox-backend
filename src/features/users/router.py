from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.models import User
from src.features.auth.dependencies import get_current_user
from src.features.users import service
from src.features.users.schemas import UserResponseSchema

router_v1 = APIRouter(prefix="/v1/users", tags=["users"])


@router_v1.get("/me")
async def me(user: Annotated[User, Depends(get_current_user)]) -> UserResponseSchema:
    return UserResponseSchema.model_validate(user)


@router_v1.get("/{user_id}", status_code=200)
async def get_user_by_id(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserResponseSchema:
    return service.get_user_by_id(db, current_user, user_id)
