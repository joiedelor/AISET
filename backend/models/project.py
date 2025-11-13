"""
Project Model
DO-178C Traceability: REQ-DB-MODEL-002
Purpose: Store project metadata and configuration

A project is the top-level container for all requirements, design,
tests, and traceability information.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base


class Project(Base):
    """
    Project model representing a systems engineering project.

    Traceability:
    - REQ-PROJ-001: Project management
    - REQ-CERT-001: Certification level tracking
    - REQ-AUDIT-003: Project-level audit trail
    """

    __tablename__ = "projects"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Project Information
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    project_code = Column(String(50), unique=True, index=True)  # e.g., "AISET-2024-001"

    # DO-178C Certification Level (A, B, C, D, or E)
    certification_level = Column(String(1), default="C")  # A=highest, E=lowest

    # Industry/Domain (aerospace, automotive, medical, etc.)
    industry = Column(String(100))

    # Status (active, archived, completed)
    status = Column(String(50), default="active")

    # Configuration
    configuration = Column(JSON, default={})  # Flexible JSON for project-specific settings

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
