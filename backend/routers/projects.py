"""
Projects Router
DO-178C Traceability: REQ-API-003
Purpose: Project management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database.connection import get_db
from models.project import Project

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
