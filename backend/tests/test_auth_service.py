"""
Authentication Service Tests
DO-178C Traceability: REQ-BE-003, REQ-BE-004
Purpose: Verify JWT authentication and user management
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from services.auth_service import (
    AuthService,
    auth_service,
    Token,
    TokenData,
    UserCreate,
    UserLogin,
    UserResponse
)
from models.user import User, UserRole


class TestPasswordHashing:
    """Test password hashing functionality."""

    def test_password_hash_is_different_from_plain(self):
        """REQ-BE-003: Passwords must be hashed, not stored in plain text."""
        password = "test_password_123"
        hashed = auth_service.get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are long

    def test_verify_correct_password(self):
        """REQ-BE-003: Correct password should verify successfully."""
        password = "correct_password"
        hashed = auth_service.get_password_hash(password)

        assert auth_service.verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        """REQ-BE-003: Wrong password should fail verification."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = auth_service.get_password_hash(password)

        assert auth_service.verify_password(wrong_password, hashed) is False


class TestJWTTokens:
    """Test JWT token generation and validation."""

    def test_create_access_token(self):
        """REQ-BE-004: JWT tokens should be created successfully."""
        data = {"sub": "1", "username": "testuser", "role": "viewer"}
        token = auth_service.create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50

    def test_verify_valid_token(self):
        """REQ-BE-004: Valid JWT tokens should be verified successfully."""
        data = {"sub": "1", "username": "testuser", "role": "viewer"}
        token = auth_service.create_access_token(data)

        token_data = auth_service.verify_token(token)

        assert token_data is not None
        assert token_data.user_id == 1
        assert token_data.username == "testuser"
        assert token_data.role == "viewer"

    def test_verify_invalid_token(self):
        """REQ-BE-004: Invalid JWT tokens should fail verification."""
        invalid_token = "invalid.token.here"
        token_data = auth_service.verify_token(invalid_token)

        assert token_data is None

    def test_token_expiration(self):
        """REQ-BE-004: Expired tokens should fail verification."""
        data = {"sub": "1", "username": "testuser", "role": "viewer"}
        # Create token with negative expiration (already expired)
        token = auth_service.create_access_token(
            data,
            expires_delta=timedelta(seconds=-1)
        )

        token_data = auth_service.verify_token(token)
        assert token_data is None

    def test_token_contains_user_data(self):
        """REQ-BE-004: Token should contain user identification data."""
        user_id = 42
        username = "john_doe"
        role = "engineer"

        token = auth_service.create_access_token({
            "sub": str(user_id),
            "username": username,
            "role": role
        })

        token_data = auth_service.verify_token(token)

        assert token_data.user_id == user_id
        assert token_data.username == username
        assert token_data.role == role


class TestUserAuthentication:
    """Test user authentication functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AuthService()

    def test_authenticate_valid_user(self):
        """REQ-BE-003: Valid credentials should authenticate user."""
        # Create mock user
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.hashed_password = self.service.get_password_hash("password123")
        mock_user.is_active = True
        mock_user.role = UserRole.VIEWER

        # Mock database session
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Authenticate
        user = self.service.authenticate_user(mock_db, "testuser", "password123")

        assert user is not None
        assert user.username == "testuser"

    def test_authenticate_wrong_password(self):
        """REQ-BE-003: Wrong password should fail authentication."""
        # Create mock user
        mock_user = MagicMock(spec=User)
        mock_user.username = "testuser"
        mock_user.hashed_password = self.service.get_password_hash("correct_password")
        mock_user.is_active = True

        # Mock database session
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Authenticate with wrong password
        user = self.service.authenticate_user(mock_db, "testuser", "wrong_password")

        assert user is None

    def test_authenticate_nonexistent_user(self):
        """REQ-BE-003: Nonexistent user should fail authentication."""
        # Mock database session with no user found
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Authenticate
        user = self.service.authenticate_user(mock_db, "nonexistent", "password")

        assert user is None

    def test_authenticate_inactive_user(self):
        """REQ-BE-003: Inactive user should fail authentication."""
        # Create mock inactive user
        mock_user = MagicMock(spec=User)
        mock_user.username = "testuser"
        mock_user.hashed_password = self.service.get_password_hash("password123")
        mock_user.is_active = False

        # Mock database session
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Authenticate
        user = self.service.authenticate_user(mock_db, "testuser", "password123")

        assert user is None


class TestUserCreation:
    """Test user creation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AuthService()

    def test_create_user_success(self):
        """REQ-BE-003: New user should be created successfully."""
        # Mock database session
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Create user data
        user_data = UserCreate(
            username="newuser",
            email="newuser@example.com",
            password="password123",
            full_name="New User"
        )

        # Mock the add and commit operations
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        # Create user
        user = self.service.create_user(mock_db, user_data)

        # Verify database operations were called
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_create_user_duplicate_username(self):
        """REQ-BE-003: Duplicate username should raise error."""
        # Mock existing user
        mock_existing = MagicMock(spec=User)

        # Mock database session
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_existing

        # Create user data
        user_data = UserCreate(
            username="existinguser",
            email="new@example.com",
            password="password123"
        )

        # Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            self.service.create_user(mock_db, user_data)

        assert "already exists" in str(exc_info.value)


class TestLoginFlow:
    """Test complete login flow."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AuthService()

    def test_login_returns_token(self):
        """REQ-BE-003, REQ-BE-004: Successful login should return JWT token."""
        # Create mock user
        mock_user = MagicMock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.hashed_password = self.service.get_password_hash("password123")
        mock_user.is_active = True
        mock_user.role = UserRole.ENGINEER

        # Mock database session
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        # Login
        login_data = UserLogin(username="testuser", password="password123")
        token = self.service.login(mock_db, login_data)

        assert token is not None
        assert token.access_token is not None
        assert token.token_type == "bearer"
        assert token.expires_in > 0

    def test_login_invalid_credentials_returns_none(self):
        """REQ-BE-003: Invalid login should return None."""
        # Mock database session with no user found
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Login
        login_data = UserLogin(username="nonexistent", password="password")
        token = self.service.login(mock_db, login_data)

        assert token is None


# Run tests with: pytest backend/tests/test_auth_service.py -v
