"""
Traceability Router
DO-178C Traceability: REQ-API-006
Purpose: Traceability management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.connection import get_db
from services.traceability_service import TraceabilityService
from models.traceability import TraceType

router = APIRouter()


class CreateTrace(BaseModel):
    """Schema for creating a trace link."""
    requirement_id: int
    design_component_id: int = None
    test_case_id: int = None
    trace_type: TraceType = TraceType.MANUAL
    rationale: str = None
    created_by: str = "system"


@router.post("/traceability/requirement-design")
async def create_requirement_design_trace(
    trace: CreateTrace,
    db: Session = Depends(get_db)
):
    """
    Create traceability link between requirement and design.

    Traceability: REQ-TRACE-015 - Trace creation API
    """
    if not trace.design_component_id:
        raise HTTPException(status_code=400, detail="design_component_id is required")

    service = TraceabilityService(db)

    try:
        db_trace = service.create_requirement_design_trace(
            requirement_id=trace.requirement_id,
            design_component_id=trace.design_component_id,
            trace_type=trace.trace_type,
            rationale=trace.rationale,
            created_by=trace.created_by
        )

        return {
            "trace_id": db_trace.id,
            "requirement_id": db_trace.requirement_id,
            "design_component_id": db_trace.design_component_id
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/traceability/requirement-test")
async def create_requirement_test_trace(
    trace: CreateTrace,
    db: Session = Depends(get_db)
):
    """
    Create traceability link between requirement and test.

    Traceability: REQ-TRACE-016 - Test trace creation API
    """
    if not trace.test_case_id:
        raise HTTPException(status_code=400, detail="test_case_id is required")

    service = TraceabilityService(db)

    try:
        db_trace = service.create_requirement_test_trace(
            requirement_id=trace.requirement_id,
            test_case_id=trace.test_case_id,
            trace_type=trace.trace_type,
            coverage_notes=trace.rationale,
            created_by=trace.created_by
        )

        return {
            "trace_id": db_trace.id,
            "requirement_id": db_trace.requirement_id,
            "test_case_id": db_trace.test_case_id
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/requirements/{requirement_id}/coverage")
async def get_requirement_coverage(
    requirement_id: int,
    db: Session = Depends(get_db)
):
    """
    Get coverage analysis for a requirement.

    Traceability: REQ-TRACE-017 - Coverage API
    """
    service = TraceabilityService(db)

    try:
        coverage = service.get_requirement_coverage(requirement_id)
        return coverage
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects/{project_id}/traceability-matrix")
async def get_traceability_matrix(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate complete traceability matrix.

    Traceability: REQ-TRACE-018 - Matrix generation API
    """
    service = TraceabilityService(db)

    try:
        matrix = service.generate_traceability_matrix(project_id)
        return matrix
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/detect-gaps")
async def detect_gaps(project_id: int, db: Session = Depends(get_db)):
    """
    Detect traceability gaps in a project.

    Traceability: REQ-TRACE-019 - Gap detection API
    """
    service = TraceabilityService(db)

    try:
        gaps = service.detect_gaps(project_id)
        return {
            "project_id": project_id,
            "gaps_found": len(gaps),
            "gaps": [
                {
                    "type": gap.gap_type.value,
                    "severity": gap.severity,
                    "description": gap.description
                }
                for gap in gaps
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
