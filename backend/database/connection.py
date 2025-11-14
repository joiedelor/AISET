"""
Database Connection Management
DO-178C Traceability: REQ-DB-001
Purpose: Manage PostgreSQL database connections with SQLAlchemy

This module provides database session management and connection pooling
for the AISET application with proper error handling and audit logging.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator
import logging

from config.settings import settings

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=10,
    max_overflow=20,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """
    Event listener for new database connections.

    Traceability: REQ-AUDIT-002 - Connection audit logging
    """
    if settings.enable_audit_trail:
        logger.info(f"New database connection established: {connection_record}")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Traceability:
    - REQ-DB-002: Session management
    - REQ-SEC-002: Proper resource cleanup

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.

    Traceability: REQ-DB-003 - Database initialization

    Note:
        In production, use Alembic migrations instead of this function.
        This is primarily for development and testing.
    """
    # Import all models to register them with Base
    import models  # noqa: F401

    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def drop_db() -> None:
    """
    Drop all database tables.

    Traceability: REQ-DB-004 - Database cleanup

    Warning:
        This is a destructive operation. Use only in development/testing.
    """
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Database tables dropped successfully")
