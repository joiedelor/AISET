"""
Pytest Configuration and Fixtures
DO-178C Traceability: REQ-TEST-001 (Test Infrastructure)

This module provides common fixtures for all tests, including:
- Database session management
- Test database setup/teardown
- Common test data
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from database.connection import Base
from models.project import Project, CIStateMachine
from models.configuration_item import ConfigurationItem, BillOfMaterials
from services.configuration_item_service import ConfigurationItemService


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db(engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def test_project(db: Session):
    """Create a test project."""
    project = Project(
        name="Test Project",
        project_code="TEST-001",
        safety_critical=True,
        dal_level="DAL_B",
        domain="aerospace",
        status="active",
        created_by="test_user"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@pytest.fixture
def ci_service(db: Session):
    """Create a CI service instance."""
    return ConfigurationItemService(db)
