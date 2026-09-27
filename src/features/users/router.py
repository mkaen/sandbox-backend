from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response as ImageResponse
from sqlalchemy.orm import Session

from src.core.logger import logger
from src.db.database import get_db
from src.db.models import User
from src.features.auth.dependencies import get_current_user
from src.features.users import service
from src.features.users.dependencies import require_admin_not_self, require_self_or_admin
from src.features.users.schemas import (
    UserResponseSchema,
    UserSetArchiveRequestSchema,
    UserSetIsArchivedResponseSchema,
    UserUpdatedDataRequestSchema,
)

router_v1 = APIRouter(prefix="/v1/users", tags=["users"])


@router_v1.get("/me")
async def me(user: Annotated[User, Depends(get_current_user)]) -> UserResponseSchema:
    return UserResponseSchema.model_validate(user)


@router_v1.get("/{user_id}", status_code=200, summary="Get user by id")
async def get_user_by_id(user_id: int, _: Annotated[User, Depends(require_self_or_admin)], db: Annotated[Session, Depends(get_db)]) -> UserResponseSchema:
    return service.get_user_by_id(db, user_id)


@router_v1.put("/update/{user_id}", status_code=200, summary="Update user data")
async def update_user_data(
    user_id: int,
    data: UserUpdatedDataRequestSchema,
    current_user: Annotated[User, Depends(require_self_or_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> UserResponseSchema:
    return service.update_user_data(user_id, current_user, db, data)


@router_v1.get(
    "/image/{user_id}",
    status_code=200,
    summary="Get profile image by id",
    responses={404: {"description": "User or profile image not found"}},
)
async def get_profile_image_by_id(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_self_or_admin)],
) -> ImageResponse:
    """Fetch user profile image bytes from worker after authz check."""
    logger.info(f"Got request to fetch image to user {user_id}")
    content, content_type = await run_in_threadpool(service.get_profile_image_by_id, user_id, db)
    return ImageResponse(content=content, media_type=content_type)


@router_v1.post(
    "/upload-profile-image/{user_id}",
    status_code=204,
    summary="Upload profile image",
    responses={400: {"description": "Unsupported content type"}},
)
async def upload_profile_image(
    user_id: int,
    request: Request,
    _: Annotated[User, Depends(require_self_or_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    logger.info(f"Got request to upload user {user_id} profile image.")
    image = await request.body()
    await run_in_threadpool(service.profile_image_upload_handler, user_id, request, db, image)


@router_v1.put(
    "/{user_id}/archive",
    status_code=200,
    summary="Set user archive status",
)
async def user_archive_handler(
    user_id: int,
    body: UserSetArchiveRequestSchema,
    _: Annotated[User, Depends(require_admin_not_self)],
    db: Annotated[Session, Depends(get_db)],
) -> UserSetIsArchivedResponseSchema:
    logger.info(f"Got request to update user {user_id} archive value to {body.data}.")
    return service.update_user_archive_value(db, user_id, body.data)


@router_v1.delete("/remove/{user_id}", status_code=200, summary="Deactivate account")
async def remove_account(
    user_id: int,
    current_user: Annotated[User, Depends(require_self_or_admin)],
    db: Annotated[Session, Depends(get_db)],
    response: Response,
) -> bool:
    logger.info(f"Got request to remove user {user_id} account.")
    return service.remove_account(user_id, current_user, db, response)
