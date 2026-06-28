from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import settings

database_url = settings.DATABASE_URL

engine = create_engine(database_url, echo=True)
# engine = create_engine( - HILJEM
#     database_url,
#     pool_size=5,
#     max_overflow=0,
#     pool_pre_ping=True,
#     echo=False,  # turn off in production
# )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
