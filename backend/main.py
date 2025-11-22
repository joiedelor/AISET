"""
AISET FastAPI Application
DO-178C Traceability: REQ-APP-001
Purpose: Main application entry point

This is the main FastAPI application that orchestrates all services,
routers, and middleware for the AISET system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config.settings import settings
from database.connection import init_db

# Import routers
from routers import (
    projects,
    requirements,
    design_components,
    test_cases,
    ai_conversation,
    traceability,
    documents,
    users,
    health,
    approval
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Traceability: REQ-APP-002 - Application lifecycle management
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Systems Engineering Tool - DO-178C Compliant Requirements Management",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(projects.router, prefix="/api/v1", tags=["Projects"])
app.include_router(requirements.router, prefix="/api/v1", tags=["Requirements"])
app.include_router(design_components.router, prefix="/api/v1", tags=["Design"])
app.include_router(test_cases.router, prefix="/api/v1", tags=["Tests"])
app.include_router(ai_conversation.router, prefix="/api/v1", tags=["AI"])
app.include_router(approval.router, prefix="/api/v1/approval", tags=["Approval Workflow"])
app.include_router(traceability.router, prefix="/api/v1", tags=["Traceability"])
app.include_router(documents.router, prefix="/api/v1", tags=["Documents"])


@app.get("/")
async def root():
    """
    Root endpoint.

    Traceability: REQ-APP-003 - API documentation
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
        "do178c_compliance": "enabled" if settings.enable_audit_trail else "disabled"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
