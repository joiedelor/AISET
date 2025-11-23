"""
Configuration Item Model
DO-178C Traceability: REQ-DB-037, REQ-DB-038, REQ-DB-039
Purpose: Hierarchical product structure and BOM management

This model implements:
- REQ-AI-038: Product Structure Extraction
- REQ-AI-039: Configuration Item Data Extraction
- REQ-AI-040: CI Classification
- REQ-DB-037: Store hierarchical product structure
- REQ-DB-038: Store CI metadata (34+ fields)
- REQ-DB-039: Store BOM relationships
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
import enum

from database.connection import Base


class CIType(enum.Enum):
    """Configuration Item Types."""
    SYSTEM = "system"
    SUBSYSTEM = "subsystem"
    COMPONENT = "component"
    SOFTWARE = "software"
    HARDWARE = "hardware"
    DOCUMENT = "document"
    INTERFACE = "interface"
    COTS = "cots"  # Commercial Off-The-Shelf
    NDI = "ndi"    # Non-Developmental Item
    OTHER = "other"


class CILifecyclePhase(enum.Enum):
    """CI Lifecycle Phases."""
    CONCEPT = "concept"
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    DEPLOYMENT = "deployment"
    OPERATION = "operation"
    MAINTENANCE = "maintenance"
    RETIREMENT = "retirement"


class CIControlLevel(enum.Enum):
    """CI Control Levels (criticality-based)."""
    LEVEL_1 = "level_1"  # Highest control
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"
    LEVEL_4 = "level_4"  # Lowest control


class CIStatus(enum.Enum):
    """CI Status."""
    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    RELEASED = "released"
    OBSOLETE = "obsolete"


class BOMType(enum.Enum):
    """Bill of Materials Types."""
    ENGINEERING = "engineering"      # Design BOM
    MANUFACTURING = "manufacturing"  # Production BOM
    SERVICE = "service"              # Maintenance BOM
    AS_BUILT = "as_built"            # Actual configuration
    AS_DESIGNED = "as_designed"      # Intended configuration


class ConfigurationItem(Base):
    """
    Configuration Item model for product structure.

    Traceability:
    - REQ-DB-037: Hierarchical product structure
    - REQ-DB-038: CI metadata (34+ fields)
    - REQ-AI-038: Product Structure Extraction
    - REQ-AI-039: CI Data Extraction
    - REQ-AI-040: CI Classification
    """
    __tablename__ = "configuration_items"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    guid = Column(String(36), unique=True, nullable=False, index=True)
    ci_identifier = Column(String(100), nullable=False, index=True)  # e.g., "SYS-001", "HW-CTRL-001"

    # Project association
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Hierarchy (self-referential)
    parent_id = Column(Integer, ForeignKey("configuration_items.id"), nullable=True)
    level = Column(Integer, default=0)  # Depth in hierarchy (0 = root)
    path = Column(String(500))  # Materialized path for efficient queries (e.g., "1.3.5")

    # Basic Information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    ci_type = Column(Enum(CIType), default=CIType.COMPONENT)

    # Part/Version Information
    part_number = Column(String(100))
    revision = Column(String(50))
    version = Column(String(50))
    serial_number = Column(String(100))

    # Lifecycle and Status
    lifecycle_phase = Column(Enum(CILifecyclePhase), default=CILifecyclePhase.DEVELOPMENT)
    control_level = Column(Enum(CIControlLevel), default=CIControlLevel.LEVEL_3)
    status = Column(Enum(CIStatus), default=CIStatus.DRAFT)

    # Classification
    criticality = Column(String(50))  # DAL A/B/C/D/E for software
    safety_classification = Column(String(50))
    security_classification = Column(String(50))

    # Supplier/Source
    supplier = Column(String(255))
    supplier_part_number = Column(String(100))
    manufacturer = Column(String(255))

    # Physical Characteristics (for hardware)
    weight = Column(Float)
    weight_unit = Column(String(20), default="kg")
    dimensions = Column(String(100))  # "LxWxH"

    # Documentation
    specification_document = Column(String(255))
    drawing_number = Column(String(100))

    # Compliance
    certification_basis = Column(String(255))
    qualification_status = Column(String(100))

    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))
    updated_by = Column(String(100))

    # AI extraction metadata
    ai_extracted = Column(Boolean, default=False)
    ai_confidence = Column(Float)
    extraction_source = Column(Text)  # Source document/conversation

    # Notes and comments
    notes = Column(Text)

    # Relationships
    project = relationship("Project", back_populates="configuration_items")
    parent = relationship("ConfigurationItem", remote_side=[id], back_populates="children")
    children = relationship("ConfigurationItem", back_populates="parent", cascade="all, delete-orphan")

    # BOM relationships
    bom_parent_entries = relationship("BillOfMaterials", foreign_keys="BillOfMaterials.parent_ci_id", back_populates="parent_ci")
    bom_child_entries = relationship("BillOfMaterials", foreign_keys="BillOfMaterials.child_ci_id", back_populates="child_ci")

    def __repr__(self):
        return f"<ConfigurationItem(id={self.id}, ci_identifier='{self.ci_identifier}', name='{self.name}')>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "guid": self.guid,
            "ci_identifier": self.ci_identifier,
            "project_id": self.project_id,
            "parent_id": self.parent_id,
            "level": self.level,
            "path": self.path,
            "name": self.name,
            "description": self.description,
            "ci_type": self.ci_type.value if self.ci_type else None,
            "part_number": self.part_number,
            "revision": self.revision,
            "version": self.version,
            "lifecycle_phase": self.lifecycle_phase.value if self.lifecycle_phase else None,
            "control_level": self.control_level.value if self.control_level else None,
            "status": self.status.value if self.status else None,
            "criticality": self.criticality,
            "supplier": self.supplier,
            "ai_extracted": self.ai_extracted,
            "ai_confidence": self.ai_confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "children_count": len(self.children) if self.children else 0
        }


class BillOfMaterials(Base):
    """
    Bill of Materials relationship model.

    Traceability:
    - REQ-DB-039: Store BOM relationships
    - REQ-FE-011: BOM Editor support
    - REQ-BE-013: BOM management
    """
    __tablename__ = "bill_of_materials"

    id = Column(Integer, primary_key=True, index=True)

    # Parent-Child relationship
    parent_ci_id = Column(Integer, ForeignKey("configuration_items.id"), nullable=False)
    child_ci_id = Column(Integer, ForeignKey("configuration_items.id"), nullable=False)

    # BOM metadata
    bom_type = Column(Enum(BOMType), default=BOMType.ENGINEERING)
    quantity = Column(Float, default=1.0)
    unit_of_measure = Column(String(50), default="each")
    position_reference = Column(String(100))  # Position in assembly

    # Find number (BOM line item reference)
    find_number = Column(String(50))

    # Effectivity
    effectivity_start = Column(DateTime)
    effectivity_end = Column(DateTime)
    serial_effectivity = Column(String(255))  # Serial number range

    # Substitution
    is_alternate = Column(Boolean, default=False)
    alternate_group = Column(String(50))

    # Notes
    notes = Column(Text)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))

    # Relationships
    parent_ci = relationship("ConfigurationItem", foreign_keys=[parent_ci_id], back_populates="bom_parent_entries")
    child_ci = relationship("ConfigurationItem", foreign_keys=[child_ci_id], back_populates="bom_child_entries")

    def __repr__(self):
        return f"<BillOfMaterials(parent={self.parent_ci_id}, child={self.child_ci_id}, qty={self.quantity})>"

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "parent_ci_id": self.parent_ci_id,
            "child_ci_id": self.child_ci_id,
            "bom_type": self.bom_type.value if self.bom_type else None,
            "quantity": self.quantity,
            "unit_of_measure": self.unit_of_measure,
            "position_reference": self.position_reference,
            "find_number": self.find_number,
            "is_alternate": self.is_alternate,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "parent_ci": self.parent_ci.to_dict() if self.parent_ci else None,
            "child_ci": self.child_ci.to_dict() if self.child_ci else None
        }
