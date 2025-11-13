"""
Requirements Service Tests
DO-178C Traceability: REQ-TEST-001
Purpose: Unit tests for requirements service
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from services.requirements_service import RequirementsService
from models.requirement import Requirement, RequirementType, RequirementPriority

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def requirements_service(db_session):
    """Create a requirements service instance."""
    return RequirementsService(db_session)


def test_create_requirement(requirements_service, db_session):
    """
    Test requirement creation.

    Traceability: REQ-REQ-003
    """
    # Create a project first
    from models.project import Project
    project = Project(
        name="Test Project",
        project_code="TEST-001",
        certification_level="C",
        created_by="test_user"
    )
    db_session.add(project)
    db_session.commit()

    # Create requirement
    requirement = requirements_service.create_requirement(
        project_id=project.id,
        requirement_id="REQ-TEST-001",
        title="Test Requirement",
        description="This is a test requirement for unit testing",
        req_type=RequirementType.FUNCTIONAL,
        priority=RequirementPriority.HIGH,
        created_by="test_user"
    )

    assert requirement.id is not None
    assert requirement.requirement_id == "REQ-TEST-001"
    assert requirement.title == "Test Requirement"
    assert requirement.type == RequirementType.FUNCTIONAL
    assert requirement.priority == RequirementPriority.HIGH


def test_validate_requirement(requirements_service, db_session):
    """
    Test requirement validation.

    Traceability: REQ-VALID-005
    """
    from models.project import Project
    project = Project(
        name="Test Project",
        project_code="TEST-001",
        certification_level="C",
        created_by="test_user"
    )
    db_session.add(project)
    db_session.commit()

    # Create a good requirement
    good_req = requirements_service.create_requirement(
        project_id=project.id,
        requirement_id="REQ-GOOD-001",
        title="Well-formed requirement title",
        description="The system shall provide user authentication capability",
        req_type=RequirementType.SECURITY,
        priority=RequirementPriority.CRITICAL,
        acceptance_criteria="User cannot access system without valid credentials",
        rationale="Security requirement per company policy",
        created_by="test_user"
    )

    validation = requirements_service.validate_requirement(good_req)

    assert validation["is_valid"] is True
    assert len(validation["issues"]) == 0
    assert validation["quality_score"] >= 0.9

    # Create a poor requirement
    poor_req = requirements_service.create_requirement(
        project_id=project.id,
        requirement_id="REQ-POOR-001",
        title="Bad req",  # Too short
        description="System might do something",  # Ambiguous word "might"
        req_type=RequirementType.FUNCTIONAL,
        created_by="test_user"
    )

    validation = requirements_service.validate_requirement(poor_req)

    assert validation["is_valid"] is False
    assert len(validation["issues"]) > 0
    assert len(validation["warnings"]) > 0
    assert "Title too short" in validation["issues"]


def test_approve_requirement(requirements_service, db_session):
    """
    Test requirement approval.

    Traceability: REQ-APPROVAL-002
    """
    from models.project import Project
    project = Project(
        name="Test Project",
        project_code="TEST-001",
        certification_level="C",
        created_by="test_user"
    )
    db_session.add(project)
    db_session.commit()

    requirement = requirements_service.create_requirement(
        project_id=project.id,
        requirement_id="REQ-APPROVE-001",
        title="Requirement to be approved",
        description="This requirement will be approved in the test",
        req_type=RequirementType.FUNCTIONAL,
        created_by="test_user"
    )

    # Approve the requirement
    from models.requirement import RequirementStatus
    approved_req = requirements_service.approve_requirement(
        requirement_id=requirement.id,
        approved_by="approver_user",
        rationale="Meets all acceptance criteria"
    )

    assert approved_req.status == RequirementStatus.APPROVED
    assert approved_req.approved_by == "approver_user"
    assert approved_req.approved_at is not None


def test_get_requirements_by_project(requirements_service, db_session):
    """
    Test retrieving requirements by project.

    Traceability: REQ-REQ-005
    """
    from models.project import Project
    project = Project(
        name="Test Project",
        project_code="TEST-001",
        certification_level="C",
        created_by="test_user"
    )
    db_session.add(project)
    db_session.commit()

    # Create multiple requirements
    for i in range(5):
        requirements_service.create_requirement(
            project_id=project.id,
            requirement_id=f"REQ-LIST-{i:03d}",
            title=f"Requirement {i}",
            description=f"Description for requirement {i}",
            req_type=RequirementType.FUNCTIONAL,
            created_by="test_user"
        )

    # Retrieve all requirements
    all_reqs = requirements_service.get_requirements_by_project(project.id)

    assert len(all_reqs) == 5

    # Filter by type
    functional_reqs = requirements_service.get_requirements_by_project(
        project.id,
        req_type=RequirementType.FUNCTIONAL
    )

    assert len(functional_reqs) == 5
