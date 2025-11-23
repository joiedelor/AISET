"""
Process Engine API Router

Provides REST API endpoints for the Process Engine functionality:
- Interview script execution
- State machine management
- Document generation
- Progress tracking

Traceability: REQ-SM-001 to REQ-SM-006, REQ-IS-001 to REQ-IS-008, REQ-AG-001 to REQ-AG-005
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

from database.connection import get_db
from sqlalchemy.orm import Session

# Import process engine components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from process_engine import (
    InterviewScriptExecutor,
    InterviewState,
    list_available_scripts,
    create_interview,
    DataCaptureService,
    ArtifactGeneratorService,
    generate_document,
    list_available_templates,
    StateMachineGenerator,
    StateMachineController,
    create_state_machine_for_ci,
    list_available_processes,
    CIType,
)


router = APIRouter(prefix="/process-engine", tags=["Process Engine"])


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class QuestionResponse(BaseModel):
    """Response containing a question to display"""
    question_id: str
    text: str
    help_text: Optional[str] = None
    data_type: str
    options: List[Dict[str, Any]] = []
    required: bool = True


class AnswerRequest(BaseModel):
    """Request to submit an answer"""
    question_id: str
    answer: Any
    project_id: Optional[int] = None


class AnswerResponse(BaseModel):
    """Response after processing an answer"""
    valid: bool
    error: Optional[str] = None
    next_question: Optional[QuestionResponse] = None
    context_updates: Dict[str, Any] = {}
    phase_complete: bool = False
    progress: Optional[Dict[str, Any]] = None


class InterviewSessionResponse(BaseModel):
    """Response with interview session info"""
    session_id: str
    script_id: str
    current_question: QuestionResponse
    progress: Dict[str, Any]


class DocumentGenerateRequest(BaseModel):
    """Request to generate a document"""
    project_id: int
    document_type: str  # SRS, RTM, GAP_ANALYSIS


class DocumentResponse(BaseModel):
    """Response with generated document"""
    document_id: str
    document_type: str
    title: str
    content: str
    version: int
    generated_at: datetime
    status: str


class StateMachineCreateRequest(BaseModel):
    """Request to create a state machine for a CI"""
    ci_id: int
    ci_type: str
    dal_level: Optional[str] = None


class StateMachineResponse(BaseModel):
    """Response with state machine info"""
    instance_id: str
    ci_id: int
    ci_type: str
    template_name: str
    current_phase_index: int
    overall_progress: float
    phases: List[Dict[str, Any]]


# =============================================================================
# INTERVIEW SCRIPT ENDPOINTS
# =============================================================================

# In-memory session storage (use Redis/DB in production)
_interview_sessions: Dict[str, Dict] = {}


@router.get("/interviews/scripts", response_model=List[Dict])
async def list_interview_scripts():
    """
    List all available interview scripts.

    Returns list of scripts with their metadata.
    """
    return list_available_scripts()


@router.post("/interviews/start/{script_name}", response_model=InterviewSessionResponse)
async def start_interview(
    script_name: str,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Start a new interview session.

    Args:
        script_name: Name of the interview script (e.g., "project_initialization")
        project_id: Optional project ID to associate with

    Returns:
        Interview session with first question
    """
    try:
        # Create executor
        executor = create_interview(script_name, db)

        # Create initial state
        state = executor.create_initial_state()

        # Get first question
        first_question = executor.get_first_question(state.context)

        # Generate session ID
        import uuid
        session_id = str(uuid.uuid4())

        # Store session
        _interview_sessions[session_id] = {
            "executor": executor,
            "state": state,
            "project_id": project_id
        }

        # Get progress
        progress = executor.get_progress(state)

        return InterviewSessionResponse(
            session_id=session_id,
            script_id=state.script_id,
            current_question=QuestionResponse(
                question_id=first_question.question_id,
                text=first_question.text,
                help_text=first_question.help_text,
                data_type=first_question.data_type,
                options=first_question.options,
                required=first_question.required
            ),
            progress=progress
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Interview script '{script_name}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interviews/{session_id}/answer", response_model=AnswerResponse)
async def submit_answer(
    session_id: str,
    request: AnswerRequest,
    db: Session = Depends(get_db)
):
    """
    Submit an answer to the current question.

    Args:
        session_id: Interview session ID
        request: Answer request with question_id and answer

    Returns:
        Result with next question or completion status
    """
    # Get session
    session = _interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    executor: InterviewScriptExecutor = session["executor"]
    state: InterviewState = session["state"]
    project_id = request.project_id or session.get("project_id")

    # Process answer
    result = executor.process_answer(
        question_id=request.question_id,
        answer=request.answer,
        context=state.context,
        project_id=project_id
    )

    if not result.valid:
        return AnswerResponse(
            valid=False,
            error=result.error,
            progress=executor.get_progress(state)
        )

    # Update state
    state = executor.update_state(state, request.question_id, result)
    session["state"] = state

    # Get next question if not complete
    next_question = None
    if result.next_question_id:
        try:
            q = executor.get_question(result.next_question_id, state.context)
            next_question = QuestionResponse(
                question_id=q.question_id,
                text=q.text,
                help_text=q.help_text,
                data_type=q.data_type,
                options=q.options,
                required=q.required
            )
        except Exception:
            pass

    return AnswerResponse(
        valid=True,
        next_question=next_question,
        context_updates=result.context_updates,
        phase_complete=result.phase_complete,
        progress=executor.get_progress(state)
    )


@router.get("/interviews/{session_id}/progress")
async def get_interview_progress(session_id: str):
    """
    Get progress information for an interview session.
    """
    session = _interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    executor = session["executor"]
    state = session["state"]

    return executor.get_progress(state)


@router.get("/interviews/{session_id}/context")
async def get_interview_context(session_id: str):
    """
    Get current context (collected data) for an interview session.
    """
    session = _interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    return session["state"].context


@router.delete("/interviews/{session_id}")
async def end_interview(session_id: str):
    """
    End an interview session.
    """
    if session_id in _interview_sessions:
        del _interview_sessions[session_id]
        return {"status": "session ended"}

    raise HTTPException(status_code=404, detail="Interview session not found")


# =============================================================================
# DOCUMENT GENERATION ENDPOINTS
# =============================================================================

@router.get("/documents/templates", response_model=List[Dict])
async def list_document_templates():
    """
    List available document templates.
    """
    return list_available_templates()


@router.post("/documents/generate", response_model=DocumentResponse)
async def generate_doc(
    request: DocumentGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a document from a template.

    Args:
        request: Document generation request with project_id and document_type

    Returns:
        Generated document
    """
    try:
        doc = generate_document(
            project_id=request.project_id,
            doc_type=request.document_type,
            db_session=db
        )

        return DocumentResponse(
            document_id=doc.document_id,
            document_type=doc.document_type,
            title=doc.title,
            content=doc.content,
            version=doc.version,
            generated_at=doc.generated_at,
            status=doc.status
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/generate/{project_id}/{doc_type}")
async def generate_doc_get(
    project_id: int,
    doc_type: str,
    db: Session = Depends(get_db)
):
    """
    Generate a document (GET version for convenience).
    """
    try:
        doc = generate_document(
            project_id=project_id,
            doc_type=doc_type,
            db_session=db
        )

        return {
            "document_id": doc.document_id,
            "document_type": doc.document_type,
            "title": doc.title,
            "content": doc.content,
            "version": doc.version,
            "generated_at": doc.generated_at.isoformat(),
            "status": doc.status
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# STATE MACHINE ENDPOINTS
# =============================================================================

@router.get("/processes/templates", response_model=List[Dict])
async def list_process_templates():
    """
    List available process templates.
    """
    return list_available_processes()


@router.post("/state-machines", response_model=StateMachineResponse)
async def create_state_machine(request: StateMachineCreateRequest):
    """
    Create a state machine for a Configuration Item.

    Args:
        request: CI information

    Returns:
        Created state machine
    """
    try:
        ci_type = CIType(request.ci_type)

        sm = create_state_machine_for_ci(
            ci_id=request.ci_id,
            ci_type=request.ci_type,
            dal_level=request.dal_level
        )

        controller = StateMachineController(sm)
        progress = controller.get_overall_progress()

        return StateMachineResponse(
            instance_id=sm.instance_id,
            ci_id=sm.ci_id,
            ci_type=sm.ci_type.value,
            template_name=sm.template_name,
            current_phase_index=sm.current_phase_index,
            overall_progress=sm.overall_progress,
            phases=progress["phases"]
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ci-types")
async def list_ci_types():
    """
    List available CI types.
    """
    return [{"value": t.value, "label": t.value.replace("_", " ").title()} for t in CIType]


# =============================================================================
# DATA VALIDATION ENDPOINT
# =============================================================================

@router.post("/validate")
async def validate_data(
    value: Any = Query(...),
    rules: List[Dict] = []
):
    """
    Validate a value against rules.

    Useful for frontend validation before submission.
    """
    service = DataCaptureService()
    errors = service.validate(value, rules)

    return {
        "valid": len(errors) == 0,
        "errors": [{"error": e.error, "field": e.field} for e in errors]
    }
