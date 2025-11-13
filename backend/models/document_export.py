"""
Document Export Model
DO-178C Traceability: REQ-DB-MODEL-011
Purpose: Track generated certification documents

Document exports are tracked for audit purposes and to maintain
a complete record of all generated certification artifacts.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database.connection import Base


class DocumentType(str, enum.Enum):
    """Type of certification document."""
    SRS = "srs"  # Software Requirements Specification
    SDD = "sdd"  # Software Design Description
    RTM = "rtm"  # Requirements Traceability Matrix
    TEST_PLAN = "test_plan"
    TEST_REPORT = "test_report"
    VV_REPORT = "vv_report"  # Verification & Validation Report
    CUSTOM = "custom"


class ExportFormat(str, enum.Enum):
    """Export file format."""
    MARKDOWN = "markdown"
    PDF = "pdf"
    HTML = "html"
    DOCX = "docx"
    JSON = "json"


class DocumentExport(Base):
    """
    Document export tracking for certification artifacts.

    Traceability:
    - REQ-DOC-001: Document generation tracking
    - REQ-CERT-004: Certification artifact management
    - REQ-AUDIT-009: Export audit trail
    """

    __tablename__ = "document_exports"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Document Information
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    export_format = Column(SQLEnum(ExportFormat), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)

    # File Information
    file_path = Column(String(1000), nullable=False)  # Path to generated file
    file_size = Column(Integer)  # Size in bytes
    file_hash = Column(String(64))  # SHA-256 hash for integrity verification

    # Generation Parameters
    template_used = Column(String(255))
    generation_params = Column(JSON, default={})  # Parameters used for generation

    # Content Filters (what was included)
    included_requirements = Column(JSON, default=[])  # List of requirement IDs
    included_design = Column(JSON, default=[])  # List of design component IDs
    included_tests = Column(JSON, default=[])  # List of test case IDs

    # Metadata
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    generated_by = Column(String(255), nullable=False)
    version = Column(String(50))  # Document version

    # Certification Metadata
    is_official = Column(Boolean, default=False)  # Official certification artifact
    certification_notes = Column(Text)

    # Relationships
    project = relationship("Project", back_populates="document_exports")

    def __repr__(self):
        return f"<DocumentExport(id={self.id}, type='{self.document_type}', format='{self.export_format}')>"
