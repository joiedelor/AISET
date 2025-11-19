"""
Project Model
DO-178C Traceability: REQ-DB-MODEL-002, REQ-AI-037
Purpose: Store project metadata and configuration including initialization context

A project is the top-level container for all requirements, design,
tests, and traceability information.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
from typing import Optional
from pydantic import BaseModel


class ProjectInitializationContext(BaseModel):
    """
    Pydantic model for project initialization interview data.

    Traceability:
    - REQ-AI-032: Structured project interview
    - REQ-AI-033: Safety criticality determination
    - REQ-AI-034: Regulatory standards identification
    - REQ-AI-035: Development process selection
    - REQ-AI-037: Context storage
    """
    # Foundation Questions (REQ-AI-033)
    safety_critical: bool
    dal_level: Optional[str] = None  # A, B, C, D, N/A
    sil_level: Optional[str] = None  # ASIL-A/B/C/D, SIL-1/2/3/4, N/A
    domain: Optional[str] = None  # aerospace, automotive, medical, industrial
    product_type: Optional[str] = None

    # Planning Questions (REQ-AI-034, REQ-AI-035)
    regulatory_standards: list[str] = []  # DO-178C, DO-254, ISO 26262, etc.
    development_process: Optional[str] = None  # V-model, iterative, agile-compliant
    architecture_type: Optional[str] = None
    requirements_source: Optional[str] = None

    # Execution Questions
    lifecycle_phase: Optional[str] = None
    verification_approach: Optional[str] = None
    team_size: Optional[int] = None

    # Additional context
    initialization_complete: bool = False
    interview_stage: str = "foundation"  # foundation, planning, execution, complete


class Project(Base):
    """
    Project model representing a systems engineering project.

    Traceability:
    - REQ-PROJ-001: Project management
    - REQ-CERT-001: Certification level tracking
    - REQ-AUDIT-003: Project-level audit trail
    - REQ-AI-037: Project context storage
    """

    __tablename__ = "projects"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Project Information
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    project_code = Column(String(50), unique=True, index=True)  # e.g., "AISET-2024-001"

    # Safety & Certification (REQ-AI-033, REQ-AI-034)
    safety_critical = Column(Boolean, default=False)
    dal_level = Column(String(10))  # DO-178C: A, B, C, D, N/A
    sil_level = Column(String(10))  # ISO 26262/IEC 61508: ASIL-A/B/C/D, SIL-1/2/3/4, N/A

    # Legacy field (deprecated in favor of dal_level/sil_level)
    certification_level = Column(String(1), default="C")  # A=highest, E=lowest

    # Domain & Type (REQ-AI-032, REQ-AI-035)
    industry = Column(String(100))  # Alias for domain
    domain = Column(String(50))  # aerospace, automotive, medical, industrial
    product_type = Column(String(100))
    architecture_type = Column(String(100))
    requirements_source = Column(String(100))

    # Status (active, archived, completed)
    status = Column(String(50), default="active")

    # Configuration & Context (REQ-AI-036, REQ-AI-037)
    configuration = Column(JSON, default={})  # Flexible JSON for project-specific settings
    initialization_context = Column(JSON, default={})  # Stores ProjectInitializationContext

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255))  # User ID or name

    # Relationships
    requirements = relationship("Requirement", back_populates="project", cascade="all, delete-orphan")
    design_components = relationship("DesignComponent", back_populates="project", cascade="all, delete-orphan")
    test_cases = relationship("TestCase", back_populates="project", cascade="all, delete-orphan")
    ai_conversations = relationship("AIConversation", back_populates="project", cascade="all, delete-orphan")
    change_requests = relationship("ChangeRequest", back_populates="project", cascade="all, delete-orphan")
    document_exports = relationship("DocumentExport", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', code='{self.project_code}')>"
