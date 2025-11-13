"""
AI Conversation Models
DO-178C Traceability: REQ-DB-MODEL-006
Purpose: Store AI conversation history and messages

AI conversations capture the requirements elicitation process
with full audit trail for certification purposes.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database.connection import Base


class ConversationStatus(str, enum.Enum):
    """Conversation lifecycle status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class MessageRole(str, enum.Enum):
    """Message sender role."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AIConversation(Base):
    """
    AI conversation model for requirements elicitation sessions.

    Traceability:
    - REQ-AI-001: AI conversation management
    - REQ-AUDIT-004: AI interaction audit trail
    """

    __tablename__ = "ai_conversations"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # Conversation Metadata
    title = Column(String(500))
    purpose = Column(String(255))  # 'requirements_elicitation', 'design_discussion', etc.
    status = Column(SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE)

    # AI Service Used
    ai_service = Column(String(50))  # 'claude', 'lmstudio'
    model_name = Column(String(100))  # e.g., 'claude-3-sonnet-20240229'

    # Session Context
    context = Column(JSON, default={})  # Flexible context storage

    # Metadata
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    created_by = Column(String(255))

    # Relationships
    project = relationship("Project", back_populates="ai_conversations")
    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="AIMessage.created_at")
    extracted_entities = relationship("AIExtractedEntity", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AIConversation(id={self.id}, title='{self.title}', status='{self.status}')>"


class AIMessage(Base):
    """
    Individual message within an AI conversation.

    Traceability:
    - REQ-AI-002: Message logging
    - REQ-AUDIT-005: Complete conversation audit trail
    """

    __tablename__ = "ai_messages"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False, index=True)

    # Message Content
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)

    # Metadata
    tokens_used = Column(Integer)  # Token count for cost tracking
    model_version = Column(String(100))  # Model version at time of message
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("AIConversation", back_populates="messages")

    def __repr__(self):
        return f"<AIMessage(id={self.id}, role='{self.role}', content='{self.content[:50]}...')>"
