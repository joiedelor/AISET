"""
Activity-Interview Linking Service
DO-178C Traceability: REQ-SM-003, REQ-IS-001

This service connects process activities with interview scripts,
enabling activities to trigger specific interviews for data collection.

Key Features:
- Link activities to interview scripts
- Retrieve interview for a given activity
- Track interview completion for activities
- Auto-populate activity completion data from interview results
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
import logging

from process_engine import InterviewScriptExecutor, create_interview
from services.configuration_item_service import ConfigurationItemService

logger = logging.getLogger(__name__)


class ActivityInterviewService:
    """
    Service for linking activities with interviews.

    This enables the Process Engine to automatically trigger appropriate
    interviews when an activity requires data collection.
    """

    # Map activity types to interview scripts
    # This can be extended or moved to database for dynamic configuration
    ACTIVITY_TO_INTERVIEW_MAP = {
        # Project initialization activities
        "PROJECT_INITIALIZATION": "project_initialization",

        # Requirements activities
        "REQUIREMENTS_ELICITATION": "requirements_gathering",
        "REQUIREMENTS_ANALYSIS": "requirements_review",

        # Design activities
        "ARCHITECTURE_DESIGN": "architecture_review",
        "DESIGN_REVIEW": "design_review",

        # Implementation activities
        "CODE_REVIEW": "code_review",

        # Test activities
        "TEST_PLANNING": "test_planning",
        "TEST_REVIEW": "test_review",

        # Certification activities
        "CERTIFICATION_PLANNING": "certification_planning",
    }

    def __init__(self, db: Session):
        self.db = db
        self.ci_service = ConfigurationItemService(db)

    def get_interview_for_activity(
        self,
        activity_type: str
    ) -> Optional[str]:
        """
        Get the interview script ID for an activity type.

        Args:
            activity_type: The activity type (e.g., "PROJECT_INITIALIZATION")

        Returns:
            Interview script ID or None if no interview linked
        """
        return self.ACTIVITY_TO_INTERVIEW_MAP.get(activity_type)

    def start_interview_for_activity(
        self,
        ci_id: int,
        activity_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Start an interview for a specific activity.

        Args:
            ci_id: Configuration Item ID
            activity_id: Activity ID

        Returns:
            Interview session data or None if no interview available
        """
        # Get current activity
        activity_data = self.ci_service.get_ci_current_activity(ci_id)

        if not activity_data:
            logger.warning(f"No current activity found for CI {ci_id}")
            return None

        current_activity = activity_data.get("activity", {})

        if current_activity.get("activity_id") != activity_id:
            logger.warning(f"Activity {activity_id} is not the current activity for CI {ci_id}")
            return None

        # Get interview script for this activity type
        activity_type = current_activity.get("type")
        script_id = self.get_interview_for_activity(activity_type)

        if not script_id:
            logger.info(f"No interview linked for activity type {activity_type}")
            return None

        # Create interview session
        try:
            interview_state = create_interview(script_id)

            return {
                "ci_id": ci_id,
                "activity_id": activity_id,
                "activity_type": activity_type,
                "script_id": script_id,
                "interview_state": {
                    "script_id": interview_state.script_id,
                    "current_sub_phase": interview_state.current_sub_phase,
                    "current_question_id": interview_state.current_question_id,
                    "started_at": interview_state.started_at.isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Failed to start interview for activity {activity_id}: {str(e)}")
            return None

    def complete_activity_with_interview_data(
        self,
        ci_id: int,
        activity_id: str,
        interview_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Complete an activity using data from interview results.

        Args:
            ci_id: Configuration Item ID
            activity_id: Activity ID
            interview_results: Results from interview execution

        Returns:
            Activity completion result
        """
        # Extract relevant data from interview results
        completion_data = {
            "interview_completed": True,
            "interview_script": interview_results.get("script_id"),
            "data_collected": interview_results.get("answers", {}),
            "artifacts_generated": interview_results.get("artifacts", []),
            "timestamp": interview_results.get("completed_at")
        }

        # Complete the activity with interview data
        result = self.ci_service.complete_activity(
            ci_id=ci_id,
            activity_id=activity_id,
            completion_data=completion_data
        )

        if result:
            logger.info(f"Activity {activity_id} completed with interview data for CI {ci_id}")

        return result

    def get_activity_interview_status(
        self,
        ci_id: int,
        activity_id: str
    ) -> Dict[str, Any]:
        """
        Get the interview status for an activity.

        Returns:
            Status information including whether interview is required,
            available, started, or completed
        """
        activity_data = self.ci_service.get_ci_current_activity(ci_id)

        if not activity_data:
            return {
                "has_interview": False,
                "interview_required": False,
                "interview_available": False
            }

        current_activity = activity_data.get("activity", {})
        activity_type = current_activity.get("type")
        script_id = self.get_interview_for_activity(activity_type)

        return {
            "ci_id": ci_id,
            "activity_id": activity_id,
            "activity_type": activity_type,
            "has_interview": script_id is not None,
            "interview_script": script_id,
            "interview_required": script_id is not None and current_activity.get("required", False),
            "interview_available": script_id is not None
        }

    @staticmethod
    def register_activity_interview_mapping(
        activity_type: str,
        script_id: str
    ) -> None:
        """
        Register a new activity-to-interview mapping.

        This allows dynamic configuration of which interviews
        are triggered by which activities.

        Args:
            activity_type: The activity type
            script_id: The interview script ID
        """
        ActivityInterviewService.ACTIVITY_TO_INTERVIEW_MAP[activity_type] = script_id
        logger.info(f"Registered interview '{script_id}' for activity type '{activity_type}'")

    @staticmethod
    def list_activity_interview_mappings() -> Dict[str, str]:
        """
        List all activity-to-interview mappings.

        Returns:
            Dictionary of activity types to interview script IDs
        """
        return ActivityInterviewService.ACTIVITY_TO_INTERVIEW_MAP.copy()
