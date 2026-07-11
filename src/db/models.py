from src.constants import UserRoles
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from src.db.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token = Column(String, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    image_reference = Column(String, nullable=True)
    role = Column(Enum(UserRoles, name='userroles'), default=UserRoles.USER, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
