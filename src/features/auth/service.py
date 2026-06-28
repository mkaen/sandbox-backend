from fastapi import Response
from features.auth.utils import verify_password
from src.features.auth.schemas import AuthorizedUserResponseSchema, LoginRequestSchema, RegisterRequestSchema
from src.core.security import create_access_token, set_access_token_cookie
from src.features.users.repository import create_user, get_user_by_email
from sqlalchemy.orm import Session
from fastapi import HTTPException


def register_user(registration_data: RegisterRequestSchema, response: Response, db: Session):
    if get_user_by_email(db, registration_data.email):
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    created_user = create_user(db, registration_data)

    if created_user:
        access_token = create_access_token({"sub": registration_data.email})
        set_access_token_cookie(response, access_token)

        return AuthorizedUserResponseSchema(
            id=created_user.id,
            first_name=created_user.first_name,
            last_name=created_user.last_name,
            phone=created_user.phone,
            email=created_user.email,
            image_reference=created_user.image_reference,
            role=created_user.role,
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to create user")


def authenticate_user(data: LoginRequestSchema, response: Response, db: Session):
    """
    Authenticate a user by email and password.
    Args:
        data: LoginRequestSchema
        response: Response
        db: Session
    Returns:
        bool: True if the user is authenticated, False otherwise
    """
    user = get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=401, detail="User with this email does not exist")
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Password is incorrect")

    access_token = create_access_token({"sub": data.email})
    set_access_token_cookie(response, access_token)

    return AuthorizedUserResponseSchema(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        email=user.email,
        image_reference=user.image_reference,
        role=user.role,
    )
