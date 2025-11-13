"""
Audit and Compliance Models
DO-178C Traceability: REQ-DB-MODEL-010
Purpose: Store complete audit trail for certification

All changes to critical entities must be tracked with full
audit trail for DO-178C compliance.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database.connection import Base


class ChangeType(str, enum.Enum):
    """Type of change made."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"


class ChangeRequestStatus(str, enum.Enum):
    """Change request workflow status."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    CANCELLED = "cancelled"


class ImpactLevel(str, enum.Enum):
    """Impact level of a change."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    TRIVIAL = "trivial"


class VersionHistory(Base):
    """
    Complete version history for all critical entities.

    Traceability:
    - REQ-AUDIT-008: Complete change tracking
    - REQ-CERT-003: Audit trail for certification
    - REQ-VERSION-001: Version control
    """

    __tablename__ = "version_history"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Entity References (one of these will be set)
    requirement_id = Column(Integer, ForeignKey("requirements.id", ondelete="CASCADE"))
    design_component_id = Column(Integer, ForeignKey("design_components.id", ondelete="CASCADE"))
    test_case_id = Column(Integer, ForeignKey("test_cases.id", ondelete="CASCADE"))

    # Change Information
    change_type = Column(SQLEnum(ChangeType), nullable=False)
    entity_type = Column(String(50), nullable=False)  # 'requirement', 'design', 'test'
    version_number = Column(Integer, nullable=False)  # Incremental version

    # Change Details
    previous_data = Column(JSON)  # Snapshot before change
    new_data = Column(JSON)  # Snapshot after change
    change_summary = Column(Text)  # Human-readable summary
    change_rationale = Column(Text)  # Why the change was made

    # Metadata
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    changed_by = Column(String(255), nullable=False)

    # Relationships
    requirement = relationship("Requirement", back_populates="version_history")
    design_component = relationship("DesignComponent", back_populates="version_history")
    test_case = relationship("TestCase", back_populates="version_history")

    def __repr__(self):
        return f"<VersionHistory(id={self.id}, type='{self.entity_type}', version={self.version_number})>"


class ChangeRequest(Base):
    """
    Change request and impact analysis tracking.

    Traceability:
    - REQ-CHANGE-001: Change request management
    - REQ-IMPACT-001: Impact analysis
    - REQ-APPROVAL-001: Approval workflow
    """

    __tablename__ = "change_requests"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Request Identification
    cr_id = Column(String(100), nullable=False, unique=True, index=True)  # e.g., "CR-2024-001"
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)

    # Status and Priority
    status = Column(SQLEnum(ChangeRequestStatus), default=ChangeRequestStatus.DRAFT)
    impact_level = Column(SQLEnum(ImpactLevel), nullable=False)

    # Impact Analysis
    affected_requirements = Column(JSON, default=[])  # List of requirement IDs
    affected_design = Column(JSON, default=[])  # List of design component IDs
    affected_tests = Column(JSON, default=[])  # List of test case IDs
    impact_analysis = Column(Text)  # Detailed impact assessment

    # Justification
    business_justification = Column(Text)
    technical_justification = Column(Text)
    risk_assessment = Column(Text)

    # Approval
    approved_by = Column(String(255))
    approved_at = Column(DateTime(timezone=True))
    rejection_reason = Column(Text)

    # Implementation
    implemented_by = Column(String(255))
    implemented_at = Column(DateTime(timezone=True))
    implementation_notes = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(255), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="change_requests")

    def __repr__(self):
        return f"<ChangeRequest(id='{self.cr_id}', title='{self.title[:50]}', status='{self.status}')>"


class ValidationDecision(Base):
    """
    Human validation decisions for AI-extracted entities.

    Traceability:
    - REQ-VALID-003: Validation decision tracking
    - REQ-HITL-001: Human-in-the-loop audit trail
    """

    __tablename__ = "validation_decisions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    extracted_entity_id = Column(Integer, ForeignKey("ai_extracted_entities.id", ondelete="CASCADE"), nullable=False, index=True)

    # Decision
    decision = Column(String(50), nullable=False)  # 'approved', 'rejected', 'modified'
    decision_rationale = Column(Text, nullable=False)

    # Modifications (if decision='modified')
    original_data = Column(JSON)
    modified_data = Column(JSON)
    modification_notes = Column(Text)

    # Metadata
    decided_at = Column(DateTime(timezone=True), server_default=func.now())
    decided_by = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<ValidationDecision(id={self.id}, decision='{self.decision}', by='{self.decided_by}')>"
