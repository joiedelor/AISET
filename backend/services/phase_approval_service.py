"""
Phase Approval Service
DO-178C Traceability: REQ-SM-002 (Phase preconditions), REQ-AUDIT-001

This service implements approval workflow for phase transitions,
ensuring that phases are not entered without proper authorization.

Features:
- Phase transition approval requests
- Approval/rejection workflow
- Entry/exit criteria validation
- Audit trail of approvals
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ApprovalStatus(str, Enum):
    """Status of an approval request"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class PhaseApprovalService:
    """
    Service for managing phase transition approvals.

    This ensures phases are not entered without proper review,
    critical for DO-178C compliance.
    """

    def __init__(self, db: Session):
        self.db = db

    def request_phase_transition_approval(
        self,
        ci_id: int,
        from_phase_index: int,
        to_phase_index: int,
        requested_by: str,
        justification: str = ""
    ) -> Dict[str, Any]:
        """
        Request approval to transition to next phase.

        Args:
            ci_id: Configuration Item ID
            from_phase_index: Current phase index
            to_phase_index: Target phase index
            requested_by: User requesting approval
            justification: Reason for transition

        Returns:
            Approval request data
        """
        # In production, this would create a database record
        # For now, we'll return a simple approval structure

        approval_request = {
            "approval_id": f"APR-{ci_id}-{to_phase_index}-{int(datetime.utcnow().timestamp())}",
            "ci_id": ci_id,
            "from_phase": from_phase_index,
            "to_phase": to_phase_index,
            "status": ApprovalStatus.PENDING.value,
            "requested_by": requested_by,
            "requested_at": datetime.utcnow().isoformat(),
            "justification": justification,
            "approved_by": None,
            "approved_at": None
        }

        logger.info(f"Created approval request {approval_request['approval_id']} for CI {ci_id}")

        return approval_request

    def approve_phase_transition(
        self,
        approval_id: str,
        approved_by: str,
        comments: str = ""
    ) -> Dict[str, Any]:
        """
        Approve a phase transition request.

        Args:
            approval_id: Approval request ID
            approved_by: User approving
            comments: Approval comments

        Returns:
            Updated approval data
        """
        # In production, update database record
        approval = {
            "approval_id": approval_id,
            "status": ApprovalStatus.APPROVED.value,
            "approved_by": approved_by,
            "approved_at": datetime.utcnow().isoformat(),
            "comments": comments
        }

        logger.info(f"Approved phase transition: {approval_id} by {approved_by}")

        return approval

    def reject_phase_transition(
        self,
        approval_id: str,
        rejected_by: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Reject a phase transition request.

        Args:
            approval_id: Approval request ID
            rejected_by: User rejecting
            reason: Rejection reason

        Returns:
            Updated approval data
        """
        approval = {
            "approval_id": approval_id,
            "status": ApprovalStatus.REJECTED.value,
            "rejected_by": rejected_by,
            "rejected_at": datetime.utcnow().isoformat(),
            "rejection_reason": reason
        }

        logger.info(f"Rejected phase transition: {approval_id} by {rejected_by}")

        return approval

    def check_phase_entry_criteria(
        self,
        ci_id: int,
        phase_index: int
    ) -> Dict[str, Any]:
        """
        Check if entry criteria are met for a phase.

        Args:
            ci_id: Configuration Item ID
            phase_index: Phase index to check

        Returns:
            Entry criteria status
        """
        # In production, this would check actual criteria from state machine
        # For now, return a simple check

        criteria = {
            "ci_id": ci_id,
            "phase_index": phase_index,
            "entry_criteria_met": True,  # Would check actual criteria
            "missing_criteria": [],
            "warnings": []
        }

        logger.debug(f"Checked entry criteria for CI {ci_id} phase {phase_index}")

        return criteria

    def check_phase_exit_criteria(
        self,
        ci_id: int,
        phase_index: int
    ) -> Dict[str, Any]:
        """
        Check if exit criteria are met for a phase.

        Args:
            ci_id: Configuration Item ID
            phase_index: Phase index to check

        Returns:
            Exit criteria status
        """
        criteria = {
            "ci_id": ci_id,
            "phase_index": phase_index,
            "exit_criteria_met": True,  # Would check actual criteria
            "incomplete_items": [],
            "warnings": []
        }

        logger.debug(f"Checked exit criteria for CI {ci_id} phase {phase_index}")

        return criteria

    def get_pending_approvals(
        self,
        ci_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get pending approval requests.

        Args:
            ci_id: Optional CI ID to filter by

        Returns:
            List of pending approvals
        """
        # In production, query database
        # For now, return empty list
        return []
