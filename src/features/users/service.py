from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session

from src.constants import UserRoles
from src.core.security import clear_auth_cookies
from src.db.models import User
from src.features.auth import utils as auth_utils, service as auth_service
from src.features.users import repository
from src.features.users.schemas import UserResponseSchema, UserUpdatedDataRequestSchema


def get_user_by_id(db: Session, user_id: int) -> UserResponseSchema:
    user = repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User by id {user_id} not found")
    return UserResponseSchema.model_validate(user)


def update_user_data(
    user_id: int,
    current_user: User,
    db: Session,
    data: UserUpdatedDataRequestSchema,
) -> UserResponseSchema:
    user = repository.get_user_by_id(db, user_id)
    is_self_user = current_user.id == user_id

    if not user:
        raise HTTPException(status_code=404, detail=f"User by id {user_id} not found")
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

    if data.image_updated:
        user.image_reference = auth_utils.generate_image_reference()

    db.commit()

    return UserResponseSchema.model_validate(user)


def remove_account(
    user_id: int,
    current_user: User,
    db: Session,
    response: Response,
) -> bool:
    user = repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User by id {user_id} not found")

    repository.deactivate_account(user, db)
    auth_service.revoke_all_user_sessions(db, user_id)

    if current_user.id == user_id:
        clear_auth_cookies(response)

    return True
