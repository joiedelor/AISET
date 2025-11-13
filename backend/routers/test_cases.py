"""
Test Cases Router
DO-178C Traceability: REQ-API-009
Purpose: Test case management endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db

router = APIRouter()


@router.get("/test-cases")
async def list_test_cases(db: Session = Depends(get_db)):
    """
    List all test cases.

    Traceability: REQ-TEST-002 - Test listing
    """
    return {"message": "Test cases endpoint - to be implemented"}
