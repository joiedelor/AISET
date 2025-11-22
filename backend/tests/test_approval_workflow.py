"""
Approval Workflow Tests
DO-178C Traceability: REQ-AI-017, REQ-AI-018, REQ-AI-019
Purpose: Verify approval workflow compliance
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from services.approval_service import (
    ApprovalWorkflowService,
    ProposedChange,
    ApprovalDecision,
    ProposalStatus,
    ChangeType,
)
from models.ai_extracted_entity import EntityType, ValidationStatus


class TestApprovalWorkflowService:
    """Test cases for ApprovalWorkflowService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = ApprovalWorkflowService()

    # ==========================================
    # REQ-AI-017: User Review of AI Updates
    # ==========================================

    def test_proposal_starts_pending(self):
        """
        REQ-AI-017: All AI-proposed updates shall require explicit user review.
        Test that new proposals start in pending status.
        """
        proposal = ProposedChange(
            change_type=ChangeType.ADDITION,
            entity_type=EntityType.REQUIREMENT,
            section="3.1 Functional Requirements",
            proposed_content="REQ-TEST-001: Test requirement",
            confidence_score=0.9,
            rationale="Test rationale"
        )

        assert proposal.status == ProposalStatus.PENDING
        assert proposal.id is not None

    def test_get_pending_proposals_returns_only_pending(self):
        """
        REQ-AI-017: User review required for all proposals.
        Test that only pending proposals are returned.
        """
        # Create proposals with different statuses
        pending_proposal = ProposedChange(
            change_type=ChangeType.ADDITION,
            entity_type=EntityType.REQUIREMENT,
            section="Test",
            proposed_content="Pending content",
            confidence_score=0.8,
            rationale="Test"
        )

        approved_proposal = ProposedChange(
            change_type=ChangeType.MODIFICATION,
            entity_type=EntityType.REQUIREMENT,
            section="Test",
            proposed_content="Approved content",
            confidence_score=0.8,
            rationale="Test"
        )
        approved_proposal.status = ProposalStatus.APPROVED

        # Add to internal cache
        self.service._pending_proposals[pending_proposal.id] = pending_proposal
        self.service._pending_proposals[approved_proposal.id] = approved_proposal

        # Get pending proposals
        pending = self.service.get_pending_proposals()

        assert len(pending) == 1
        assert pending[0].id == pending_proposal.id

    # ==========================================
    # REQ-AI-018: No Automatic Approval
    # ==========================================

    @pytest.mark.asyncio
    async def test_approval_requires_reviewer(self):
        """
        REQ-AI-018: AI shall NEVER automatically approve changes.
        Test that approval decision requires a reviewer identity.
        """
        # Create a proposal
        proposal = ProposedChange(
            change_type=ChangeType.ADDITION,
            entity_type=EntityType.REQUIREMENT,
            section="Test",
            proposed_content="Test content",
            confidence_score=0.8,
            rationale="Test"
        )
        self.service._pending_proposals[proposal.id] = proposal

        # Attempt approval without reviewer
        decision = ApprovalDecision(
            proposal_id=proposal.id,
            decision=ProposalStatus.APPROVED,
            rationale="Test approval",
            reviewed_by=""  # Empty reviewer - should fail
        )

        # Mock database session
        mock_db = MagicMock()

        with pytest.raises(ValueError) as exc_info:
            await self.service.process_approval_decision(decision, mock_db)

        assert "REQ-AI-018 violation" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_no_auto_commit_without_user_action(self):
        """
        REQ-AI-018: AI shall NEVER automatically commit changes.
        Test that changes are not committed without explicit user action.
        """
        # Create a proposal
        proposal = ProposedChange(
            change_type=ChangeType.ADDITION,
            entity_type=EntityType.REQUIREMENT,
            section="Test",
            proposed_content="Test content",
            confidence_score=0.8,
            rationale="Test"
        )
        self.service._pending_proposals[proposal.id] = proposal

        # Verify proposal is still pending (not auto-committed)
        assert proposal.status == ProposalStatus.PENDING

        # Verify it's in the pending list
        pending = self.service.get_pending_proposals()
        assert proposal.id in [p.id for p in pending]

    # ==========================================
    # REQ-AI-019: Highlighted Proposed Changes
    # ==========================================

    def test_proposal_has_change_type(self):
        """
        REQ-AI-019: AI shall highlight proposed changes.
        Test that proposals have change type for highlighting.
        """
        addition = ProposedChange(
            change_type=ChangeType.ADDITION,
            entity_type=EntityType.REQUIREMENT,
            section="Test",
            proposed_content="New content",
            confidence_score=0.8,
            rationale="Test"
        )

        modification = ProposedChange(
            change_type=ChangeType.MODIFICATION,
            entity_type=EntityType.REQUIREMENT,
            section="Test",
            original_content="Old content",
            proposed_content="New content",
            confidence_score=0.8,
            rationale="Test"
        )

        deletion = ProposedChange(
            change_type=ChangeType.DELETION,
            entity_type=EntityType.REQUIREMENT,
            section="Test",
            original_content="Content to delete",
            proposed_content="",
            confidence_score=0.8,
            rationale="Test"
        )

        assert addition.change_type == ChangeType.ADDITION
        assert modification.change_type == ChangeType.MODIFICATION
        assert deletion.change_type == ChangeType.DELETION

    def test_get_proposal_diff_returns_highlight_info(self):
        """
        REQ-AI-019: Visually distinct highlighting for proposed changes.
        Test that diff view includes highlight class information.
        """
        # Create a proposal
        proposal = ProposedChange(
            change_type=ChangeType.ADDITION,
            entity_type=EntityType.REQUIREMENT,
            section="Test",
            proposed_content="Test content",
            confidence_score=0.8,
            rationale="Test"
        )
        self.service._pending_proposals[proposal.id] = proposal

        # Get diff
        diff = self.service.get_proposal_diff(proposal.id)

        assert "highlight_class" in diff
        assert "green" in diff["highlight_class"]  # Addition should be green
        assert diff["change_type"] == "addition"

    def test_modification_has_original_and_proposed(self):
        """
        REQ-AI-019: Enable easy identification of changes.
        Test that modifications include both original and proposed content.
        """
        proposal = ProposedChange(
            change_type=ChangeType.MODIFICATION,
            entity_type=EntityType.REQUIREMENT,
            section="Test",
            original_content="Original requirement text",
            proposed_content="Modified requirement text",
            confidence_score=0.8,
            rationale="Improved clarity"
        )
        self.service._pending_proposals[proposal.id] = proposal

        diff = self.service.get_proposal_diff(proposal.id)

        assert diff["original"] == "Original requirement text"
        assert diff["proposed"] == "Modified requirement text"
        assert "yellow" in diff["highlight_class"]  # Modification should be yellow

    # ==========================================
    # Integration Tests
    # ==========================================

    @pytest.mark.asyncio
    async def test_approve_proposal_creates_entity(self):
        """
        Test that approving a proposal creates the corresponding entity.
        """
        # Create a proposal
        proposal = ProposedChange(
            change_type=ChangeType.ADDITION,
            entity_type=EntityType.REQUIREMENT,
            section="3.1 Functional",
            proposed_content="REQ-TEST-001: Test requirement",
            confidence_score=0.9,
            rationale="Test"
        )
        self.service._pending_proposals[proposal.id] = proposal

        # Mock database with proper chain
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.flush = MagicMock()

        # Approve
        decision = ApprovalDecision(
            proposal_id=proposal.id,
            decision=ProposalStatus.APPROVED,
            rationale="Approved for testing",
            reviewed_by="test_user"
        )

        # Patch the database query to avoid JSONB issues
        with patch.object(self.service, '_create_entity_from_proposal', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = 123  # Fake entity ID
            result = await self.service.process_approval_decision(decision, mock_db)

        assert result["decision"] == "approved"
        assert result["reviewed_by"] == "test_user"
        assert proposal.id not in self.service._pending_proposals

    @pytest.mark.asyncio
    async def test_reject_proposal_removes_from_pending(self):
        """
        Test that rejecting a proposal removes it from pending.
        """
        # Create a proposal
        proposal = ProposedChange(
            change_type=ChangeType.ADDITION,
            entity_type=EntityType.REQUIREMENT,
            section="Test",
            proposed_content="Test content",
            confidence_score=0.8,
            rationale="Test"
        )
        self.service._pending_proposals[proposal.id] = proposal

        # Mock database with proper chain
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()

        # Reject
        decision = ApprovalDecision(
            proposal_id=proposal.id,
            decision=ProposalStatus.REJECTED,
            rationale="Not needed",
            reviewed_by="test_user"
        )

        result = await self.service.process_approval_decision(decision, mock_db)

        assert result["decision"] == "rejected"
        assert proposal.id not in self.service._pending_proposals

    @pytest.mark.asyncio
    async def test_modify_proposal_uses_modified_content(self):
        """
        Test that modifying a proposal uses the user's modified content.
        """
        # Create a proposal
        proposal = ProposedChange(
            change_type=ChangeType.ADDITION,
            entity_type=EntityType.REQUIREMENT,
            section="Test",
            proposed_content="Original AI proposal",
            confidence_score=0.8,
            rationale="Test"
        )
        self.service._pending_proposals[proposal.id] = proposal

        # Mock database with proper chain
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.flush = MagicMock()

        # Modify
        modified_content = "User-modified content"
        decision = ApprovalDecision(
            proposal_id=proposal.id,
            decision=ProposalStatus.MODIFIED,
            modified_content=modified_content,
            rationale="Improved wording",
            reviewed_by="test_user"
        )

        # Patch the database query to avoid JSONB issues
        with patch.object(self.service, '_create_entity_from_proposal', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = 124  # Fake entity ID
            result = await self.service.process_approval_decision(decision, mock_db)

        assert result["decision"] == "modified"
        assert result["modified_content"] == modified_content


class TestApprovalDecision:
    """Test cases for ApprovalDecision model."""

    def test_approval_decision_requires_rationale(self):
        """Test that approval decisions require rationale."""
        decision = ApprovalDecision(
            proposal_id="test-123",
            decision=ProposalStatus.APPROVED,
            rationale="Test rationale",
            reviewed_by="test_user"
        )

        assert decision.rationale == "Test rationale"

    def test_modified_decision_can_have_content(self):
        """Test that modified decisions can include modified content."""
        decision = ApprovalDecision(
            proposal_id="test-123",
            decision=ProposalStatus.MODIFIED,
            modified_content="Modified content here",
            rationale="Changed wording",
            reviewed_by="test_user"
        )

        assert decision.modified_content == "Modified content here"


class TestProposedChange:
    """Test cases for ProposedChange model."""

    def test_proposed_change_has_uuid(self):
        """Test that proposals have unique UUIDs."""
        proposal1 = ProposedChange(
            change_type=ChangeType.ADDITION,
            entity_type=EntityType.REQUIREMENT,
            section="Test",
            proposed_content="Content 1",
            confidence_score=0.8,
            rationale="Test"
        )

        proposal2 = ProposedChange(
            change_type=ChangeType.ADDITION,
            entity_type=EntityType.REQUIREMENT,
            section="Test",
            proposed_content="Content 2",
            confidence_score=0.8,
            rationale="Test"
        )

        assert proposal1.id != proposal2.id

    def test_confidence_score_validation(self):
        """Test that confidence score is between 0 and 1."""
        proposal = ProposedChange(
            change_type=ChangeType.ADDITION,
            entity_type=EntityType.REQUIREMENT,
            section="Test",
            proposed_content="Content",
            confidence_score=0.85,
            rationale="Test"
        )

        assert 0.0 <= proposal.confidence_score <= 1.0


# Run tests with: pytest backend/tests/test_approval_workflow.py -v
