from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Query, Session
from pydantic import EmailStr

from src.core.logger import logger
from src.constants import DEFAULT_SORT, SortOrder, SortType, UserRoles
from src.features.users.schemas import CreateUserData
from src.features.users.utils import create_deactivated_email
from src.features.auth.utils import hash_password
from src.db.models import User
from src.features.users.helper import USER_SORT_HELPER


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
    logger.info(f"Created new user: {user}, id={user.id}.")
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
    logger.info(f"User {user.id} archive set to {value}.")
    return user


def save_user(db: Session, user: User) -> User:
    db.commit()
    logger.info(f"User {user} data updated successfully.")
    return user


def set_user_image_reference(db: Session, user: User, image_reference: str) -> None:
    user.image_reference = image_reference
    db.commit()
    logger.info(f"New image reference is set for {user}")


def deactivate_account(db: Session, user: User) -> None:
    user.is_active = False
    user.is_archived = True
    user.email = create_deactivated_email(user.id, user.email)
    logger.info(f"User {user.id} account is removed.")
    db.commit()


def _active_users_query(db: Session, name_filter: str | None, role: UserRoles | None) -> Query:
    query = db.query(User).filter(User.is_active.is_(True))
    if role:
        query = query.filter(User.role == role)
    if name_filter:
        pattern = f"%{name_filter.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')}%"
        query = query.filter(or_(User.first_name.ilike(pattern, escape="\\"), User.last_name.ilike(pattern, escape="\\")))
    return query


def count_filtered_users(db: Session, name_filter: str | None, role: UserRoles | None) -> int:
    return _active_users_query(db, name_filter, role).count()


def get_filtered_users(
    db: Session, name_filter: str | None, role: UserRoles | None, size: int, page: int,
    sort_by: SortType | None = None, sort_order: SortOrder | None = None,
) -> list[User]:

    query = _active_users_query(db, name_filter, role)
    query = _apply_sorting(query, sort_by, sort_order)
    return query.offset((page - 1) * size).limit(size).all()


def _apply_sorting(query: Query, sort_by: SortType | None, sort_order: SortOrder | None) -> Query:
    """Order by ``sort_by`` (default ``created_at``). With no sort params at all, newest users come first."""
    column = USER_SORT_HELPER.get(sort_by, DEFAULT_SORT.value)
    if not sort_by and not sort_order:
        sort_order = SortOrder.DESC
    
    direction = asc if sort_order is not None and sort_order == SortOrder.ASC else desc

    return query.order_by(direction(column), User.id)
