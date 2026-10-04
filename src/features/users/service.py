from fastapi import HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from src.features.r2.service import remove_image
from src.core.logger import logger
from src.constants import ImageTypesFolderName
from src.features.utils import generate_uuid
from src.core.security import clear_auth_cookies
from src.db.models import User
from src.features.auth import utils as auth_utils, service as auth_service
from src.features.users import repository
from src.features.users.schemas import UserResponseSchema, UserSetIsArchivedResponseSchema, UserUpdatedDataRequestSchema
from src.features.r2 import service as r2_service
from src.features.users.utils import handle_role_change_permission


def _get_active_user(db: Session, user_id: int) -> User:
    user = repository.get_active_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"Active user by id {user_id} not found")
    return user


def get_user_by_id(db: Session, user_id: int) -> UserResponseSchema:
    return UserResponseSchema.model_validate(_get_active_user(db, user_id))


def update_user_archive_value(db: Session, user_id: int, value: bool) -> UserSetIsArchivedResponseSchema:
    user = _get_active_user(db, user_id)
    updated_user = repository.set_user_archive_value(db, user, value)
    return UserSetIsArchivedResponseSchema.model_validate(updated_user)



def update_user_data(user_id: int, current_user: User, db: Session, data: UserUpdatedDataRequestSchema) -> UserResponseSchema:
    if user_id != data.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request id {user_id} do not match with payload id {data.id}.",
        )

    user = _get_active_user(db, user_id)
    is_self_user = current_user.id == user_id

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
        existing = repository.get_user_by_email(db, data.email)
        if existing and existing.id != user.id:
            logger.info(f"Cannot update email. User with email {data.email} already exists.")
            raise HTTPException(status_code=400, detail=f"Cannot update email to: {data.email}")
        user.email = data.email
    if user.phone != data.phone:
        user.phone = data.phone

    if data.role and handle_role_change_permission(data.role, current_user, user):
        user.role = data.role

    if all([data.old_password, data.new_password]):
        if not auth_utils.verify_password(data.old_password, user.password):
            raise HTTPException(
                status_code=400,
                detail="Client's entered old password does not match, cannot change password.",
            )
        user.password = auth_utils.hash_password(data.new_password)
        logger.info("User %s password is updated", user_id)

    repository.save_user(db, user)

    return UserResponseSchema.model_validate(user)


def get_profile_image_by_id(user_id: int, db: Session) -> tuple[bytes, str]:
    """Load profile image bytes from worker after resolving the user's image reference."""
    user = _get_active_user(db, user_id)
    if not user.image_reference:
        raise HTTPException(status_code=404, detail="Profile image not found")

    return r2_service.fetch_profile_image(user.image_reference)


def profile_image_upload_handler(user_id: int, request: Request, db: Session, image: bytes) -> None:
    """Validate request content, upload new profile image, remove old one and set new profile image reference into database."""
    content_type = request.headers.get("content-type")
    user = _get_active_user(db, user_id)

    old_image_reference = user.image_reference
    image_reference_uuid = generate_uuid()
    folder = ImageTypesFolderName.PROFILE.value

    r2_service.upload_image(folder, image_reference_uuid, image, content_type)

    try:
        repository.set_user_image_reference(db, user, image_reference_uuid)
    except Exception:
        try:
            remove_image(folder, str(image_reference_uuid))
        except Exception:
            logger.exception("Failed to remove orphaned profile image %s after DB error", image_reference_uuid)
        raise

    logger.info("User %s profile image reference saved", user_id)

    if old_image_reference:
        remove_image(folder, old_image_reference)


def remove_account(user_id: int, current_user: User, db: Session, response: Response) -> bool:
    user = _get_active_user(db, user_id)

    repository.deactivate_account(db, user)
    auth_service.revoke_all_user_sessions(db, user_id)

    if current_user.id == user_id:
        clear_auth_cookies(response)

    logger.info("User %s account removed successfully!", user_id)

    return True
