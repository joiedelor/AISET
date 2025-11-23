"""
Authentication Service
DO-178C Traceability: REQ-BE-003, REQ-BE-004
Purpose: JWT token generation, validation, and password hashing

This service implements:
- REQ-BE-003: API authentication for all endpoints
- REQ-BE-004: JWT token-based stateless authentication
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging

from config.settings import settings
from models.user import User, UserRole

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[datetime] = None


class UserCreate(BaseModel):
    """User registration schema."""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema."""
    username: str
    password: str


class UserResponse(BaseModel):
    """User response schema (without password)."""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class AuthService:
    """
    Authentication service for user management and JWT tokens.

    Traceability:
    - REQ-BE-003: API Authentication
    - REQ-BE-004: JWT Token Authentication
    """

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.

        Args:
            plain_password: The plain text password
            hashed_password: The hashed password to compare against

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: The plain text password

        Returns:
            The hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.

        Traceability: REQ-BE-004 - JWT Token Authentication

        Args:
            data: The data to encode in the token
            expires_delta: Optional expiration time delta

        Returns:
            The encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )

        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """
        Verify and decode a JWT token.

        Traceability: REQ-BE-003 - API Authentication

        Args:
            token: The JWT token to verify

        Returns:
            TokenData if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )

            sub = payload.get("sub")
            username: str = payload.get("username")
            role: str = payload.get("role")

            if sub is None:
                return None

            # Handle both string and int sub values
            user_id = int(sub) if isinstance(sub, str) else sub

            return TokenData(
                user_id=user_id,
                username=username,
                role=role,
                exp=datetime.fromtimestamp(payload.get("exp", 0))
            )

        except JWTError as e:
            logger.warning(f"JWT verification failed: {str(e)}")
            return None

    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by username and password.

        Traceability: REQ-BE-003 - API Authentication

        Args:
            db: Database session
            username: The username
            password: The plain text password

        Returns:
            User if authenticated, None otherwise
        """
        user = db.query(User).filter(User.username == username).first()

        if not user:
            logger.warning(f"Authentication failed: user '{username}' not found")
            return None

        if not self.verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: invalid password for user '{username}'")
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: user '{username}' is inactive")
            return None

        return user

    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """
        Create a new user.

        Args:
            db: Database session
            user_data: User registration data

        Returns:
            The created user

        Raises:
            ValueError: If username or email already exists
        """
        # Check if username exists
        if db.query(User).filter(User.username == user_data.username).first():
            raise ValueError(f"Username '{user_data.username}' already exists")

        # Check if email exists
        if db.query(User).filter(User.email == user_data.email).first():
            raise ValueError(f"Email '{user_data.email}' already exists")

        # Create user
        hashed_password = self.get_password_hash(user_data.password)

        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=UserRole.VIEWER,  # Default role
            is_active=True,
            is_verified=False
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"Created new user: {user.username}")
        return user

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get a user by username."""
        return db.query(User).filter(User.username == username).first()

    def update_last_login(self, db: Session, user: User) -> None:
        """Update user's last login timestamp."""
        user.last_login = datetime.utcnow()
        db.commit()

    def login(self, db: Session, login_data: UserLogin) -> Optional[Token]:
        """
        Authenticate user and return JWT token.

        Traceability: REQ-BE-003, REQ-BE-004

        Args:
            db: Database session
            login_data: Login credentials

        Returns:
            Token if successful, None otherwise
        """
        user = self.authenticate_user(db, login_data.username, login_data.password)

        if not user:
            return None

        # Update last login
        self.update_last_login(db, user)

        # Create token (sub must be string per JWT spec)
        access_token = self.create_access_token(
            data={
                "sub": str(user.id),
                "username": user.username,
                "role": user.role.value
            }
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )


# Singleton instance
auth_service = AuthService()
