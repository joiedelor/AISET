"""
Requirements Router
DO-178C Traceability: REQ-API-004
Purpose: Requirements management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from database.connection import get_db
from models.requirement import Requirement, RequirementType, RequirementPriority, RequirementStatus
from services.requirements_service import RequirementsService

router = APIRouter()


class RequirementCreate(BaseModel):
    """Schema for creating a requirement."""
    project_id: int
    requirement_id: str
    title: str
    description: str
    type: RequirementType
    priority: RequirementPriority = RequirementPriority.MEDIUM
    parent_id: Optional[int] = None
    rationale: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    created_by: str = "system"


class RequirementResponse(BaseModel):
    """Schema for requirement response."""
    id: int
    requirement_id: str
    title: str
    description: str
    type: RequirementType
    priority: RequirementPriority
    status: RequirementStatus
    parent_id: Optional[int] = None
    confidence_score: float

    class Config:
        from_attributes = True


@router.post("/requirements", response_model=RequirementResponse)
async def create_requirement(
    requirement: RequirementCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new requirement.

    Traceability: REQ-REQ-006 - Requirement creation API
    """
    service = RequirementsService(db)

    try:
        db_requirement = service.create_requirement(**requirement.dict())
        return db_requirement
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/requirements/{requirement_id}", response_model=RequirementResponse)
async def get_requirement(requirement_id: int, db: Session = Depends(get_db)):
    """
    Get a specific requirement.

    Traceability: REQ-REQ-007 - Requirement retrieval API
    """
    service = RequirementsService(db)
    requirement = service.get_requirement(requirement_id)

    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    return requirement


@router.get("/projects/{project_id}/requirements", response_model=List[RequirementResponse])
async def list_requirements(
    project_id: int,
    status: Optional[RequirementStatus] = None,
    type: Optional[RequirementType] = None,
    priority: Optional[RequirementPriority] = None,
    db: Session = Depends(get_db)
):
    """
    List all requirements for a project.

    Traceability: REQ-REQ-008 - Requirements listing API
    """
    service = RequirementsService(db)
    requirements = service.get_requirements_by_project(
        project_id=project_id,
        status=status,
        req_type=type,
        priority=priority
    )

    return requirements


@router.post("/requirements/{requirement_id}/approve")
async def approve_requirement(
    requirement_id: int,
    approved_by: str,
    rationale: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Approve a requirement for implementation.

    Traceability: REQ-APPROVAL-003 - Approval API
    """
    service = RequirementsService(db)

    try:
        requirement = service.approve_requirement(
            requirement_id=requirement_id,
            approved_by=approved_by,
            rationale=rationale
        )
        return {"status": "approved", "requirement_id": requirement.requirement_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/requirements/{requirement_id}/validate")
async def validate_requirement(requirement_id: int, db: Session = Depends(get_db)):
    """
    Validate requirement quality per DO-178C.

    Traceability: REQ-VALID-006 - Validation API
    """
    service = RequirementsService(db)
    requirement = service.get_requirement(requirement_id)

    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")

    validation_result = service.validate_requirement(requirement)
    return validation_result
