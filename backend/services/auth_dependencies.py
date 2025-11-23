"""
Authentication Dependencies
DO-178C Traceability: REQ-BE-003, REQ-BE-004
Purpose: FastAPI dependencies for authentication and authorization

These dependencies implement:
- REQ-BE-003: API authentication enforcement
- REQ-BE-004: JWT token validation
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database.connection import get_db
from models.user import User, UserRole
from services.auth_service import auth_service, TokenData

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.

    Traceability: REQ-BE-003 - API Authentication

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        The authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    token_data = auth_service.verify_token(token)

    if token_data is None or token_data.user_id is None:
        raise credentials_exception

    user = auth_service.get_user_by_id(db, token_data.user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the current user if authenticated, None otherwise.

    Use this for endpoints that work with or without authentication.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        The authenticated user or None
    """
    if not token:
        return None

    token_data = auth_service.verify_token(token)

    if token_data is None or token_data.user_id is None:
        return None

    user = auth_service.get_user_by_id(db, token_data.user_id)

    if user is None or not user.is_active:
        return None

    return user


def require_role(required_roles: list[UserRole]):
    """
    Dependency factory for role-based access control.

    Traceability: REQ-RBAC-001 - Role-based access control

    Args:
        required_roles: List of roles that are allowed

    Returns:
        Dependency function that checks user role
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {[r.value for r in required_roles]}"
            )
        return current_user

    return role_checker


# Pre-configured role dependencies
require_admin = require_role([UserRole.ADMIN])
require_engineer = require_role([UserRole.ADMIN, UserRole.ENGINEER])
require_reviewer = require_role([UserRole.ADMIN, UserRole.ENGINEER, UserRole.REVIEWER])
require_auditor = require_role([UserRole.ADMIN, UserRole.AUDITOR])
