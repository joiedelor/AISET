"""
Traceability Service Tests
DO-178C Traceability: REQ-TEST-002
Purpose: Unit tests for traceability service
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from services.traceability_service import TraceabilityService
from models.requirement import RequirementType, RequirementPriority

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
def traceability_service(db_session):
    """Create a traceability service instance."""
    return TraceabilityService(db_session)


@pytest.fixture
def sample_data(db_session):
    """Create sample project, requirement, design, and test data."""
    from models.project import Project
    from models.requirement import Requirement
    from models.design_component import DesignComponent, ComponentType
    from models.test_case import TestCase, TestType

    # Create project
    project = Project(
        name="Test Project",
        project_code="TEST-001",
        certification_level="C",
        created_by="test_user"
    )
    db_session.add(project)
    db_session.commit()

    # Create requirement
    requirement = Requirement(
        project_id=project.id,
        requirement_id="REQ-TRACE-001",
        title="Test Requirement",
        description="Requirement for traceability testing",
        type=RequirementType.FUNCTIONAL,
        priority=RequirementPriority.HIGH,
        created_by="test_user"
    )
    db_session.add(requirement)

    # Create design component
    design = DesignComponent(
        project_id=project.id,
        component_id="COMP-TEST-001",
        name="Test Component",
        description="Design component for testing",
        type=ComponentType.MODULE,
        created_by="test_user"
    )
    db_session.add(design)

    # Create test case
    test = TestCase(
        project_id=project.id,
        test_id="TEST-CASE-001",
        title="Test Case",
        description="Test case for traceability",
        type=TestType.UNIT,
        created_by="test_user"
    )
    db_session.add(test)

    db_session.commit()

    return {
        "project": project,
        "requirement": requirement,
        "design": design,
        "test": test
    }


def test_create_requirement_design_trace(traceability_service, sample_data):
    """
    Test creating requirement-design trace link.

    Traceability: REQ-TRACE-009
    """
    trace = traceability_service.create_requirement_design_trace(
        requirement_id=sample_data["requirement"].id,
        design_component_id=sample_data["design"].id,
        rationale="Design implements the requirement",
        created_by="test_user"
    )

    assert trace.id is not None
    assert trace.requirement_id == sample_data["requirement"].id
    assert trace.design_component_id == sample_data["design"].id
    assert trace.rationale == "Design implements the requirement"


def test_create_requirement_test_trace(traceability_service, sample_data):
    """
    Test creating requirement-test trace link.

    Traceability: REQ-TRACE-010
    """
    trace = traceability_service.create_requirement_test_trace(
        requirement_id=sample_data["requirement"].id,
        test_case_id=sample_data["test"].id,
        coverage_notes="Test verifies the requirement",
        created_by="test_user"
    )

    assert trace.id is not None
    assert trace.requirement_id == sample_data["requirement"].id
    assert trace.test_case_id == sample_data["test"].id


def test_get_requirement_coverage(traceability_service, sample_data):
    """
    Test getting requirement coverage analysis.

    Traceability: REQ-TRACE-012
    """
    # Create traces
    traceability_service.create_requirement_design_trace(
        requirement_id=sample_data["requirement"].id,
        design_component_id=sample_data["design"].id,
        created_by="test_user"
    )

    traceability_service.create_requirement_test_trace(
        requirement_id=sample_data["requirement"].id,
        test_case_id=sample_data["test"].id,
        created_by="test_user"
    )

    # Get coverage
    coverage = traceability_service.get_requirement_coverage(sample_data["requirement"].id)

    assert coverage["has_design_coverage"] is True
    assert coverage["design_count"] == 1
    assert coverage["has_test_coverage"] is True
    assert coverage["test_count"] == 1
    assert coverage["is_fully_traced"] is True


def test_detect_gaps(traceability_service, db_session, sample_data):
    """
    Test traceability gap detection.

    Traceability: REQ-TRACE-013
    """
    # Create a requirement without traces
    from models.requirement import Requirement
    orphan_req = Requirement(
        project_id=sample_data["project"].id,
        requirement_id="REQ-ORPHAN-001",
        title="Orphan Requirement",
        description="Requirement without design or tests",
        type=RequirementType.FUNCTIONAL,
        priority=RequirementPriority.CRITICAL,
        created_by="test_user"
    )
    db_session.add(orphan_req)
    db_session.commit()

    # Detect gaps
    gaps = traceability_service.detect_gaps(sample_data["project"].id)

    # Should find at least 2 gaps (missing design and missing test for orphan_req)
    assert len(gaps) >= 2

    # Check gap types
    gap_types = [gap.gap_type.value for gap in gaps]
    assert "missing_design" in gap_types
    assert "missing_test" in gap_types


def test_generate_traceability_matrix(traceability_service, sample_data):
    """
    Test traceability matrix generation.

    Traceability: REQ-TRACE-014
    """
    # Create traces
    traceability_service.create_requirement_design_trace(
        requirement_id=sample_data["requirement"].id,
        design_component_id=sample_data["design"].id,
        created_by="test_user"
    )

    traceability_service.create_requirement_test_trace(
        requirement_id=sample_data["requirement"].id,
        test_case_id=sample_data["test"].id,
        created_by="test_user"
    )

    # Generate matrix
    matrix = traceability_service.generate_traceability_matrix(sample_data["project"].id)

    assert "matrix" in matrix
    assert "statistics" in matrix
    assert matrix["statistics"]["total_requirements"] >= 1
    assert matrix["statistics"]["fully_traced"] >= 1
    assert matrix["statistics"]["coverage_percentage"] > 0
