"""
Projects Router
DO-178C Traceability: REQ-API-003
Purpose: Project management endpoints including initialization interview
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from database.connection import get_db
from models.project import Project, ProjectInitializationContext
from services.ai_service import ai_service

router = APIRouter()


class ProjectCreate(BaseModel):
    """Schema for creating a project."""
    name: str
    description: str = None
    project_code: str
    certification_level: str = "C"
    industry: str = None
    created_by: str = "system"


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: int
    name: str
    description: str = None
    project_code: str
    certification_level: str
    status: str
    created_by: str

    class Config:
        from_attributes = True


@router.post("/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    Create a new project.

    Traceability: REQ-PROJ-002 - Project creation
    """
    # Check if project code already exists
    existing = db.query(Project).filter(Project.project_code == project.project_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project code already exists")

    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    List all projects with optional filtering.

    Traceability: REQ-PROJ-003 - Project listing
    """
    query = db.query(Project)

    if status:
        query = query.filter(Project.status == status)

    projects = query.all()
    return projects


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    Get a specific project by ID.

    Traceability: REQ-PROJ-004 - Project retrieval
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


class InitializationRequest(BaseModel):
    """Schema for project initialization interview request."""
    project_id: Optional[int] = None
    user_input: str
    context: Optional[Dict[str, Any]] = None


class InitializationResponse(BaseModel):
    """Schema for project initialization interview response."""
    next_question: str
    stage: str
    complete: bool
    project_id: Optional[int] = None
    context: Dict[str, Any]


@router.post("/projects/initialize", response_model=InitializationResponse)
async def initialize_project(
    request: InitializationRequest,
    db: Session = Depends(get_db)
):
    """
    Conduct project initialization interview using AI.

    Traceability:
    - REQ-AI-032: Structured project interview
    - REQ-AI-033: Safety criticality determination
    - REQ-AI-034: Regulatory standards identification
    - REQ-AI-035: Development process selection
    - REQ-AI-036: Tool configuration
    - REQ-AI-037: Context storage

    The interview proceeds through stages:
    1. Initial: Open-ended project description
    2. Foundation: Safety criticality, DAL/SIL, domain, product type
    3. Planning: Regulatory standards, dev process, architecture
    4. Execution: Lifecycle phase, verification, team size
    5. Complete: Summary and confirmation
    """
    try:
        # Get or create project
        project = None
        if request.project_id:
            project = db.query(Project).filter(Project.id == request.project_id).first()
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")

        # Conduct interview
        interview_result = await ai_service.project_initialization_interview(
            user_input=request.user_input,
            context=request.context
        )

        # If interview is complete and we have a project, update it
        if interview_result["complete"] and project:
            # Extract collected data from context
            collected_data = request.context.get("data", {}) if request.context else {}

            # Update project fields
            if "safety_critical" in collected_data:
                project.safety_critical = collected_data["safety_critical"]
            if "dal_level" in collected_data:
                project.dal_level = collected_data["dal_level"]
            if "sil_level" in collected_data:
                project.sil_level = collected_data["sil_level"]
            if "domain" in collected_data:
                project.domain = collected_data["domain"]
                project.industry = collected_data["domain"]  # Update legacy field
            if "product_type" in collected_data:
                project.product_type = collected_data["product_type"]
            if "architecture_type" in collected_data:
                project.architecture_type = collected_data["architecture_type"]
            if "requirements_source" in collected_data:
                project.requirements_source = collected_data["requirements_source"]

            # Store complete context in JSON field (REQ-AI-037)
            project.initialization_context = {
                "interview_complete": True,
                "stage": interview_result["stage"],
                "collected_data": collected_data,
                "model_used": interview_result["model"]
            }

            db.commit()
            db.refresh(project)

        # Build response context
        response_context = request.context or {"stage": "initial", "data": {}}
        response_context["stage"] = interview_result["stage"]

        return InitializationResponse(
            next_question=interview_result["next_question"],
            stage=interview_result["stage"],
            complete=interview_result["complete"],
            project_id=project.id if project else None,
            context=response_context
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initialization error: {str(e)}")
