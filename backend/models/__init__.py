"""
AISET Database Models
DO-178C Traceability: REQ-DB-MODEL-001
Purpose: SQLAlchemy ORM models for all database tables

This package contains all database models with complete traceability
to DO-178C requirements and audit trail capabilities.
"""

from .project import Project
from .requirement import Requirement
from .design_component import DesignComponent
from .test_case import TestCase
from .ai_conversation import AIConversation, AIMessage
from .ai_extracted_entity import AIExtractedEntity
from .traceability import (
    RequirementDesignTrace,
    RequirementTestTrace,
    DesignTestTrace,
    TraceabilityGap
)
from .audit import VersionHistory, ChangeRequest, ValidationDecision
from .user import User
from .document_export import DocumentExport
from .configuration_item import (
    ConfigurationItem,
    BillOfMaterials,
    CIType,
    CILifecyclePhase,
    CIControlLevel,
    CIStatus,
    BOMType
)

__all__ = [
    # Core entities
    "Project",
    "Requirement",
    "DesignComponent",
    "TestCase",
    "User",

    # AI entities
    "AIConversation",
    "AIMessage",
    "AIExtractedEntity",

    # Traceability
    "RequirementDesignTrace",
    "RequirementTestTrace",
    "DesignTestTrace",
    "TraceabilityGap",

    # Audit and compliance
    "VersionHistory",
    "ChangeRequest",
    "ValidationDecision",
    "DocumentExport",

    # Configuration Management
    "ConfigurationItem",
    "BillOfMaterials",
    "CIType",
    "CILifecyclePhase",
    "CIControlLevel",
    "CIStatus",
    "BOMType",
]
