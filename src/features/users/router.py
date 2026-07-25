from typing import Annotated

from fastapi import APIRouter, Depends

from src.db.models import User
from src.features.auth.dependencies import get_current_user
from src.features.users.schemas import UserResponseSchema

router_v1 = APIRouter(prefix="/v1/users", tags=["users"])


@router_v1.get("/me")
async def me(user: Annotated[User, Depends(get_current_user)]) -> UserResponseSchema:
    return UserResponseSchema.model_validate(user)
