"""
AI Approval Workflow Router
DO-178C Traceability: REQ-AI-017, REQ-AI-018, REQ-AI-019
Purpose: API endpoints for AI proposal approval workflow
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from database.connection import get_db
from services.approval_service import (
    approval_service,
    ProposedChange,
    ApprovalDecision,
    ProposalStatus,
    ChangeType
)
from models.ai_extracted_entity import AIExtractedEntity, ValidationStatus, EntityType
from models.ai_conversation import AIConversation

router = APIRouter()


# === Request/Response Schemas ===

class ProposalResponse(BaseModel):
    """Response schema for a proposal."""
    id: str
    change_type: str
    entity_type: str
    section: str
    original_content: Optional[str] = None
    proposed_content: str
    confidence_score: float
    rationale: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApprovalRequest(BaseModel):
    """Request schema for approving/rejecting a proposal."""
    decision: str = Field(..., description="One of: approved, rejected, modified")
    modified_content: Optional[str] = Field(None, description="Required if decision is 'modified'")
    rationale: str = Field(..., description="Reason for the decision")
    reviewed_by: str = Field(..., description="Username of the reviewer")


class ApprovalResponse(BaseModel):
    """Response schema for approval decision."""
    proposal_id: str
    decision: str
    reviewed_by: str
    reviewed_at: str
    created_entity_id: Optional[int] = None
    modified_content: Optional[str] = None


class BulkApprovalRequest(BaseModel):
    """Request schema for bulk approval."""
    proposal_ids: List[str]
    decision: str
    rationale: str
    reviewed_by: str


class ProposalDiff(BaseModel):
    """Response schema for proposal diff view."""
    id: str
    change_type: str
    entity_type: str
    section: str
    original: Optional[str] = None
    proposed: str
    rationale: str
    confidence: float
    highlight_class: str


# === Endpoints ===

@router.get("/proposals", response_model=List[ProposalResponse])
async def get_pending_proposals(
    conversation_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all pending proposals requiring user approval.

    Traceability: REQ-AI-017 - User review required

    Args:
        conversation_id: Optional filter by conversation
        db: Database session

    Returns:
        List of pending proposals
    """
    # Get from in-memory cache
    proposals = approval_service.get_pending_proposals(conversation_id)

    # Also get from database for persistence across restarts
    db_query = db.query(AIExtractedEntity).filter(
        AIExtractedEntity.validation_status == ValidationStatus.PENDING
    )

    if conversation_id:
        db_query = db_query.filter(AIExtractedEntity.conversation_id == conversation_id)

    db_entities = db_query.all()

    # Convert database entities to ProposalResponse
    db_proposals = []
    for entity in db_entities:
        data = entity.extracted_data or {}
        db_proposals.append(ProposalResponse(
            id=data.get("proposal_id", str(entity.id)),
            change_type=data.get("change_type", "addition"),
            entity_type=entity.entity_type.value,
            section=data.get("section", "General"),
            proposed_content=data.get("content", ""),
            confidence_score=entity.confidence_score or 0.8,
            rationale=data.get("rationale", ""),
            status="pending",
            created_at=entity.created_at
        ))

    # Merge in-memory and database proposals
    in_memory_ids = {p.id for p in proposals}
    result = [ProposalResponse(
        id=p.id,
        change_type=p.change_type.value,
        entity_type=p.entity_type.value,
        section=p.section,
        original_content=p.original_content,
        proposed_content=p.proposed_content,
        confidence_score=p.confidence_score,
        rationale=p.rationale,
        status=p.status.value,
        created_at=p.created_at
    ) for p in proposals]

    # Add database proposals not in memory
    for db_proposal in db_proposals:
        if db_proposal.id not in in_memory_ids:
            result.append(db_proposal)

    return result


@router.get("/proposals/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific proposal by ID.

    Traceability: REQ-AI-019 - View proposed changes

    Args:
        proposal_id: ID of the proposal
        db: Database session

    Returns:
        The proposal details
    """
    # Check in-memory first
    proposals = approval_service.get_pending_proposals()
    for p in proposals:
        if p.id == proposal_id:
            return ProposalResponse(
                id=p.id,
                change_type=p.change_type.value,
                entity_type=p.entity_type.value,
                section=p.section,
                original_content=p.original_content,
                proposed_content=p.proposed_content,
                confidence_score=p.confidence_score,
                rationale=p.rationale,
                status=p.status.value,
                created_at=p.created_at
            )

    # Check database
    entity = db.query(AIExtractedEntity).filter(
        AIExtractedEntity.extracted_data["proposal_id"].astext == proposal_id
    ).first()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal {proposal_id} not found"
        )

    data = entity.extracted_data or {}
    return ProposalResponse(
        id=data.get("proposal_id", str(entity.id)),
        change_type=data.get("change_type", "addition"),
        entity_type=entity.entity_type.value,
        section=data.get("section", "General"),
        proposed_content=data.get("content", ""),
        confidence_score=entity.confidence_score or 0.8,
        rationale=data.get("rationale", ""),
        status=entity.validation_status.value,
        created_at=entity.created_at
    )


@router.get("/proposals/{proposal_id}/diff", response_model=ProposalDiff)
async def get_proposal_diff(
    proposal_id: str,
    db: Session = Depends(get_db)
):
    """
    Get diff view for a proposal with highlighting information.

    Traceability: REQ-AI-019 - Highlighted proposed changes

    Args:
        proposal_id: ID of the proposal
        db: Database session

    Returns:
        Diff information for display
    """
    diff = approval_service.get_proposal_diff(proposal_id)

    if not diff:
        # Try database
        entity = db.query(AIExtractedEntity).filter(
            AIExtractedEntity.extracted_data["proposal_id"].astext == proposal_id
        ).first()

        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proposal {proposal_id} not found"
            )

        data = entity.extracted_data or {}
        change_type = data.get("change_type", "addition")
        highlight_class = {
            "addition": "bg-green-100 border-l-green-500",
            "modification": "bg-yellow-100 border-l-yellow-500",
            "deletion": "bg-red-100 border-l-red-500"
        }.get(change_type, "bg-gray-100")

        diff = {
            "id": data.get("proposal_id", str(entity.id)),
            "change_type": change_type,
            "entity_type": entity.entity_type.value,
            "section": data.get("section", "General"),
            "original": None,
            "proposed": data.get("content", ""),
            "rationale": data.get("rationale", ""),
            "confidence": entity.confidence_score or 0.8,
            "highlight_class": highlight_class
        }

    return ProposalDiff(**diff)


@router.post("/proposals/{proposal_id}/approve", response_model=ApprovalResponse)
async def approve_proposal(
    proposal_id: str,
    request: ApprovalRequest,
    db: Session = Depends(get_db)
):
    """
    Approve or reject a proposal.

    Traceability:
    - REQ-AI-017: Explicit user approval required
    - REQ-AI-018: No automatic approval (must have reviewer)

    Args:
        proposal_id: ID of the proposal
        request: Approval request with decision and rationale
        db: Database session

    Returns:
        Result of the approval decision
    """
    # Validate decision
    try:
        decision_status = ProposalStatus(request.decision)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid decision '{request.decision}'. Must be: approved, rejected, or modified"
        )

    # REQ-AI-018: Require reviewer identity
    if not request.reviewed_by:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="REQ-AI-018 violation: reviewed_by is required (no automatic approval)"
        )

    # REQ-AI-017: If modified, require modified_content
    if decision_status == ProposalStatus.MODIFIED and not request.modified_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="modified_content is required when decision is 'modified'"
        )

    decision = ApprovalDecision(
        proposal_id=proposal_id,
        decision=decision_status,
        modified_content=request.modified_content,
        rationale=request.rationale,
        reviewed_by=request.reviewed_by
    )

    try:
        result = await approval_service.process_approval_decision(decision, db)
        return ApprovalResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/proposals/bulk-approve", response_model=List[ApprovalResponse])
async def bulk_approve_proposals(
    request: BulkApprovalRequest,
    db: Session = Depends(get_db)
):
    """
    Approve or reject multiple proposals at once.

    Traceability: REQ-AI-017 - Batch user approval

    Args:
        request: Bulk approval request
        db: Database session

    Returns:
        List of approval results
    """
    # Validate decision
    try:
        decision_status = ProposalStatus(request.decision)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid decision '{request.decision}'"
        )

    # REQ-AI-018: Require reviewer identity
    if not request.reviewed_by:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="REQ-AI-018 violation: reviewed_by is required"
        )

    results = []
    for proposal_id in request.proposal_ids:
        decision = ApprovalDecision(
            proposal_id=proposal_id,
            decision=decision_status,
            rationale=request.rationale,
            reviewed_by=request.reviewed_by
        )

        try:
            result = await approval_service.process_approval_decision(decision, db)
            results.append(ApprovalResponse(**result))
        except ValueError as e:
            # Skip non-existent proposals but log the error
            import logging
            logging.getLogger(__name__).warning(f"Skipping proposal {proposal_id}: {str(e)}")

    return results


@router.get("/conversations/{conversation_id}/proposals", response_model=List[ProposalResponse])
async def get_conversation_proposals(
    conversation_id: int,
    include_processed: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all proposals for a specific conversation.

    Traceability: REQ-AI-017, REQ-AI-019

    Args:
        conversation_id: ID of the conversation
        include_processed: Whether to include approved/rejected proposals
        db: Database session

    Returns:
        List of proposals for the conversation
    """
    # Verify conversation exists
    conversation = db.query(AIConversation).filter(
        AIConversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )

    # Query database
    query = db.query(AIExtractedEntity).filter(
        AIExtractedEntity.conversation_id == conversation_id
    )

    if not include_processed:
        query = query.filter(AIExtractedEntity.validation_status == ValidationStatus.PENDING)

    entities = query.order_by(AIExtractedEntity.created_at.desc()).all()

    return [
        ProposalResponse(
            id=(entity.extracted_data or {}).get("proposal_id", str(entity.id)),
            change_type=(entity.extracted_data or {}).get("change_type", "addition"),
            entity_type=entity.entity_type.value,
            section=(entity.extracted_data or {}).get("section", "General"),
            proposed_content=(entity.extracted_data or {}).get("content", ""),
            confidence_score=entity.confidence_score or 0.8,
            rationale=(entity.extracted_data or {}).get("rationale", ""),
            status=entity.validation_status.value,
            created_at=entity.created_at
        )
        for entity in entities
    ]


@router.post("/conversations/{conversation_id}/extract-proposals")
async def extract_proposals_from_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """
    Extract proposals from all messages in a conversation.

    Traceability: REQ-AI-016, REQ-AI-019

    Args:
        conversation_id: ID of the conversation
        db: Database session

    Returns:
        Number of proposals extracted
    """
    from models.ai_conversation import AIMessage, MessageRole

    # Get all assistant messages
    messages = db.query(AIMessage).filter(
        AIMessage.conversation_id == conversation_id,
        AIMessage.role == MessageRole.ASSISTANT
    ).order_by(AIMessage.created_at).all()

    if not messages:
        return {"extracted_count": 0, "message": "No assistant messages found"}

    total_proposals = []
    for message in messages:
        proposals = await approval_service.extract_proposals_from_response(
            ai_response=message.content,
            conversation_id=conversation_id,
            message_id=message.id,
            db=db
        )
        total_proposals.extend(proposals)

    return {
        "extracted_count": len(total_proposals),
        "proposals": [
            {
                "id": p.id,
                "type": p.change_type.value,
                "section": p.section,
                "content": p.proposed_content[:100] + "..." if len(p.proposed_content) > 100 else p.proposed_content
            }
            for p in total_proposals
        ]
    }
