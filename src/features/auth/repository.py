from datetime import datetime

from sqlalchemy.orm import Session

from src.db.models import RefreshToken


def create_refresh_token(db: Session, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
    refresh_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return refresh_token


def get_refresh_token(db: Session, token: str) -> RefreshToken | None:
    return db.query(RefreshToken).filter(RefreshToken.token == token).first()


def revoke_refresh_token(db: Session, token: str) -> None:
    refresh_token = get_refresh_token(db, token)
    if refresh_token:
        refresh_token.revoked = True
        db.commit()
