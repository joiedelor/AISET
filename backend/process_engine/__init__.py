"""
AISET Process Engine

The Process Engine is the core of AISET's "Codification of the Systems Engineer".
It provides deterministic, executable development processes based on standards
like ARP4754A, DO-178C, and DO-254.

Key Components:
- Process Templates: JSON definitions of development processes
- State Machine Generator: Creates executable state machines from templates
- State Machine Controller: Manages execution of state machines

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

__all__ = [
    "StateMachineGenerator",
    "StateMachineController",
    "StateMachineInstance",
    "ProcessTemplateLoader",
    "CIType",
    "PhaseStatus",
    "ActivityStatus",
    "create_state_machine_for_ci",
    "list_available_processes",
]

__version__ = "1.0.0"
