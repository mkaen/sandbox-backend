from fastapi import HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from src.features.r2.service import remove_image
from src.core.logger import logger
from src.constants import ImageTypes, UserRoles
from src.features.utils import generate_uuid
from src.core.security import clear_auth_cookies
from src.db.models import User
from src.features.auth import utils as auth_utils, service as auth_service
from src.features.users import repository
from src.features.users.schemas import UserResponseSchema, UserUpdatedDataRequestSchema
from src.features.r2 import service as r2_service


def get_user_by_id(db: Session, user_id: int) -> UserResponseSchema:
    user = repository.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail=f"User by id {user_id} not found")
    return UserResponseSchema.model_validate(user)


def update_user_data(user_id: int, current_user: User, db: Session, data: UserUpdatedDataRequestSchema) -> UserResponseSchema:

    user = repository.get_user_by_id(db, user_id)
    is_self_user = current_user.id == user_id

    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail=f"Cannot update user! User by id {user_id} not found")
    if data.role and is_self_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User {current_user.id} cannot change self role",
        )

    if user.first_name != data.first_name:
        user.first_name = data.first_name
    if user.last_name != data.last_name:
        user.last_name = data.last_name
    if user.email != data.email:
        user.email = data.email
    if user.phone != data.phone:
        user.phone = data.phone

    if data.role and current_user.role == UserRoles.ADMIN:
        user.role = repository.set_user_role(db, user_id, data.role)

    if all([data.old_password, data.new_password]):
        if not auth_utils.verify_password(data.old_password, user.password):
            raise HTTPException(
                status_code=400,
                detail="Client's entered old password does not match, cannot change password.",
            )
        user.password = auth_utils.hash_password(data.new_password)
        logger.info("User %s password updated", user_id)

    # if data.image_updated:
    #     user.image_reference = auth_utils.generate_image_reference()

    db.commit()

    return UserResponseSchema.model_validate(user)


def profile_image_upload_handler(user_id: int, request: Request, db: Session, image: bytes):
    """Validate request content, upload new profile image, remove old one and set new profile image reference into database."""

    content_type = request.headers.get("content-type")
    user = get_user_by_id(db, user_id)

    image_reference, success = r2_service.upload_image(ImageTypes.PROFILE.value, generate_uuid(), image, content_type)

    if image_reference:
        user.image_reference = image_reference
        db.commit()

    if user.image_reference and success:
        remove_image(ImageTypes.PROFILE.value, user.image_reference)


def remove_account(user_id: int, current_user: User, db: Session, response: Response) -> bool:
    user = repository.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail=f"User by id {user_id} not found")

    repository.deactivate_account(user, db)
    auth_service.revoke_all_user_sessions(db, user_id)

    if current_user.id == user_id:
        clear_auth_cookies(response)
    
    logger.info("User %s account removed successfully!", user_id)

    return True
