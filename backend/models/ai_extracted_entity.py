"""
AI Extracted Entity Model
DO-178C Traceability: REQ-DB-MODEL-007
Purpose: Store AI-extracted entities pending validation

AI extracts requirements, design components, and tests from conversations.
These entities must be validated by humans before database insertion.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database.connection import Base


class EntityType(str, enum.Enum):
    """Type of extracted entity."""
    REQUIREMENT = "requirement"
    DESIGN_COMPONENT = "design_component"
    TEST_CASE = "test_case"


class ValidationStatus(str, enum.Enum):
    """Validation workflow status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"  # Approved with modifications


class AIExtractedEntity(Base):
    """
    AI-extracted entity awaiting human validation.

    Traceability:
    - REQ-AI-003: AI extraction tracking
    - REQ-VALID-002: Human-in-the-loop validation
    - REQ-AUDIT-006: Extraction audit trail
    """

    __tablename__ = "ai_extracted_entities"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False, index=True)

    # Entity Classification
    entity_type = Column(SQLEnum(EntityType), nullable=False)
    validation_status = Column(SQLEnum(ValidationStatus), default=ValidationStatus.PENDING)

    # Extracted Data (JSON for flexibility)
    extracted_data = Column(JSON, nullable=False)  # Contains all extracted fields

    # AI Metadata
    confidence_score = Column(Float, default=0.0)  # AI confidence (0.0 to 1.0)
    extraction_method = Column(String(100))  # e.g., 'structured_parsing', 'nlp_extraction'

    # Source Context
    source_message_id = Column(Integer, ForeignKey("ai_messages.id", ondelete="SET NULL"))
    source_text = Column(Text)  # Original text that was extracted from

    # Validation
    validated_by = Column(String(255))
    validated_at = Column(DateTime(timezone=True))
    validation_notes = Column(Text)  # Reviewer comments

    # If approved, reference to created entity
    created_requirement_id = Column(Integer, ForeignKey("requirements.id", ondelete="SET NULL"))
    created_design_id = Column(Integer, ForeignKey("design_components.id", ondelete="SET NULL"))
    created_test_id = Column(Integer, ForeignKey("test_cases.id", ondelete="SET NULL"))

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    conversation = relationship("AIConversation", back_populates="extracted_entities")

    def __repr__(self):
        return f"<AIExtractedEntity(id={self.id}, type='{self.entity_type}', status='{self.validation_status}')>"
