"""
User Model
DO-178C Traceability: REQ-DB-MODEL-008
Purpose: Store user accounts and authentication information

Users are tracked for audit trail and accountability in
the certification process.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from database.connection import Base


class UserRole(str, enum.Enum):
    """User roles for access control."""
    ADMIN = "admin"
    ENGINEER = "engineer"
    REVIEWER = "reviewer"
    AUDITOR = "auditor"
    VIEWER = "viewer"


class User(Base):
    """
    User model for authentication and authorization.

    Traceability:
    - REQ-AUTH-001: User authentication
    - REQ-RBAC-001: Role-based access control
    - REQ-AUDIT-007: User activity tracking
    """

    __tablename__ = "users"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # User Information
    full_name = Column(String(255))
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER)

    # Account Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
