from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import settings

database_url = settings.DATABASE_URL

engine = create_engine(
    database_url,
    echo=settings.DB_ECHO,
    pool_pre_ping=settings.POOL_PRE_PING,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
