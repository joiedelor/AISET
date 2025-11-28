"""
User Activity Logging Service
DO-178C Traceability: REQ-BE-028 (Comprehensive user activity logging)

This service tracks all user actions for audit, compliance, and analytics.

Logged Activities:
- Authentication (login, logout, token refresh)
- Data modifications (create, update, delete)
- File operations (upload, download, export)
- Process transitions (phase changes, approvals)
- Configuration changes
- Search queries
- Report generation
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class ActivityType:
    """Activity type constants."""
    # Authentication
    LOGIN = "auth.login"
    LOGOUT = "auth.logout"
    TOKEN_REFRESH = "auth.token_refresh"
    PASSWORD_CHANGE = "auth.password_change"

    # Data operations
    CREATE = "data.create"
    UPDATE = "data.update"
    DELETE = "data.delete"
    BULK_UPDATE = "data.bulk_update"
    BULK_DELETE = "data.bulk_delete"

    # File operations
    UPLOAD = "file.upload"
    DOWNLOAD = "file.download"
    EXPORT = "file.export"
    IMPORT = "file.import"

    # Process operations
    PHASE_TRANSITION = "process.phase_transition"
    ACTIVITY_COMPLETE = "process.activity_complete"
    APPROVAL_REQUEST = "process.approval_request"
    APPROVAL_DECISION = "process.approval_decision"

    # Configuration
    CONFIG_CHANGE = "config.change"
    PERMISSION_CHANGE = "config.permission_change"

    # Search and reporting
    SEARCH = "query.search"
    REPORT_GENERATE = "report.generate"

    # AI interactions
    AI_QUERY = "ai.query"
    AI_APPROVAL = "ai.approval"


class ActivityLoggingService:
    """
    Service for comprehensive user activity logging.

    Tracks all significant user actions with full context for
    audit trail and compliance reporting.
    """

    def __init__(self, db: Session):
        """
        Initialize activity logging service.

        Args:
            db: Database session
        """
        self.db = db

    def log_activity(
        self,
        user_id: int,
        activity_type: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Log a user activity.

        Args:
            user_id: User performing the action
            activity_type: Type of activity (use ActivityType constants)
            entity_type: Type of entity affected (e.g., 'requirement', 'project')
            entity_id: ID of affected entity
            details: Additional context data
            ip_address: User's IP address
            user_agent: User's browser/client
            project_id: Related project ID

        Returns:
            Logged activity record
        """
        activity_log = {
            "id": self._generate_log_id(),
            "user_id": user_id,
            "activity_type": activity_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": json.dumps(details) if details else None,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "project_id": project_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        # In production, this would insert into user_activity_log table
        logger.info(f"Activity logged: {activity_type} by user {user_id} on {entity_type}:{entity_id}")

        return activity_log

    def log_authentication(
        self,
        user_id: int,
        action: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None
    ):
        """
        Log authentication activity.

        Args:
            user_id: User ID
            action: Authentication action (login, logout, etc.)
            success: Whether authentication succeeded
            ip_address: IP address
            user_agent: User agent string
            failure_reason: Reason for failure if applicable
        """
        activity_type = getattr(ActivityType, action.upper(), ActivityType.LOGIN)

        details = {
            "success": success,
            "failure_reason": failure_reason
        }

        return self.log_activity(
            user_id=user_id,
            activity_type=activity_type,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )

    def log_data_change(
        self,
        user_id: int,
        operation: str,
        entity_type: str,
        entity_id: int,
        changes: Optional[Dict[str, Any]] = None,
        project_id: Optional[int] = None
    ):
        """
        Log data modification.

        Args:
            user_id: User making the change
            operation: Type of operation (create, update, delete)
            entity_type: Type of entity
            entity_id: Entity ID
            changes: Dictionary of changed fields (old_value -> new_value)
            project_id: Related project
        """
        activity_type = getattr(ActivityType, operation.upper(), ActivityType.UPDATE)

        details = {
            "operation": operation,
            "changes": changes
        }

        return self.log_activity(
            user_id=user_id,
            activity_type=activity_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            project_id=project_id
        )

    def log_file_operation(
        self,
        user_id: int,
        operation: str,
        filename: str,
        file_size: Optional[int] = None,
        file_type: Optional[str] = None,
        project_id: Optional[int] = None
    ):
        """
        Log file operation.

        Args:
            user_id: User performing operation
            operation: Type of operation (upload, download, export)
            filename: Name of file
            file_size: Size in bytes
            file_type: MIME type
            project_id: Related project
        """
        activity_type = getattr(ActivityType, operation.upper(), ActivityType.DOWNLOAD)

        details = {
            "filename": filename,
            "file_size": file_size,
            "file_type": file_type
        }

        return self.log_activity(
            user_id=user_id,
            activity_type=activity_type,
            details=details,
            project_id=project_id
        )

    def log_process_transition(
        self,
        user_id: int,
        ci_id: int,
        from_phase: str,
        to_phase: str,
        project_id: int
    ):
        """
        Log process phase transition.

        Args:
            user_id: User initiating transition
            ci_id: Configuration item ID
            from_phase: Source phase
            to_phase: Target phase
            project_id: Project ID
        """
        details = {
            "from_phase": from_phase,
            "to_phase": to_phase,
            "ci_id": ci_id
        }

        return self.log_activity(
            user_id=user_id,
            activity_type=ActivityType.PHASE_TRANSITION,
            entity_type="configuration_item",
            entity_id=ci_id,
            details=details,
            project_id=project_id
        )

    def log_search(
        self,
        user_id: int,
        search_query: str,
        search_type: str,
        results_count: int,
        project_id: Optional[int] = None
    ):
        """
        Log search activity.

        Args:
            user_id: User performing search
            search_query: Search query string
            search_type: Type of search (global, requirements, etc.)
            results_count: Number of results returned
            project_id: Project context if applicable
        """
        details = {
            "query": search_query,
            "search_type": search_type,
            "results_count": results_count
        }

        return self.log_activity(
            user_id=user_id,
            activity_type=ActivityType.SEARCH,
            details=details,
            project_id=project_id
        )

    def get_user_activity(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0,
        activity_types: Optional[list] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list:
        """
        Get user activity logs.

        Args:
            user_id: User ID
            limit: Maximum number of records
            offset: Pagination offset
            activity_types: Filter by activity types
            start_date: Start date filter
            end_date: End date filter

        Returns:
            List of activity logs
        """
        # In production, query from user_activity_log table
        # For now, return empty list
        logger.debug(f"Fetching activity for user {user_id}")
        return []

    def get_entity_history(
        self,
        entity_type: str,
        entity_id: int,
        limit: int = 50
    ) -> list:
        """
        Get complete history of changes to an entity.

        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            limit: Maximum records

        Returns:
            List of activity logs for the entity
        """
        logger.debug(f"Fetching history for {entity_type}:{entity_id}")
        return []

    def get_project_activity(
        self,
        project_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> list:
        """
        Get all activity for a project.

        Args:
            project_id: Project ID
            limit: Maximum records
            offset: Pagination offset

        Returns:
            List of activity logs for the project
        """
        logger.debug(f"Fetching activity for project {project_id}")
        return []

    def _generate_log_id(self) -> str:
        """Generate unique log ID."""
        import uuid
        return f"LOG-{uuid.uuid4().hex[:12].upper()}"


def get_activity_logger(db: Session) -> ActivityLoggingService:
    """
    Get activity logging service instance.

    Args:
        db: Database session

    Returns:
        ActivityLoggingService instance
    """
    return ActivityLoggingService(db)
