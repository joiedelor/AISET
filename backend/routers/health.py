"""
Health Check Router
DO-178C Traceability: REQ-API-002
Purpose: System health and status endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from config.settings import settings

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Check application health status.

    Traceability: REQ-MONITOR-001 - System monitoring
    """
    # Test database connection
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "operational",
        "version": settings.app_version,
        "database": db_status,
        "ai_service": settings.ai_service,
        "do178c_compliance": {
            "audit_trail": settings.enable_audit_trail,
            "approval_workflow": settings.require_approval_workflow,
            "traceability_strict": settings.traceability_strict_mode
        }
    }


@router.get("/version")
async def get_version():
    """Get application version information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "api_version": "v1"
    }
