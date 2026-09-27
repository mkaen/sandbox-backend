from sqlalchemy.orm import Session
from pydantic import EmailStr

from src.features.users.schemas import CreateUserData
from src.features.users.utils import create_deactivated_email
from src.features.auth.utils import hash_password
from src.db.models import User


def create_user(db: Session, data: CreateUserData) -> User:
    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        email=data.email,
        password=hash_password(data.password),
        image_reference=None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: EmailStr) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_active_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()


def set_user_archive_value(db: Session, user: User, value: bool) -> User:
    user.is_archived = value
    db.commit()
    db.refresh(user)
    return user


def save_user(db: Session, user: User) -> User:
    db.commit()
    return user


def set_user_image_reference(db: Session, user: User, image_reference: str) -> None:
    user.image_reference = image_reference
    db.commit()


def deactivate_account(db: Session, user: User) -> None:
    user.is_active = False
    user.is_archived = True
    user.email = create_deactivated_email(user.id, user.email)
    db.commit()
