from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from los_classificados.config import Config


class Base(DeclarativeBase):
    pass


def create_db_engine():
    engine = create_engine(
        Config.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=10,
        max_overflow=20,
        echo=Config.DEBUG,
    )
    return engine


try:
    engine = create_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    DB_AVAILABLE = True
except Exception:
    engine = None
    SessionLocal = None
    DB_AVAILABLE = False


def get_db():
    """Dependency-style DB session context manager."""
    if not DB_AVAILABLE or SessionLocal is None:
        raise RuntimeError("Database not configured.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they don't exist."""
    if engine is not None:
        from los_classificados.db import models  # noqa: F401  triggers model registration
        Base.metadata.create_all(bind=engine)
