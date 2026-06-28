from fastapi import HTTPException
from features.auth.utils import hash_password
from src.db.models import User
from sqlalchemy.orm import Session
from pydantic import EmailStr
from src.features.auth.schemas import RegisterRequestSchema


def create_user(db: Session, user: RegisterRequestSchema) -> User:
    """
    Create new user and save it to the database. If user is created successfully, return the user object.
    Args:
        db: Session
        user: RegisterRequestSchema
    Returns:
        User: User object
    """
    user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        email=user.email,
        password=hash_password(user.password),
        image_reference=user.has_image,
    )
    db.add(user)
    db.commit()
    return user


def get_user_by_email(db: Session, email: EmailStr) -> User:
    """
    Get a user by email. 
    Args:
        db: Session
        email: EmailStr
    Returns:
        User: User object or None
    """
    return db.query(User).filter(User.email == email).first()
