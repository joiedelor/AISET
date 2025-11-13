"""
Users Router
DO-178C Traceability: REQ-API-010
Purpose: User authentication and management endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db

router = APIRouter()


@router.get("/users")
async def list_users(db: Session = Depends(get_db)):
    """
    List all users.

    Traceability: REQ-AUTH-002 - User listing
    """
    return {"message": "Users endpoint - to be implemented"}
