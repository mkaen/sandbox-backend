from src.constants import UserRoles
from sqlalchemy import BigInteger, Boolean, Column, Float, ForeignKey, Integer, String, DateTime, Enum, Uuid
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
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    image_reference = Column(Uuid, nullable=True)
    is_archived = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    role = Column(Enum(UserRoles, name='userroles'), default=UserRoles.USER, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"


class CryptoAsset(Base):
    __tablename__ = "crypto_assets"

    id = Column(Integer, primary_key=True, nullable=False)
    symbol = Column(String, nullable=False, unique=True, index=True)
    updated_at = Column(DateTime, nullable=False)
    currency = Column(String, nullable=False, unique=True)
    price_usd = Column(Float, nullable=False)
    market_cap = Column(BigInteger, nullable=False)
    market_cap_rank = Column(Integer, nullable=False)
    ath_change = Column(Float, nullable=False)
    change_24h = Column(Float, nullable=False)
    image_thumb = Column(String, nullable=False, unique=True)
    image_small = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)


    def __repr__(self) -> str:
        return self.currency.title()
