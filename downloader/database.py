"""Database connection and session management."""

import os
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

# Read database configuration from environment variables
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", "5432"))
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
DATABASE_NAME = os.getenv("DATABASE_NAME", "downloader")
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA", "public")

# Build database URL
DATABASE_URL = f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using them
)


@event.listens_for(engine, "connect")
def set_search_path(dbapi_conn, connection_record):
    """Set the search path to the configured schema."""
    cursor = dbapi_conn.cursor()
    cursor.execute(f"SET search_path TO {DATABASE_SCHEMA}")
    cursor.close()


# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Session:
    """Get a database session."""
    return SessionLocal()


@contextmanager
def get_session_context():
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
