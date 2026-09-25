"""
SQLAlchemy engine / session setup with SQLite fallback if MySQL is unavailable.
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

logger = logging.getLogger("medreport")

try:
    if settings.SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        engine = create_engine(
            settings.SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
        )
    else:
        engine = create_engine(
            settings.SQLALCHEMY_DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        # Test connection
        with engine.connect() as conn:
            pass
except Exception as exc:
    logger.warning(
        "Could not connect to MySQL database (%s). Falling back to SQLite database at medreport.db",
        exc,
    )
    engine = create_engine("sqlite:///./medreport.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

