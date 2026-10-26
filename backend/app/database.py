"""Database configuration and session management for VoiceMenu AI."""

import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Configure SQLite engine with multi-threading support
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Provide a transactional database session dependency.

    Yields:
        Session: SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all database tables and seed initial data if database is empty."""
    from app.models import MenuItem, Restaurant  # noqa: F401
    from app.seed_menu import seed_database

    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        seed_database(db)
    logger.info("Database initialization and seed verification complete.")
