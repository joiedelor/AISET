"""
Documents Router
DO-178C Traceability: REQ-API-007
Purpose: Document generation and export endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from services.document_service import DocumentService

router = APIRouter()


@router.post("/projects/{project_id}/generate-srs")
async def generate_srs(
    project_id: int,
    generated_by: str = "system",
    db: Session = Depends(get_db)
):
    """
    Generate Software Requirements Specification (SRS).

    Traceability: REQ-DOC-005 - SRS generation API
    """
    service = DocumentService(db)

    try:
        export = service.generate_srs(project_id, generated_by)

        return {
            "document_id": export.id,
            "file_path": export.file_path,
            "file_hash": export.file_hash,
            "generated_at": export.generated_at
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/generate-rtm")
async def generate_rtm(
    project_id: int,
    generated_by: str = "system",
    db: Session = Depends(get_db)
):
    """
    Generate Requirements Traceability Matrix (RTM).

    Traceability: REQ-DOC-006 - RTM generation API
    """
    service = DocumentService(db)

    try:
        export = service.generate_rtm(project_id, generated_by)

        return {
            "document_id": export.id,
            "file_path": export.file_path,
            "file_hash": export.file_hash,
            "generated_at": export.generated_at
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
