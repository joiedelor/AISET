"""
AISET Process Engine

The Process Engine is the core of AISET's "Codification of the Systems Engineer".
It provides deterministic, executable development processes based on standards
like ARP4754A, DO-178C, and DO-254.

Key Components:
- Process Templates: JSON definitions of development processes
- State Machine Generator: Creates executable state machines from templates
- State Machine Controller: Manages execution of state machines
- Interview Script Executor: Executes structured interview scripts
- Data Capture Service: Validates, transforms, and stores captured data
- Artifact Generator: Generates documents from Jinja2 templates

Philosophy:
- AISET-AI is NOT an intelligent decision-maker
- AISET-AI is a rigorous process executor
- AI is OPTIONAL - only used for natural language polish
"""

from .services.state_machine_generator import (
    StateMachineGenerator,
    StateMachineController,
    StateMachineInstance,
    ProcessTemplateLoader,
    CIType,
    PhaseStatus,
    ActivityStatus,
    create_state_machine_for_ci,
    list_available_processes,
)

from .services.interview_executor import (
    InterviewScriptExecutor,
    InterviewState,
    Question,
    AnswerResult,
    list_available_scripts,
    create_interview,
)

from .services.data_capture import (
    DataCaptureService,
    AutoPopulationService,
    ValidationResult,
    CaptureResult,
    StorageTarget,
    validate_answer,
    transform_answer,
)

from .services.artifact_generator import (
    ArtifactGeneratorService,
    GeneratedDocument,
    generate_document,
    list_available_templates,
)

__all__ = [
    # State Machine
    "StateMachineGenerator",
    "StateMachineController",
    "StateMachineInstance",
    "ProcessTemplateLoader",
    "CIType",
    "PhaseStatus",
    "ActivityStatus",
    "create_state_machine_for_ci",
    "list_available_processes",
    # Interview Executor
    "InterviewScriptExecutor",
    "InterviewState",
    "Question",
    "AnswerResult",
    "list_available_scripts",
    "create_interview",
    # Data Capture
    "DataCaptureService",
    "AutoPopulationService",
    "ValidationResult",
    "CaptureResult",
    "StorageTarget",
    "validate_answer",
    "transform_answer",
    # Artifact Generator
    "ArtifactGeneratorService",
    "GeneratedDocument",
    "generate_document",
    "list_available_templates",
]

__version__ = "1.0.0"
