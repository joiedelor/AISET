"""
Test Case Model
DO-178C Traceability: REQ-DB-MODEL-005
Purpose: Store verification and validation test cases

Test cases verify that requirements are correctly implemented
in the design components.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database.connection import Base


class TestType(str, enum.Enum):
    """Test case types per DO-178C."""
    UNIT = "unit"
    INTEGRATION = "integration"
    SYSTEM = "system"
    ACCEPTANCE = "acceptance"
    REGRESSION = "regression"
    PERFORMANCE = "performance"
    SECURITY = "security"


class TestStatus(str, enum.Enum):
    """Test execution status."""
    NOT_RUN = "not_run"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class TestCase(Base):
    """
    Test case model for verification and validation.

    Traceability:
    - REQ-TEST-001: Test case management
    - REQ-TRACE-003: Requirements to tests traceability
    - REQ-VV-001: Verification and validation
    """

    __tablename__ = "test_cases"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Test Identification
    test_id = Column(String(100), nullable=False, unique=True, index=True)  # e.g., "TEST-UNIT-001"
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)

    # Classification
    type = Column(SQLEnum(TestType), nullable=False)
    status = Column(SQLEnum(TestStatus), default=TestStatus.NOT_RUN)

    # Test Details
    preconditions = Column(Text)  # Setup requirements
    test_steps = Column(Text)  # Detailed test procedure
    expected_result = Column(Text)  # Expected outcome
    actual_result = Column(Text)  # Actual outcome (after execution)

    # Test Data
    test_data = Column(Text)  # Test inputs and data sets

    # Automation
    is_automated = Column(Boolean, default=False)
    automation_script = Column(String(500))  # Path to automated test script

    # Execution
    last_run_at = Column(DateTime(timezone=True))
    last_run_by = Column(String(255))
    execution_notes = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255))

    # Relationships
    project = relationship("Project", back_populates="test_cases")
    requirement_traces = relationship("RequirementTestTrace", back_populates="test_case", cascade="all, delete-orphan")
    design_traces = relationship("DesignTestTrace", back_populates="test_case", cascade="all, delete-orphan")
    version_history = relationship("VersionHistory", back_populates="test_case", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestCase(id='{self.test_id}', title='{self.title[:50]}')>"
