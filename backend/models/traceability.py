"""
Traceability Models
DO-178C Traceability: REQ-DB-MODEL-009
Purpose: Store bidirectional traceability links

Traceability is critical for DO-178C compliance, ensuring all
requirements are implemented and verified.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database.connection import Base


class TraceType(str, enum.Enum):
    """Type of traceability link."""
    MANUAL = "manual"  # Manually created by user
    AI_SUGGESTED = "ai_suggested"  # Suggested by AI
    AUTO_DETECTED = "auto_detected"  # Automatically detected


class GapType(str, enum.Enum):
    """Type of traceability gap."""
    MISSING_DESIGN = "missing_design"  # Requirement without design
    MISSING_TEST = "missing_test"  # Requirement without test
    ORPHAN_DESIGN = "orphan_design"  # Design without requirement
    ORPHAN_TEST = "orphan_test"  # Test without requirement
    INCOMPLETE_COVERAGE = "incomplete_coverage"  # Partial coverage


class RequirementDesignTrace(Base):
    """
    Traceability link between requirements and design components.

    Traceability:
    - REQ-TRACE-004: Requirements to design traceability
    - REQ-CERT-002: DO-178C traceability matrix
    """

    __tablename__ = "requirements_design_trace"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    requirement_id = Column(Integer, ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False, index=True)
    design_component_id = Column(Integer, ForeignKey("design_components.id", ondelete="CASCADE"), nullable=False, index=True)

    # Trace Metadata
    trace_type = Column(SQLEnum(TraceType), default=TraceType.MANUAL)
    confidence_score = Column(Float, default=1.0)  # For AI-suggested traces
    rationale = Column(Text)  # Why this link exists

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(255))
    verified_by = Column(String(255))
    verified_at = Column(DateTime(timezone=True))

    # Relationships
    requirement = relationship("Requirement", back_populates="design_traces")
    design_component = relationship("DesignComponent", back_populates="requirement_traces")

    def __repr__(self):
        return f"<RequirementDesignTrace(req_id={self.requirement_id}, design_id={self.design_component_id})>"


class RequirementTestTrace(Base):
    """
    Traceability link between requirements and test cases.

    Traceability:
    - REQ-TRACE-005: Requirements to tests traceability
    - REQ-VV-002: Verification coverage tracking
    """

    __tablename__ = "requirements_test_trace"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    requirement_id = Column(Integer, ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False, index=True)

    # Trace Metadata
    trace_type = Column(SQLEnum(TraceType), default=TraceType.MANUAL)
    confidence_score = Column(Float, default=1.0)
    coverage_notes = Column(Text)  # How the test verifies the requirement

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(255))
    verified_by = Column(String(255))
    verified_at = Column(DateTime(timezone=True))

    # Relationships
    requirement = relationship("Requirement", back_populates="test_traces")
    test_case = relationship("TestCase", back_populates="requirement_traces")

    def __repr__(self):
        return f"<RequirementTestTrace(req_id={self.requirement_id}, test_id={self.test_case_id})>"


class DesignTestTrace(Base):
    """
    Traceability link between design components and test cases.

    Traceability:
    - REQ-TRACE-006: Design to tests traceability
    - REQ-VV-003: Unit/integration test coverage
    """

    __tablename__ = "design_test_trace"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    design_component_id = Column(Integer, ForeignKey("design_components.id", ondelete="CASCADE"), nullable=False, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False, index=True)

    # Trace Metadata
    trace_type = Column(SQLEnum(TraceType), default=TraceType.MANUAL)
    confidence_score = Column(Float, default=1.0)
    test_notes = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(255))

    # Relationships
    design_component = relationship("DesignComponent", back_populates="test_traces")
    test_case = relationship("TestCase", back_populates="design_traces")

    def __repr__(self):
        return f"<DesignTestTrace(design_id={self.design_component_id}, test_id={self.test_case_id})>"


class TraceabilityGap(Base):
    """
    Detected gaps in traceability coverage.

    Traceability:
    - REQ-TRACE-007: Gap detection
    - REQ-QA-001: Quality assurance tracking
    """

    __tablename__ = "traceability_gaps"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Gap Information
    gap_type = Column(SQLEnum(GapType), nullable=False)
    severity = Column(String(50), default="medium")  # critical, high, medium, low
    description = Column(Text, nullable=False)

    # References to affected entities
    requirement_id = Column(Integer, ForeignKey("requirements.id", ondelete="CASCADE"))
    design_component_id = Column(Integer, ForeignKey("design_components.id", ondelete="CASCADE"))
    test_case_id = Column(Integer, ForeignKey("test_cases.id", ondelete="CASCADE"))

    # Resolution
    is_resolved = Column(Boolean, default=False)
    resolution_notes = Column(Text)
    resolved_by = Column(String(255))
    resolved_at = Column(DateTime(timezone=True))

    # Metadata
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    detection_method = Column(String(100))  # 'automated_scan', 'manual_review'

    def __repr__(self):
        return f"<TraceabilityGap(id={self.id}, type='{self.gap_type}', severity='{self.severity}')>"
