"""
Design Component Model
DO-178C Traceability: REQ-DB-MODEL-004
Purpose: Store system architecture and design elements

Design components represent the software architecture that implements
the system requirements.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database.connection import Base


class ComponentType(str, enum.Enum):
    """Design component types."""
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    INTERFACE = "interface"
    DATABASE = "database"
    API = "api"
    SERVICE = "service"
    COMPONENT = "component"


class DesignStatus(str, enum.Enum):
    """Design component status."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    REVIEWED = "reviewed"
    VERIFIED = "verified"
    DEPRECATED = "deprecated"


class DesignComponent(Base):
    """
    Design component model for software architecture.

    Traceability:
    - REQ-DESIGN-001: Design documentation
    - REQ-TRACE-002: Requirements to design traceability
    - REQ-ARCH-001: Architecture management
    """

    __tablename__ = "design_components"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Component Identification
    component_id = Column(String(100), nullable=False, unique=True, index=True)  # e.g., "COMP-AI-001"
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Classification
    type = Column(SQLEnum(ComponentType), nullable=False)
    status = Column(SQLEnum(DesignStatus), default=DesignStatus.PLANNED)

    # Hierarchy (for architectural decomposition)
    parent_id = Column(Integer, ForeignKey("design_components.id", ondelete="SET NULL"), nullable=True)

    # Design Details
    implementation_notes = Column(Text)  # How it's implemented
    interfaces = Column(Text)  # Interface specifications
    dependencies = Column(Text)  # Dependencies on other components

    # Code References
    file_path = Column(String(500))  # Path to implementation file
    line_number = Column(Integer)  # Starting line number

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255))
    reviewed_by = Column(String(255))
    reviewed_at = Column(DateTime(timezone=True))

    # Relationships
    project = relationship("Project", back_populates="design_components")
    parent = relationship("DesignComponent", remote_side=[id], backref="children")
    requirement_traces = relationship("RequirementDesignTrace", back_populates="design_component", cascade="all, delete-orphan")
    test_traces = relationship("DesignTestTrace", back_populates="design_component", cascade="all, delete-orphan")
    version_history = relationship("VersionHistory", back_populates="design_component", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DesignComponent(id='{self.component_id}', name='{self.name}')>"
