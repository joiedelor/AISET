"""
Configuration Items Router
DO-178C Traceability: REQ-AI-038, REQ-AI-039, REQ-AI-040, REQ-BE-013
Purpose: REST API endpoints for product structure and BOM management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from database.connection import get_db
from services.configuration_item_service import ConfigurationItemService
from services.activity_interview_service import ActivityInterviewService
from models.configuration_item import CIType, CILifecyclePhase, CIControlLevel, CIStatus, BOMType

router = APIRouter()


# ==================== Pydantic Schemas ====================

class CICreate(BaseModel):
    """Schema for creating a Configuration Item."""
    ci_identifier: str
    name: str
    ci_type: str = "component"
    parent_id: Optional[int] = None
    description: Optional[str] = None
    part_number: Optional[str] = None
    revision: Optional[str] = None
    version: Optional[str] = None
    lifecycle_phase: Optional[str] = "development"
    control_level: Optional[str] = "level_3"
    status: Optional[str] = "draft"
    criticality: Optional[str] = None
    supplier: Optional[str] = None
    notes: Optional[str] = None


class CIUpdate(BaseModel):
    """Schema for updating a Configuration Item."""
    name: Optional[str] = None
    description: Optional[str] = None
    ci_type: Optional[str] = None
    parent_id: Optional[int] = None
    part_number: Optional[str] = None
    revision: Optional[str] = None
    version: Optional[str] = None
    lifecycle_phase: Optional[str] = None
    control_level: Optional[str] = None
    status: Optional[str] = None
    criticality: Optional[str] = None
    supplier: Optional[str] = None
    notes: Optional[str] = None


class BOMCreate(BaseModel):
    """Schema for creating a BOM entry."""
    parent_ci_id: int
    child_ci_id: int
    quantity: float = 1.0
    bom_type: str = "engineering"
    unit_of_measure: str = "each"
    position_reference: Optional[str] = None
    find_number: Optional[str] = None
    is_alternate: bool = False
    notes: Optional[str] = None


class CIResponse(BaseModel):
    """Response schema for a Configuration Item."""
    id: int
    guid: str
    ci_identifier: str
    project_id: int
    parent_id: Optional[int]
    level: int
    name: str
    description: Optional[str]
    ci_type: Optional[str]
    part_number: Optional[str]
    status: Optional[str]
    lifecycle_phase: Optional[str]
    control_level: Optional[str]
    criticality: Optional[str]
    created_at: Optional[datetime]
    children_count: int = 0

    class Config:
        from_attributes = True


# ==================== CI Endpoints ====================

@router.get("/projects/{project_id}/configuration-items")
async def get_project_cis(
    project_id: int,
    ci_type: Optional[str] = None,
    root_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all Configuration Items for a project.

    Traceability: REQ-AI-038 - Product Structure

    Args:
        project_id: Project ID
        ci_type: Optional filter by CI type
        root_only: If true, only return root items (no parent)
    """
    service = ConfigurationItemService(db)

    type_enum = None
    if ci_type:
        try:
            type_enum = CIType(ci_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid CI type: {ci_type}")

    parent_filter = None if not root_only else None

    cis = service.get_project_cis(project_id, ci_type=type_enum, parent_id=parent_filter)

    return {
        "project_id": project_id,
        "count": len(cis),
        "configuration_items": [ci.to_dict() for ci in cis]
    }


@router.get("/projects/{project_id}/product-structure")
async def get_product_structure_tree(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get full product structure tree for a project.

    Traceability: REQ-AI-038 - Product Structure Extraction
    """
    service = ConfigurationItemService(db)
    tree = service.get_product_structure_tree(project_id)

    return {
        "project_id": project_id,
        "tree": tree
    }


@router.post("/projects/{project_id}/configuration-items", status_code=status.HTTP_201_CREATED)
async def create_ci(
    project_id: int,
    ci_data: CICreate,
    db: Session = Depends(get_db)
):
    """
    Create a new Configuration Item.

    Traceability: REQ-AI-039 - CI Data Extraction
    """
    service = ConfigurationItemService(db)

    # Check if identifier already exists
    existing = service.get_ci_by_identifier(project_id, ci_data.ci_identifier)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"CI identifier '{ci_data.ci_identifier}' already exists in this project"
        )

    # Parse enums
    try:
        ci_type = CIType(ci_data.ci_type) if ci_data.ci_type else CIType.COMPONENT
        lifecycle = CILifecyclePhase(ci_data.lifecycle_phase) if ci_data.lifecycle_phase else CILifecyclePhase.DEVELOPMENT
        control = CIControlLevel(ci_data.control_level) if ci_data.control_level else CIControlLevel.LEVEL_3
        status_enum = CIStatus(ci_data.status) if ci_data.status else CIStatus.DRAFT
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    ci = service.create_ci(
        project_id=project_id,
        ci_identifier=ci_data.ci_identifier,
        name=ci_data.name,
        ci_type=ci_type,
        parent_id=ci_data.parent_id,
        description=ci_data.description,
        part_number=ci_data.part_number,
        revision=ci_data.revision,
        version=ci_data.version,
        lifecycle_phase=lifecycle,
        control_level=control,
        status=status_enum,
        criticality=ci_data.criticality,
        supplier=ci_data.supplier,
        notes=ci_data.notes
    )

    return ci.to_dict()


@router.get("/configuration-items/{ci_id}")
async def get_ci(ci_id: int, db: Session = Depends(get_db)):
    """Get a Configuration Item by ID."""
    service = ConfigurationItemService(db)
    ci = service.get_ci_by_id(ci_id)

    if not ci:
        raise HTTPException(status_code=404, detail="Configuration Item not found")

    return ci.to_dict()


@router.put("/configuration-items/{ci_id}")
async def update_ci(
    ci_id: int,
    ci_data: CIUpdate,
    db: Session = Depends(get_db)
):
    """Update a Configuration Item."""
    service = ConfigurationItemService(db)

    update_data = ci_data.dict(exclude_unset=True)

    # Parse enums if provided
    if "ci_type" in update_data and update_data["ci_type"]:
        try:
            update_data["ci_type"] = CIType(update_data["ci_type"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid CI type")

    if "lifecycle_phase" in update_data and update_data["lifecycle_phase"]:
        try:
            update_data["lifecycle_phase"] = CILifecyclePhase(update_data["lifecycle_phase"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid lifecycle phase")

    if "control_level" in update_data and update_data["control_level"]:
        try:
            update_data["control_level"] = CIControlLevel(update_data["control_level"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid control level")

    if "status" in update_data and update_data["status"]:
        try:
            update_data["status"] = CIStatus(update_data["status"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")

    ci = service.update_ci(ci_id, **update_data)

    if not ci:
        raise HTTPException(status_code=404, detail="Configuration Item not found")

    return ci.to_dict()


@router.delete("/configuration-items/{ci_id}")
async def delete_ci(ci_id: int, db: Session = Depends(get_db)):
    """Delete a Configuration Item and its children."""
    service = ConfigurationItemService(db)

    if not service.delete_ci(ci_id):
        raise HTTPException(status_code=404, detail="Configuration Item not found")

    return {"message": "Configuration Item deleted", "ci_id": ci_id}


@router.get("/configuration-items/{ci_id}/children")
async def get_ci_children(ci_id: int, db: Session = Depends(get_db)):
    """Get children of a Configuration Item."""
    service = ConfigurationItemService(db)
    ci = service.get_ci_by_id(ci_id)

    if not ci:
        raise HTTPException(status_code=404, detail="Configuration Item not found")

    children = service.db.query(service.db.query(ConfigurationItemService).filter(
        ConfigurationItemService.parent_id == ci_id
    )).all()

    # Direct query for children
    from models.configuration_item import ConfigurationItem
    children = service.db.query(ConfigurationItem).filter(
        ConfigurationItem.parent_id == ci_id
    ).order_by(ConfigurationItem.ci_identifier).all()

    return {
        "parent_id": ci_id,
        "children": [child.to_dict() for child in children]
    }


@router.get("/configuration-items/{ci_id}/classify")
async def classify_ci(ci_id: int, db: Session = Depends(get_db)):
    """
    Classify a Configuration Item.

    Traceability: REQ-AI-040 - CI Classification
    """
    service = ConfigurationItemService(db)
    classification = service.classify_ci(ci_id)

    if "error" in classification:
        raise HTTPException(status_code=404, detail=classification["error"])

    return classification


# ==================== BOM Endpoints ====================

@router.post("/configuration-items/{ci_id}/bom", status_code=status.HTTP_201_CREATED)
async def add_bom_entry(
    ci_id: int,
    bom_data: BOMCreate,
    db: Session = Depends(get_db)
):
    """
    Add a BOM entry for a Configuration Item.

    Traceability: REQ-DB-039 - Store BOM relationships
    """
    service = ConfigurationItemService(db)

    # Verify parent CI exists and matches
    if bom_data.parent_ci_id != ci_id:
        raise HTTPException(status_code=400, detail="Parent CI ID mismatch")

    parent = service.get_ci_by_id(ci_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Parent CI not found")

    child = service.get_ci_by_id(bom_data.child_ci_id)
    if not child:
        raise HTTPException(status_code=404, detail="Child CI not found")

    try:
        bom_type = BOMType(bom_data.bom_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid BOM type: {bom_data.bom_type}")

    bom = service.add_bom_entry(
        parent_ci_id=ci_id,
        child_ci_id=bom_data.child_ci_id,
        quantity=bom_data.quantity,
        bom_type=bom_type,
        unit_of_measure=bom_data.unit_of_measure,
        position_reference=bom_data.position_reference,
        find_number=bom_data.find_number,
        is_alternate=bom_data.is_alternate,
        notes=bom_data.notes
    )

    return bom.to_dict()


@router.get("/configuration-items/{ci_id}/bom")
async def get_ci_bom(
    ci_id: int,
    bom_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get BOM entries for a Configuration Item."""
    service = ConfigurationItemService(db)

    type_enum = None
    if bom_type:
        try:
            type_enum = BOMType(bom_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid BOM type: {bom_type}")

    bom_entries = service.get_bom_for_ci(ci_id, bom_type=type_enum)

    return {
        "parent_ci_id": ci_id,
        "bom_entries": [entry.to_dict() for entry in bom_entries]
    }


@router.get("/configuration-items/{ci_id}/where-used")
async def get_where_used(ci_id: int, db: Session = Depends(get_db)):
    """Get where a CI is used (reverse BOM lookup)."""
    service = ConfigurationItemService(db)

    where_used = service.get_where_used(ci_id)

    return {
        "ci_id": ci_id,
        "used_in": [entry.to_dict() for entry in where_used]
    }


@router.delete("/bom/{bom_id}")
async def delete_bom_entry(bom_id: int, db: Session = Depends(get_db)):
    """Delete a BOM entry."""
    service = ConfigurationItemService(db)

    if not service.delete_bom_entry(bom_id):
        raise HTTPException(status_code=404, detail="BOM entry not found")

    return {"message": "BOM entry deleted", "bom_id": bom_id}


# ==================== Statistics ====================

@router.get("/projects/{project_id}/ci-statistics")
async def get_ci_statistics(project_id: int, db: Session = Depends(get_db)):
    """Get CI statistics for a project."""
    service = ConfigurationItemService(db)
    stats = service.get_project_ci_statistics(project_id)

    return {
        "project_id": project_id,
        **stats
    }


# ==================== Process Engine Integration ====================

class StateMachineCreate(BaseModel):
    """Schema for creating a state machine for a CI."""
    dal_level: Optional[str] = None
    auto_start: bool = True


@router.post("/configuration-items/{ci_id}/state-machine")
async def create_ci_state_machine(
    ci_id: int,
    request: StateMachineCreate,
    db: Session = Depends(get_db)
):
    """
    Create a development process state machine for a Configuration Item.

    Traceability: REQ-SM-001 to REQ-SM-006

    This creates an executable process instance based on the CI's type and criticality.
    For example, a SOFTWARE CI with DAL_B criticality gets a DO-178C DAL B process.
    """
    service = ConfigurationItemService(db)

    result = service.create_state_machine_for_ci_item(
        ci_id=ci_id,
        dal_level=request.dal_level,
        auto_start=request.auto_start
    )

    if not result:
        raise HTTPException(
            status_code=400,
            detail="Failed to create state machine. CI may not exist or process template may be missing."
        )

    return result


@router.get("/configuration-items/{ci_id}/state-machine")
async def get_ci_state_machine(ci_id: int, db: Session = Depends(get_db)):
    """
    Get the state machine instance for a CI.

    Returns the complete state machine with all phases, sub-phases, and activities.
    """
    service = ConfigurationItemService(db)

    sm_data = service.get_ci_state_machine(ci_id)

    if not sm_data:
        raise HTTPException(
            status_code=404,
            detail=f"No state machine found for CI {ci_id}. Create one first."
        )

    return sm_data


@router.get("/configuration-items/{ci_id}/current-activity")
async def get_ci_current_activity(ci_id: int, db: Session = Depends(get_db)):
    """
    Get the current activity that should be worked on for this CI.

    Returns:
        - Current phase, sub-phase, and activity information
        - What needs to be done next
        - Required outputs/artifacts
    """
    service = ConfigurationItemService(db)

    activity = service.get_ci_current_activity(ci_id)

    if not activity:
        raise HTTPException(
            status_code=404,
            detail=f"No current activity for CI {ci_id}. The process may be complete or not started."
        )

    return activity


@router.get("/configuration-items/{ci_id}/progress")
async def get_ci_progress(ci_id: int, db: Session = Depends(get_db)):
    """
    Get progress information for a CI's development process.

    Returns:
        - Overall completion percentage
        - Phase progress
        - Activity completion counts
        - Current phase/activity
    """
    service = ConfigurationItemService(db)

    progress = service.get_ci_progress(ci_id)

    if not progress:
        raise HTTPException(
            status_code=404,
            detail=f"No process found for CI {ci_id}. Create a state machine first."
        )

    return progress


class ActivityComplete(BaseModel):
    """Schema for completing an activity."""
    activity_id: str
    completion_data: Optional[dict] = None


class ActivitySkip(BaseModel):
    """Schema for skipping an activity."""
    activity_id: str
    reason: str


@router.post("/configuration-items/{ci_id}/complete-activity")
async def complete_activity(
    ci_id: int,
    request: ActivityComplete,
    db: Session = Depends(get_db)
):
    """
    Mark an activity as complete and advance the state machine.

    Traceability: REQ-SM-003 (Activity sequencing)

    This endpoint:
    - Marks the specified activity as complete
    - Stores optional completion data (artifacts, notes, etc.)
    - Advances the state machine to the next activity
    - Updates progress percentages
    """
    service = ConfigurationItemService(db)

    result = service.complete_activity(
        ci_id=ci_id,
        activity_id=request.activity_id,
        completion_data=request.completion_data
    )

    if not result:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to complete activity. Activity may not exist or is not current."
        )

    return result


@router.post("/configuration-items/{ci_id}/skip-activity")
async def skip_activity(
    ci_id: int,
    request: ActivitySkip,
    db: Session = Depends(get_db)
):
    """
    Skip an optional activity.

    Traceability: REQ-SM-003 (Activity optional/required)

    This endpoint:
    - Skips the specified optional activity
    - Records the reason for skipping
    - Advances the state machine to the next activity
    - Cannot skip required activities
    """
    service = ConfigurationItemService(db)

    result = service.skip_activity(
        ci_id=ci_id,
        activity_id=request.activity_id,
        reason=request.reason
    )

    if not result:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to skip activity. Activity may be required or not found."
        )

    return result


# ==================== Activity-Interview Integration ====================

@router.get("/configuration-items/{ci_id}/activity/{activity_id}/interview-status")
async def get_activity_interview_status(
    ci_id: int,
    activity_id: str,
    db: Session = Depends(get_db)
):
    """
    Get interview status for an activity.

    Returns:
        - Whether activity has an associated interview
        - Interview script ID if available
        - Whether interview is required
    """
    service = ActivityInterviewService(db)
    status = service.get_activity_interview_status(ci_id, activity_id)
    return status


@router.post("/configuration-items/{ci_id}/activity/{activity_id}/start-interview")
async def start_activity_interview(
    ci_id: int,
    activity_id: str,
    db: Session = Depends(get_db)
):
    """
    Start an interview for a specific activity.

    Traceability: REQ-SM-003, REQ-IS-001

    This endpoint:
    - Checks if activity has an associated interview
    - Creates interview session
    - Returns interview state for frontend
    """
    service = ActivityInterviewService(db)

    result = service.start_interview_for_activity(ci_id, activity_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No interview available for activity {activity_id} or activity not current."
        )

    return result


class InterviewCompletionData(BaseModel):
    """Schema for completing activity with interview data."""
    interview_results: dict


@router.post("/configuration-items/{ci_id}/activity/{activity_id}/complete-with-interview")
async def complete_activity_with_interview(
    ci_id: int,
    activity_id: str,
    request: InterviewCompletionData,
    db: Session = Depends(get_db)
):
    """
    Complete an activity using interview results.

    Traceability: REQ-SM-003, REQ-IS-008

    This endpoint:
    - Takes interview results as input
    - Extracts relevant data for activity completion
    - Marks activity as complete
    - Advances state machine
    """
    service = ActivityInterviewService(db)

    result = service.complete_activity_with_interview_data(
        ci_id=ci_id,
        activity_id=activity_id,
        interview_results=request.interview_results
    )

    if not result:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to complete activity with interview data."
        )

    return result


@router.get("/activity-interview-mappings")
async def list_activity_interview_mappings():
    """
    List all activity-to-interview mappings.

    Returns:
        Dictionary of activity types to interview script IDs
    """
    mappings = ActivityInterviewService.list_activity_interview_mappings()
    return {
        "mappings": mappings,
        "total": len(mappings)
    }
