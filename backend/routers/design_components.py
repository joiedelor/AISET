"""
Design Components Router
DO-178C Traceability: REQ-API-008
Purpose: Design component management endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db

router = APIRouter()


@router.get("/design-components")
async def list_design_components(db: Session = Depends(get_db)):
    """
    List all design components.

    Traceability: REQ-DESIGN-002 - Design listing
    """
    return {"message": "Design components endpoint - to be implemented"}
