"""
Authentication Router
DO-178C Traceability: REQ-BE-003, REQ-BE-004
Purpose: Authentication endpoints for login, register, and token management

This router implements:
- REQ-BE-003: API authentication endpoints
- REQ-BE-004: JWT token generation and refresh
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from database.connection import get_db
from models.user import User
from services.auth_service import (
    auth_service,
    Token,
    UserCreate,
    UserLogin,
    UserResponse
)
from services.auth_dependencies import get_current_user, get_current_user_optional

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.

    Traceability: REQ-BE-003 - User registration

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user information

    Raises:
        HTTPException: If username or email already exists
    """
    try:
        user = auth_service.create_user(db, user_data)
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login=user.last_login
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.

    Traceability: REQ-BE-003, REQ-BE-004 - User login with JWT

    Args:
        login_data: Login credentials
        db: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
    token = auth_service.login(db, login_data)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return token


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token endpoint.

    Traceability: REQ-BE-004 - OAuth2 token endpoint

    Args:
        form_data: OAuth2 form data (username, password)
        db: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
    login_data = UserLogin(username=form_data.username, password=form_data.password)
    token = auth_service.login(db, login_data)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return token


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.

    Traceability: REQ-BE-003 - User profile endpoint

    Args:
        current_user: Current authenticated user

    Returns:
        Current user information
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Refresh the JWT access token.

    Traceability: REQ-BE-004 - Token refresh

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        New JWT access token
    """
    access_token = auth_service.create_access_token(
        data={
            "sub": str(current_user.id),
            "username": current_user.username,
            "role": current_user.role.value
        }
    )

    from config.settings import settings

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout endpoint (client-side token invalidation).

    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the token. This endpoint exists for API completeness.

    Args:
        current_user: Current authenticated user

    Returns:
        Logout confirmation
    """
    return {
        "message": "Successfully logged out",
        "detail": "Please remove the token from client storage"
    }


@router.get("/verify")
async def verify_token(
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Verify if the current token is valid.

    Traceability: REQ-BE-004 - Token verification

    Args:
        current_user: Current user if token is valid

    Returns:
        Token validity status
    """
    if current_user:
        return {
            "valid": True,
            "user_id": current_user.id,
            "username": current_user.username,
            "role": current_user.role.value
        }
    else:
        return {
            "valid": False,
            "user_id": None,
            "username": None,
            "role": None
        }
