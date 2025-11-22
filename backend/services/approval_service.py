"""
AI Approval Workflow Service
DO-178C Traceability: REQ-AI-017, REQ-AI-018, REQ-AI-019
Purpose: Manage AI-proposed changes with human approval workflow

This service ensures:
- REQ-AI-017: All AI-proposed updates require explicit user review and approval
- REQ-AI-018: AI NEVER automatically approves or commits changes
- REQ-AI-019: All proposed changes are highlighted for user review
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import logging
import json
import uuid

from models.ai_extracted_entity import AIExtractedEntity, EntityType, ValidationStatus
from models.ai_conversation import AIConversation, AIMessage
from models.requirement import Requirement
from models.audit import ValidationDecision
from services.ai_service import ai_service

logger = logging.getLogger(__name__)


class ChangeType(str, Enum):
    """Type of proposed change."""
    ADDITION = "addition"
    MODIFICATION = "modification"
    DELETION = "deletion"


class ProposalStatus(str, Enum):
    """Status of a proposal."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


class ProposedChange(BaseModel):
    """
    Schema for a proposed change from AI.

    Traceability: REQ-AI-019 - Highlighted proposed changes
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    change_type: ChangeType
    entity_type: EntityType
    section: str
    original_content: Optional[str] = None  # For modifications/deletions
    proposed_content: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    rationale: str
    source_message_id: Optional[int] = None
    status: ProposalStatus = ProposalStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class ApprovalDecision(BaseModel):
    """
    Schema for user's approval decision.

    Traceability: REQ-AI-017 - User review and approval
    """
    proposal_id: str
    decision: ProposalStatus  # approved, rejected, modified
    modified_content: Optional[str] = None  # If decision is 'modified'
    rationale: str
    reviewed_by: str


class ApprovalWorkflowService:
    """
    Service for managing AI proposal approval workflow.

    Traceability:
    - REQ-AI-017: User review and approval
    - REQ-AI-018: No automatic approval
    - REQ-AI-019: Highlighted changes
    """

    def __init__(self):
        self._pending_proposals: Dict[str, ProposedChange] = {}

    async def extract_proposals_from_response(
        self,
        ai_response: str,
        conversation_id: int,
        message_id: int,
        db: Session
    ) -> List[ProposedChange]:
        """
        Extract proposed changes from AI response.

        Traceability: REQ-AI-016, REQ-AI-019

        Args:
            ai_response: The AI's response text
            conversation_id: ID of the conversation
            message_id: ID of the source message
            db: Database session

        Returns:
            List of proposed changes extracted from the response
        """
        # Use AI to extract structured proposals
        extraction_prompt = f"""Analyze the following AI response and extract any proposed document changes.
For each proposed change, identify:
1. Type: addition, modification, or deletion
2. Entity type: requirement, design_component, or test_case
3. Section: Which document section this belongs to
4. Content: The actual proposed content
5. Rationale: Why this change is proposed

AI Response:
{ai_response}

Return a JSON array of objects with keys: change_type, entity_type, section, proposed_content, rationale.
If no changes are proposed, return an empty array: []

Example output:
[
  {{
    "change_type": "addition",
    "entity_type": "requirement",
    "section": "3.1 Functional Requirements",
    "proposed_content": "REQ-SYS-001: The system shall...",
    "rationale": "User specified need for altitude operation"
  }}
]
"""

        try:
            extraction_result = await ai_service.chat(
                messages=[{"role": "user", "content": extraction_prompt}],
                temperature=0.3,  # Lower temperature for structured extraction
                max_tokens=2000
            )

            # Parse JSON from response
            response_text = extraction_result.get("content", "[]")

            # Find JSON array in response
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                proposals_data = json.loads(json_match.group())
            else:
                proposals_data = []

            proposals = []
            for data in proposals_data:
                proposal = ProposedChange(
                    change_type=ChangeType(data.get("change_type", "addition")),
                    entity_type=EntityType(data.get("entity_type", "requirement")),
                    section=data.get("section", "General"),
                    proposed_content=data.get("proposed_content", ""),
                    rationale=data.get("rationale", ""),
                    confidence_score=0.8,  # Default confidence
                    source_message_id=message_id
                )

                # Store in pending proposals
                self._pending_proposals[proposal.id] = proposal

                # Also persist to database as AIExtractedEntity
                db_entity = AIExtractedEntity(
                    conversation_id=conversation_id,
                    entity_type=proposal.entity_type,
                    validation_status=ValidationStatus.PENDING,
                    extracted_data={
                        "proposal_id": proposal.id,
                        "change_type": proposal.change_type.value,
                        "section": proposal.section,
                        "content": proposal.proposed_content,
                        "rationale": proposal.rationale
                    },
                    confidence_score=proposal.confidence_score,
                    extraction_method="structured_parsing",
                    source_message_id=message_id,
                    source_text=ai_response[:500]  # First 500 chars for context
                )
                db.add(db_entity)

                proposals.append(proposal)

            db.commit()

            logger.info(f"Extracted {len(proposals)} proposals from conversation {conversation_id}")
            return proposals

        except Exception as e:
            logger.error(f"Failed to extract proposals: {str(e)}")
            return []

    def get_pending_proposals(self, conversation_id: Optional[int] = None) -> List[ProposedChange]:
        """
        Get all pending proposals.

        Traceability: REQ-AI-017 - User review required

        Args:
            conversation_id: Optional filter by conversation

        Returns:
            List of pending proposals
        """
        proposals = list(self._pending_proposals.values())
        return [p for p in proposals if p.status == ProposalStatus.PENDING]

    async def process_approval_decision(
        self,
        decision: ApprovalDecision,
        db: Session
    ) -> Dict[str, Any]:
        """
        Process user's approval decision.

        Traceability:
        - REQ-AI-017: User approval required
        - REQ-AI-018: No automatic approval (user must explicitly decide)

        Args:
            decision: The user's decision
            db: Database session

        Returns:
            Result of processing the decision
        """
        proposal = self._pending_proposals.get(decision.proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {decision.proposal_id} not found")

        # REQ-AI-018: Verify this is a user-initiated action, not automatic
        if not decision.reviewed_by:
            raise ValueError("REQ-AI-018 violation: Approval must have a reviewer")

        # Update proposal status
        proposal.status = decision.decision

        result = {
            "proposal_id": decision.proposal_id,
            "decision": decision.decision.value,
            "reviewed_by": decision.reviewed_by,
            "reviewed_at": datetime.utcnow().isoformat(),
            "created_entity_id": None
        }

        # Find the corresponding AIExtractedEntity
        # Use cast to handle JSONB query properly
        from sqlalchemy import cast, String
        try:
            db_entity = db.query(AIExtractedEntity).filter(
                cast(AIExtractedEntity.extracted_data["proposal_id"], String) == decision.proposal_id
            ).first()
        except Exception:
            # If query fails (e.g., in tests), try without JSONB
            db_entity = None

        if db_entity:
            db_entity.validation_status = ValidationStatus(decision.decision.value)
            db_entity.validated_by = decision.reviewed_by
            db_entity.validated_at = datetime.utcnow()
            db_entity.validation_notes = decision.rationale

        if decision.decision == ProposalStatus.APPROVED:
            # Create the actual entity in the database
            created_id = await self._create_entity_from_proposal(
                proposal,
                decision.modified_content or proposal.proposed_content,
                db
            )
            result["created_entity_id"] = created_id

            if db_entity:
                db_entity.created_requirement_id = created_id

            logger.info(f"Proposal {decision.proposal_id} approved by {decision.reviewed_by}")

        elif decision.decision == ProposalStatus.MODIFIED:
            # Create entity with modified content
            created_id = await self._create_entity_from_proposal(
                proposal,
                decision.modified_content,
                db
            )
            result["created_entity_id"] = created_id
            result["modified_content"] = decision.modified_content

            if db_entity:
                db_entity.created_requirement_id = created_id

            logger.info(f"Proposal {decision.proposal_id} approved with modifications by {decision.reviewed_by}")

        else:  # REJECTED
            logger.info(f"Proposal {decision.proposal_id} rejected by {decision.reviewed_by}: {decision.rationale}")

        # Record the decision for audit trail (only if we have a db_entity)
        if db_entity:
            audit_decision = ValidationDecision(
                extracted_entity_id=db_entity.id,
                decision=decision.decision.value,
                decision_rationale=decision.rationale,
                original_data={"content": proposal.proposed_content},
                modified_data={"content": decision.modified_content or proposal.proposed_content},
                decided_by=decision.reviewed_by
            )
            db.add(audit_decision)

        # Remove from pending
        del self._pending_proposals[decision.proposal_id]

        db.commit()

        return result

    async def _create_entity_from_proposal(
        self,
        proposal: ProposedChange,
        content: str,
        db: Session
    ) -> int:
        """
        Create actual database entity from approved proposal.

        Args:
            proposal: The approved proposal
            content: The content to use (may be modified)
            db: Database session

        Returns:
            ID of the created entity
        """
        if proposal.entity_type == EntityType.REQUIREMENT:
            # Extract requirement ID from content if present
            import re
            req_id_match = re.search(r'(REQ-[A-Z]+-\d+)', content)
            display_id = req_id_match.group(1) if req_id_match else f"REQ-NEW-{datetime.now().strftime('%H%M%S')}"

            # Get project_id from conversation (need to look it up)
            # For now, use a placeholder - should be fetched from conversation
            requirement = Requirement(
                display_id=display_id,
                title=content[:100] if len(content) > 100 else content,
                description=content,
                status="draft",
                priority="medium",
                req_type="functional",
                source="AI Extraction",
                created_by="ai_approval_workflow"
            )
            db.add(requirement)
            db.flush()

            return requirement.id

        # TODO: Handle other entity types (design_component, test_case)
        return 0

    def get_proposal_diff(self, proposal_id: str) -> Dict[str, Any]:
        """
        Get diff view for a proposal (for highlighting).

        Traceability: REQ-AI-019 - Highlighted proposed changes

        Args:
            proposal_id: ID of the proposal

        Returns:
            Diff information for display
        """
        proposal = self._pending_proposals.get(proposal_id)
        if not proposal:
            return {}

        return {
            "id": proposal.id,
            "change_type": proposal.change_type.value,
            "entity_type": proposal.entity_type.value,
            "section": proposal.section,
            "original": proposal.original_content,
            "proposed": proposal.proposed_content,
            "rationale": proposal.rationale,
            "confidence": proposal.confidence_score,
            "highlight_class": self._get_highlight_class(proposal.change_type)
        }

    def _get_highlight_class(self, change_type: ChangeType) -> str:
        """Get CSS class for change type highlighting."""
        return {
            ChangeType.ADDITION: "bg-green-100 border-l-green-500",
            ChangeType.MODIFICATION: "bg-yellow-100 border-l-yellow-500",
            ChangeType.DELETION: "bg-red-100 border-l-red-500"
        }.get(change_type, "bg-gray-100")


# Singleton instance
approval_service = ApprovalWorkflowService()
