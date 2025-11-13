"""
Requirement Model
DO-178C Traceability: REQ-DB-MODEL-003
Purpose: Store system requirements with full attributes

Requirements are the foundation of the traceability system,
linking to design components and test cases.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database.connection import Base


class RequirementType(str, enum.Enum):
    """Requirement types per IEEE 29148."""
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    INTERFACE = "interface"
    SAFETY = "safety"
    SECURITY = "security"
    OPERATIONAL = "operational"
    DESIGN_CONSTRAINT = "design_constraint"
    DATA = "data"


class RequirementPriority(str, enum.Enum):
    """Requirement priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RequirementStatus(str, enum.Enum):
    """Requirement lifecycle status."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    REJECTED = "rejected"
    OBSOLETE = "obsolete"


class Requirement(Base):
    """
    Requirement model with DO-178C compliance attributes.

    Traceability:
    - REQ-REQ-001: Requirements management
    - REQ-TRACE-001: Bidirectional traceability
    - REQ-VALID-001: Validation workflow
    """

    __tablename__ = "requirements"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Requirement Identification
    requirement_id = Column(String(100), nullable=False, unique=True, index=True)  # e.g., "REQ-SYS-001"
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)

    # Classification
    type = Column(SQLEnum(RequirementType), nullable=False)
    priority = Column(SQLEnum(RequirementPriority), default=RequirementPriority.MEDIUM)
    status = Column(SQLEnum(RequirementStatus), default=RequirementStatus.DRAFT)

    # Hierarchy (for requirement decomposition)
    parent_id = Column(Integer, ForeignKey("requirements.id", ondelete="SET NULL"), nullable=True)

    # AI Extraction Metadata
    confidence_score = Column(Float, default=1.0)  # AI confidence (0.0 to 1.0)
    extraction_source = Column(String(50))  # 'manual', 'ai_claude', 'ai_mistral'

    # Validation
    rationale = Column(Text)  # Why this requirement exists
    acceptance_criteria = Column(Text)  # How to verify this requirement

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255))
    approved_by = Column(String(255))
    approved_at = Column(DateTime(timezone=True))

    # Relationships
    project = relationship("Project", back_populates="requirements")
    parent = relationship("Requirement", remote_side=[id], backref="children")
    design_traces = relationship("RequirementDesignTrace", back_populates="requirement", cascade="all, delete-orphan")
    test_traces = relationship("RequirementTestTrace", back_populates="requirement", cascade="all, delete-orphan")
    version_history = relationship("VersionHistory", back_populates="requirement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Requirement(id='{self.requirement_id}', title='{self.title[:50]}')>"
