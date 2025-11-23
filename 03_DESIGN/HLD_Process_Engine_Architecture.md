# AISET - Process Engine High-Level Design

**Document Type:** [Level 1] AISET Tool Development - DO-178C DAL D
**Document Version:** 1.0.0
**Last Updated:** 2025-11-23
**Status:** Draft
**Parent Document:** HLD_High_Level_Design.md v1.2.0
**Requirements Document:** SRS_Process_Engine_Requirements.md v1.0.0

---

## Document Control

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2025-11-23 | Claude + User | Initial creation - Codification of Systems Engineer |

---

## 1. Introduction

### 1.1 Purpose

This document specifies the high-level design for the AISET **Process Engine** - the core component that codifies the systems engineering process into deterministic, executable logic.

### 1.2 Design Philosophy

**The Process Engine replaces "AI intelligence" with "process knowledge".**

| Traditional AI Approach | AISET Process Engine Approach |
|------------------------|------------------------------|
| AI decides what to ask | Script defines what to ask |
| AI interprets responses | Rules parse and validate responses |
| AI generates documents | Templates generate documents |
| AI is required | AI is optional (for polish only) |
| Behavior is probabilistic | Behavior is deterministic |
| Hard to verify | Easy to verify |
| DO-178C compliance difficult | DO-178C compliance straightforward |

### 1.3 Scope

This design covers:
- Process Engine component architecture
- State Machine implementation
- Interview Script framework
- Data Capture pipeline
- Artifact Generation system
- Integration with existing AISET components

---

## 2. Architecture Overview

### 2.1 Process Engine Position in AISET Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           AISET SYSTEM                                      │
│                                                                             │
│  ┌──────────────────┐     ┌──────────────────────────────────────────────┐ │
│  │     Frontend     │     │              BACKEND                          │ │
│  │     (React)      │     │  ┌────────────────────────────────────────┐  │ │
│  │                  │     │  │         PROCESS ENGINE                  │  │ │
│  │  - Chat UI       │◀───▶│  │  ┌──────────┐  ┌──────────────────┐   │  │ │
│  │  - Document View │     │  │  │  State   │  │  Interview       │   │  │ │
│  │  - Progress      │     │  │  │  Machine │──│  Script Executor │   │  │ │
│  │    Indicators    │     │  │  └──────────┘  └──────────────────┘   │  │ │
│  │                  │     │  │       │                │               │  │ │
│  └──────────────────┘     │  │       ▼                ▼               │  │ │
│                           │  │  ┌──────────┐  ┌──────────────────┐   │  │ │
│                           │  │  │  Data    │  │  Artifact        │   │  │ │
│                           │  │  │  Capture │  │  Generator       │   │  │ │
│                           │  │  └──────────┘  └──────────────────┘   │  │ │
│                           │  └────────────────────────────────────────┘  │ │
│                           │                    │                          │ │
│                           │  ┌─────────────────┼─────────────────────┐   │ │
│                           │  │                 ▼                     │   │ │
│                           │  │  ┌──────────────────────────────┐    │   │ │
│                           │  │  │  NLP Wrapper (OPTIONAL)      │    │   │ │
│                           │  │  │  - Question rephrasing       │    │   │ │
│                           │  │  │  - Answer interpretation     │    │   │ │
│                           │  │  │  - Uses Claude/LM Studio     │    │   │ │
│                           │  │  └──────────────────────────────┘    │   │ │
│                           │  │            AI ENGINE LAYER            │   │ │
│                           │  └───────────────────────────────────────┘   │ │
│                           └──────────────────────────────────────────────┘ │
│                                               │                             │
│                                               ▼                             │
│                           ┌──────────────────────────────────────────────┐ │
│                           │              PostgreSQL Database              │ │
│                           │  - Interview state    - Generated documents   │ │
│                           │  - Captured data      - Traceability links    │ │
│                           │  - Phase progress     - Audit trail           │ │
│                           └──────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

| Component | Responsibility | Dependencies |
|-----------|---------------|--------------|
| **State Machine** | Control process flow, phase management, transition validation | Interview Scripts |
| **Interview Script Executor** | Load scripts, select questions, handle conditions | State Machine, Data Capture |
| **Data Capture** | Validate input, transform data, write to database | Database |
| **Artifact Generator** | Load templates, query data, render documents | Database |
| **NLP Wrapper** | (Optional) Rephrase questions, interpret answers | AI Engine |

---

## 3. State Machine Design

### 3.1 State Machine Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         STATE MACHINE CONTROLLER                          │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │                    PHASE STATE MACHINE                             │   │
│  │                                                                    │   │
│  │    ┌──────────┐     ┌──────────┐     ┌──────────┐                │   │
│  │    │ PROJECT  │────▶│ REQUIRE- │────▶│ REQUIRE- │                │   │
│  │    │ INIT     │     │ MENTS    │     │ MENTS    │                │   │
│  │    │          │     │ ELICIT   │     │ ANALYSIS │                │   │
│  │    └──────────┘     └──────────┘     └──────────┘                │   │
│  │         │                │                │                       │   │
│  │         │                │                ▼                       │   │
│  │         │                │          ┌──────────┐                  │   │
│  │         │                │          │ ARCH     │                  │   │
│  │         │                │          │ DEFINE   │                  │   │
│  │         │                │          └──────────┘                  │   │
│  │         │                │                │                       │   │
│  │         │                │                ▼                       │   │
│  │         │                │          ┌──────────┐                  │   │
│  │         │                │          │ DETAIL   │                  │   │
│  │         │                │          │ DESIGN   │                  │   │
│  │         │                │          └──────────┘                  │   │
│  │         │                │                │                       │   │
│  │         │                │                ▼                       │   │
│  │         │                │          ┌──────────┐     ┌─────────┐ │   │
│  │         │                │          │ VERIF    │────▶│ CERTIF  │ │   │
│  │         │                └─────────▶│ PLANNING │     │ PREP    │ │   │
│  │         │                           └──────────┘     └─────────┘ │   │
│  │         │                                                         │   │
│  │         └────────────────────────(Rollback paths)─────────────────│   │
│  │                                                                    │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │                   SUB-PHASE STATE MACHINES                         │   │
│  │                                                                    │   │
│  │  Each phase contains a sub-phase state machine:                    │   │
│  │                                                                    │   │
│  │  PROJECT_INIT:                                                     │   │
│  │  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐           │   │
│  │  │ INITIAL │──▶│ DOMAIN  │──▶│ SAFETY  │──▶│ STAND-  │──▶...     │   │
│  │  │ DESCR   │   │ IDENT   │   │ CRITIC  │   │ ARDS    │           │   │
│  │  └─────────┘   └─────────┘   └─────────┘   └─────────┘           │   │
│  │                                                                    │   │
│  └───────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
```

### 3.2 State Machine Data Model

```python
# backend/models/process_state.py

from enum import Enum
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class Phase(str, Enum):
    PROJECT_INITIALIZATION = "project_initialization"
    REQUIREMENTS_ELICITATION = "requirements_elicitation"
    REQUIREMENTS_ANALYSIS = "requirements_analysis"
    ARCHITECTURE_DEFINITION = "architecture_definition"
    DETAILED_DESIGN = "detailed_design"
    IMPLEMENTATION_TRACKING = "implementation_tracking"
    VERIFICATION_PLANNING = "verification_planning"
    VERIFICATION_EXECUTION = "verification_execution"
    CONFIGURATION_MANAGEMENT = "configuration_management"
    CERTIFICATION_PREPARATION = "certification_preparation"

class SubPhase(str, Enum):
    # PROJECT_INITIALIZATION sub-phases
    PI_INITIAL_DESCRIPTION = "pi_initial_description"
    PI_DOMAIN_IDENTIFICATION = "pi_domain_identification"
    PI_SAFETY_CRITICALITY = "pi_safety_criticality"
    PI_DAL_SIL_DETERMINATION = "pi_dal_sil_determination"
    PI_STANDARDS_IDENTIFICATION = "pi_standards_identification"
    PI_PROCESS_SELECTION = "pi_process_selection"
    PI_TEAM_CONTEXT = "pi_team_context"
    PI_COMPLETE = "pi_complete"

    # REQUIREMENTS_ELICITATION sub-phases
    RE_CAPTURE_REQUIREMENT = "re_capture_requirement"
    RE_CLASSIFY_REQUIREMENT = "re_classify_requirement"
    RE_ALLOCATE_REQUIREMENT = "re_allocate_requirement"
    RE_TRACE_REQUIREMENT = "re_trace_requirement"
    RE_CONFIRM_MORE = "re_confirm_more"
    RE_COMPLETE = "re_complete"

    # ... (additional sub-phases for other phases)

class ProcessState(BaseModel):
    """
    Current state of the process engine for a project.
    Persisted to database after every interaction.
    """
    project_id: int
    current_phase: Phase
    current_sub_phase: SubPhase

    # Question tracking within current sub-phase
    current_question_id: str
    questions_answered: List[str]
    questions_skipped: List[str]
    questions_remaining: List[str]

    # Phase completion tracking
    phases_completed: List[Phase]
    phase_completion_data: Dict[Phase, Dict]  # Completion criteria data

    # Context for conditional logic
    context: Dict[str, any]  # Accumulated answers for conditional branching

    # Timestamps
    phase_started_at: datetime
    last_interaction_at: datetime

    # Session tracking
    session_id: str
    user_id: int
```

### 3.3 State Transition Logic

```python
# backend/services/state_machine.py

class StateMachineController:
    """
    Controls process flow through phases and sub-phases.
    """

    def __init__(self, project_id: int):
        self.project_id = project_id
        self.state = self._load_state()
        self.transitions = self._load_transition_rules()

    def get_current_question(self) -> Question:
        """
        Get the next question to ask based on current state.
        """
        script = self._get_script(self.state.current_sub_phase)
        question = script.get_question(
            self.state.current_question_id,
            self.state.context
        )
        return question

    def process_answer(self, answer: str) -> ProcessResult:
        """
        Process user answer, update state, determine next action.
        """
        # Validate answer
        validation_result = self._validate_answer(answer)
        if not validation_result.valid:
            return ProcessResult(
                success=False,
                error=validation_result.error,
                retry=True
            )

        # Store answer
        self._store_answer(answer)

        # Update context
        self.state.context[self.state.current_question_id] = answer

        # Determine next question or sub-phase
        next_action = self._determine_next(answer)

        if next_action.type == "next_question":
            self.state.current_question_id = next_action.question_id
        elif next_action.type == "next_sub_phase":
            self._transition_sub_phase(next_action.sub_phase)
        elif next_action.type == "next_phase":
            self._transition_phase(next_action.phase)
        elif next_action.type == "phase_complete":
            self._mark_phase_complete()

        # Persist state
        self._save_state()

        return ProcessResult(
            success=True,
            next_question=self.get_current_question(),
            phase=self.state.current_phase,
            progress=self._calculate_progress()
        )

    def _check_phase_preconditions(self, target_phase: Phase) -> bool:
        """
        Check if preconditions for phase transition are met.
        """
        preconditions = {
            Phase.REQUIREMENTS_ELICITATION: [
                lambda: self.state.context.get("project_name") is not None,
                lambda: self.state.context.get("assurance_level") is not None,
            ],
            Phase.REQUIREMENTS_ANALYSIS: [
                lambda: self._count_requirements() >= 1,
            ],
            Phase.ARCHITECTURE_DEFINITION: [
                lambda: self._all_requirements_classified(),
            ],
            # ... more preconditions
        }

        for precondition in preconditions.get(target_phase, []):
            if not precondition():
                return False
        return True
```

---

## 4. Interview Script Framework

### 4.1 Script Structure

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        INTERVIEW SCRIPT STRUCTURE                           │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      interview_scripts/                               │  │
│  │  ├── project_initialization/                                          │  │
│  │  │   ├── script.json           # Main script definition               │  │
│  │  │   ├── questions/                                                   │  │
│  │  │   │   ├── PI-001.json       # Individual question definitions      │  │
│  │  │   │   ├── PI-002.json                                              │  │
│  │  │   │   └── ...                                                      │  │
│  │  │   └── conditions.json       # Conditional logic rules              │  │
│  │  │                                                                    │  │
│  │  ├── requirements_elicitation/                                        │  │
│  │  │   ├── script.json                                                  │  │
│  │  │   ├── questions/                                                   │  │
│  │  │   └── conditions.json                                              │  │
│  │  │                                                                    │  │
│  │  ├── design_capture/                                                  │  │
│  │  │   └── ...                                                          │  │
│  │  │                                                                    │  │
│  │  └── verification_planning/                                           │  │
│  │      └── ...                                                          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Question Definition Format

```json
// interview_scripts/project_initialization/questions/PI-004.json
{
  "question_id": "PI-004",
  "phase": "PROJECT_INITIALIZATION",
  "sub_phase": "PI_SAFETY_CRITICALITY",
  "order": 4,

  "variants": [
    "Is this a safety-critical system?",
    "Does this system have safety implications?",
    "Could a failure of this system cause harm to people or property?",
    "Are there safety requirements for this system?"
  ],

  "help_text": "A safety-critical system is one where a failure could result in death, injury, or significant property damage.",

  "data_type": "selection",
  "options": [
    {"value": "yes", "label": "Yes, it is safety-critical"},
    {"value": "no", "label": "No, it is not safety-critical"},
    {"value": "unknown", "label": "I'm not sure"}
  ],

  "required": true,

  "validation": {
    "allowed_values": ["yes", "no", "unknown"]
  },

  "target": {
    "table": "projects",
    "column": "is_safety_critical",
    "transformation": "boolean_from_yes_no"
  },

  "on_answer": {
    "yes": {
      "next_question": "PI-005",
      "set_context": {"is_safety_critical": true}
    },
    "no": {
      "next_question": "PI-007",
      "set_context": {"is_safety_critical": false},
      "auto_set": [
        {"table": "projects", "column": "assurance_level", "value": null}
      ]
    },
    "unknown": {
      "next_question": "PI-004-CLARIFY",
      "set_context": {"safety_needs_clarification": true}
    }
  }
}
```

### 4.3 Interview Script Executor

```python
# backend/services/interview_script_executor.py

import json
import random
from pathlib import Path
from typing import Dict, Optional

class InterviewScriptExecutor:
    """
    Loads and executes interview scripts.
    """

    SCRIPTS_PATH = Path("interview_scripts")

    def __init__(self, phase: str):
        self.phase = phase
        self.script = self._load_script()
        self.questions = self._load_questions()
        self.conditions = self._load_conditions()

    def get_question(self, question_id: str, context: Dict) -> Question:
        """
        Get a question definition, applying context-based conditions.
        """
        question_def = self.questions.get(question_id)
        if not question_def:
            raise ValueError(f"Question {question_id} not found")

        # Check skip conditions
        if self._should_skip(question_id, context):
            return self._get_next_question(question_id, context)

        # Select variant (random or sequential)
        variant_text = self._select_variant(question_def)

        # Build question object
        return Question(
            question_id=question_id,
            text=variant_text,
            help_text=question_def.get("help_text"),
            data_type=question_def["data_type"],
            options=self._apply_context_to_options(
                question_def.get("options", []),
                context
            ),
            required=question_def.get("required", True),
            validation=question_def.get("validation", {})
        )

    def process_answer(self, question_id: str, answer: str, context: Dict) -> AnswerResult:
        """
        Process an answer and determine next action.
        """
        question_def = self.questions[question_id]

        # Validate answer
        if not self._validate_answer(answer, question_def):
            return AnswerResult(
                valid=False,
                error=self._get_validation_error(answer, question_def)
            )

        # Transform answer for storage
        transformed = self._transform_answer(answer, question_def)

        # Determine storage target
        target = question_def["target"]

        # Determine next action based on answer
        on_answer = question_def.get("on_answer", {})
        answer_action = on_answer.get(answer) or on_answer.get("default", {})

        return AnswerResult(
            valid=True,
            storage_target=StorageTarget(
                table=target["table"],
                column=target["column"],
                value=transformed
            ),
            next_question=answer_action.get("next_question"),
            context_updates=answer_action.get("set_context", {}),
            auto_sets=answer_action.get("auto_set", [])
        )

    def _select_variant(self, question_def: Dict) -> str:
        """
        Select a question variant. Can be random or context-aware.
        """
        variants = question_def.get("variants", [])
        if not variants:
            return question_def.get("text", "")

        # For now, use random selection
        # In future, could use context to select most appropriate variant
        return random.choice(variants)

    def _apply_context_to_options(self, options: list, context: Dict) -> list:
        """
        Filter or modify options based on context.
        E.g., Show DAL options only for Aerospace projects.
        """
        filtered = []
        for option in options:
            condition = option.get("condition")
            if condition:
                if not self._evaluate_condition(condition, context):
                    continue
            filtered.append(option)
        return filtered
```

---

## 5. Data Capture Pipeline

### 5.1 Data Flow

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         DATA CAPTURE PIPELINE                               │
│                                                                             │
│  User Answer                                                                │
│      │                                                                      │
│      ▼                                                                      │
│  ┌──────────────────┐                                                       │
│  │  1. VALIDATION   │◀─────────────────────────────────────────────┐       │
│  │  - Type check    │                                               │       │
│  │  - Required      │                                               │       │
│  │  - Pattern       │──Invalid──▶ Return error + retry              │       │
│  │  - Range         │                                               │       │
│  └────────┬─────────┘                                               │       │
│           │ Valid                                                   │       │
│           ▼                                                         │       │
│  ┌──────────────────┐                                               │       │
│  │  2. TRANSFORM    │                                               │       │
│  │  - Type convert  │                                               │       │
│  │  - Normalize     │                                               │       │
│  │  - Generate IDs  │                                               │       │
│  └────────┬─────────┘                                               │       │
│           │                                                         │       │
│           ▼                                                         │       │
│  ┌──────────────────┐                                               │       │
│  │  3. STORAGE      │                                               │       │
│  │  - Map to table  │                                               │       │
│  │  - Map to column │                                               │       │
│  │  - Execute SQL   │──Constraint violation──▶ Return error ────────┘       │
│  └────────┬─────────┘                                                       │
│           │ Success                                                         │
│           ▼                                                                 │
│  ┌──────────────────┐                                                       │
│  │  4. POST-STORE   │                                                       │
│  │  - Create traces │                                                       │
│  │  - Update state  │                                                       │
│  │  - Trigger hooks │                                                       │
│  └──────────────────┘                                                       │
└────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Data Capture Service

```python
# backend/services/data_capture.py

from typing import Dict, Any, List
from dataclasses import dataclass
import re

@dataclass
class StorageTarget:
    table: str
    column: str
    value: Any

@dataclass
class ValidationRule:
    rule_type: str  # required, min_length, max_length, pattern, allowed_values, etc.
    params: Dict

class DataCaptureService:
    """
    Handles validation, transformation, and storage of captured data.
    """

    TRANSFORMATIONS = {
        "boolean_from_yes_no": lambda x: x.lower() == "yes",
        "uppercase": lambda x: x.upper(),
        "lowercase": lambda x: x.lower(),
        "strip": lambda x: x.strip(),
        "to_int": lambda x: int(x),
        "to_float": lambda x: float(x),
        "array_from_csv": lambda x: [i.strip() for i in x.split(",")],
    }

    def validate(self, value: str, rules: List[ValidationRule]) -> ValidationResult:
        """
        Validate input against all defined rules.
        """
        for rule in rules:
            result = self._apply_validation_rule(value, rule)
            if not result.valid:
                return result
        return ValidationResult(valid=True)

    def _apply_validation_rule(self, value: str, rule: ValidationRule) -> ValidationResult:
        """
        Apply a single validation rule.
        """
        if rule.rule_type == "required":
            if not value or not value.strip():
                return ValidationResult(
                    valid=False,
                    error="This field is required"
                )

        elif rule.rule_type == "min_length":
            if len(value) < rule.params["min"]:
                return ValidationResult(
                    valid=False,
                    error=f"Must be at least {rule.params['min']} characters"
                )

        elif rule.rule_type == "max_length":
            if len(value) > rule.params["max"]:
                return ValidationResult(
                    valid=False,
                    error=f"Must be no more than {rule.params['max']} characters"
                )

        elif rule.rule_type == "pattern":
            pattern = rule.params["pattern"]
            if not re.match(pattern, value):
                return ValidationResult(
                    valid=False,
                    error=rule.params.get("error", f"Must match pattern: {pattern}")
                )

        elif rule.rule_type == "allowed_values":
            if value not in rule.params["values"]:
                return ValidationResult(
                    valid=False,
                    error=f"Must be one of: {', '.join(rule.params['values'])}"
                )

        elif rule.rule_type == "shall_statement":
            # DO-178C requirement format validation
            if "shall" not in value.lower():
                return ValidationResult(
                    valid=False,
                    error="Requirement must contain 'shall' statement"
                )
            if " and " in value.lower() and value.count("shall") > 1:
                return ValidationResult(
                    valid=False,
                    error="Split compound requirements: only one 'shall' per requirement"
                )

        return ValidationResult(valid=True)

    def transform(self, value: str, transformation: str) -> Any:
        """
        Transform input value according to transformation rule.
        """
        if transformation in self.TRANSFORMATIONS:
            return self.TRANSFORMATIONS[transformation](value)
        return value

    def store(self, target: StorageTarget, context: Dict) -> StorageResult:
        """
        Store value in database.
        """
        # Build SQL based on target
        # This is simplified - actual implementation uses SQLAlchemy

        if self._is_update(target, context):
            return self._update_record(target, context)
        else:
            return self._insert_record(target, context)

    def create_traceability_links(self, source: str, targets: List[str], link_type: str):
        """
        Create traceability links between artifacts.
        """
        for target in targets:
            self._create_trace_link(source, target, link_type)
```

### 5.3 Automatic Field Population

```python
# backend/services/auto_population.py

import uuid
from datetime import datetime
from typing import Dict, Any

class AutoPopulationService:
    """
    Automatically populate fields based on rules.
    """

    def populate_defaults(self, table: str, data: Dict) -> Dict:
        """
        Add auto-populated fields to data before insert.
        """
        # Common audit fields
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        data["version"] = 1

        # GUID for hybrid ID system
        if "guid" not in data:
            data["guid"] = str(uuid.uuid4())

        # Table-specific auto-population
        if table == "requirements":
            data = self._populate_requirement_fields(data)
        elif table == "configuration_items":
            data = self._populate_ci_fields(data)
        elif table == "design_components":
            data = self._populate_design_fields(data)

        return data

    def _populate_requirement_fields(self, data: Dict) -> Dict:
        """
        Auto-populate requirement-specific fields.
        """
        # Generate requirement ID
        if "requirement_id" not in data:
            req_type = data.get("type", "FN")[:2].upper()
            next_num = self._get_next_sequence("requirement", req_type)
            data["requirement_id"] = f"REQ-{req_type}-{next_num:03d}"

        # Default status
        if "status" not in data:
            data["status"] = "draft"

        # Default display ID same as requirement_id
        if "display_id" not in data:
            data["display_id"] = data["requirement_id"]

        return data

    def _populate_ci_fields(self, data: Dict) -> Dict:
        """
        Auto-populate CI-specific fields.
        """
        # Generate display ID
        if "display_id" not in data:
            ci_type = data.get("type", "").upper()[:2] or "CI"
            next_num = self._get_next_sequence("ci", ci_type)
            data["display_id"] = f"CI-{ci_type}-{next_num:04d}"

        # Default lifecycle phase
        if "lifecycle_phase" not in data:
            data["lifecycle_phase"] = "development"

        # Default baseline status
        if "baseline_status" not in data:
            data["baseline_status"] = "none"

        return data
```

---

## 6. Artifact Generation System

### 6.1 Template Engine Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        ARTIFACT GENERATION SYSTEM                           │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      document_templates/                              │  │
│  │  ├── SRS_template.md           # Software Requirements Spec          │  │
│  │  ├── HLD_template.md           # High-Level Design                   │  │
│  │  ├── LLD_template.md           # Low-Level Design                    │  │
│  │  ├── RTM_template.md           # Requirements Traceability Matrix    │  │
│  │  ├── CI_List_template.md       # Configuration Item List             │  │
│  │  ├── Test_Plan_template.md     # Test Plan                           │  │
│  │  └── Gap_Analysis_template.md  # Gap Analysis Report                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│                              │                                              │
│                              ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    TEMPLATE ENGINE (Jinja2)                           │  │
│  │                                                                       │  │
│  │  1. Load template                                                     │  │
│  │  2. Query database for data                                           │  │
│  │  3. Apply filters and sorting                                         │  │
│  │  4. Render Markdown                                                   │  │
│  │  5. Save or return document                                           │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│                              │                                              │
│                              ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     GENERATED DOCUMENTS                               │  │
│  │                                                                       │  │
│  │  - Stored in database (documents table)                               │  │
│  │  - Marked with generation timestamp                                   │  │
│  │  - Linked to source data                                              │  │
│  │  - Can be exported as .md, .pdf, .docx                               │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Template Format (Example: SRS)

```markdown
{# document_templates/SRS_template.md #}

# Software Requirements Specification
## {{ project.name }}

---

## Document Control

| Item | Value |
|------|-------|
| Document ID | {{ project.display_id }}-SRS-001 |
| Version | {{ document.version }} |
| Date | {{ document.generated_at | date }} |
| Status | Generated - Needs Review |
| Project | {{ project.name }} |
| DAL/SIL | {{ project.assurance_level or "N/A" }} |

---

## 1. Introduction

### 1.1 Purpose

This document specifies the software requirements for {{ project.name }}.

### 1.2 Scope

{{ project.description }}

### 1.3 Applicable Standards

{% for standard in project.standards %}
- {{ standard.name }} ({{ standard.version }})
{% endfor %}

---

## 2. Functional Requirements

{% for req in requirements | selectattr("type", "equalto", "functional") | sort(attribute="requirement_id") %}

### {{ req.requirement_id }}: {{ req.title or "Untitled" }}

**Statement:** {{ req.description }}

**Priority:** {{ req.priority }}

**Rationale:** {{ req.rationale or "Not specified" }}

**Verification Method:** {{ req.verification_method or "Test" }}

**Status:** {{ req.status }}

---

{% endfor %}

## 3. Performance Requirements

{% for req in requirements | selectattr("type", "equalto", "performance") | sort(attribute="requirement_id") %}
### {{ req.requirement_id }}: {{ req.title or "Untitled" }}

**Statement:** {{ req.description }}

**Priority:** {{ req.priority }}

---

{% endfor %}

{# Continue for other requirement types... #}

## Appendix A: Requirements Summary

| Req ID | Type | Priority | Status |
|--------|------|----------|--------|
{% for req in requirements | sort(attribute="requirement_id") %}
| {{ req.requirement_id }} | {{ req.type }} | {{ req.priority }} | {{ req.status }} |
{% endfor %}

---

**Generated by AISET Process Engine**
**Generation timestamp:** {{ document.generated_at | datetime }}
```

### 6.3 Artifact Generator Service

```python
# backend/services/artifact_generator.py

from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import datetime

class ArtifactGeneratorService:
    """
    Generates documents from templates and database data.
    """

    TEMPLATES_PATH = Path("document_templates")

    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(self.TEMPLATES_PATH),
            autoescape=False  # We're generating Markdown, not HTML
        )
        self._register_filters()

    def generate_srs(self, project_id: int) -> GeneratedDocument:
        """
        Generate Software Requirements Specification.
        """
        # Load data
        project = self._get_project(project_id)
        requirements = self._get_requirements(project_id)
        standards = self._get_project_standards(project_id)

        # Load and render template
        template = self.env.get_template("SRS_template.md")
        content = template.render(
            project=project,
            requirements=requirements,
            standards=standards,
            document={
                "version": self._get_next_doc_version(project_id, "SRS"),
                "generated_at": datetime.utcnow()
            }
        )

        # Store document
        doc = self._store_document(
            project_id=project_id,
            doc_type="SRS",
            content=content,
            source_data_hash=self._hash_source_data(requirements)
        )

        return doc

    def generate_traceability_matrix(self, project_id: int) -> GeneratedDocument:
        """
        Generate Requirements Traceability Matrix.
        """
        # Query traceability data
        traces = self._get_traceability_data(project_id)
        gaps = self._identify_gaps(project_id)

        template = self.env.get_template("RTM_template.md")
        content = template.render(
            project=self._get_project(project_id),
            traces=traces,
            gaps=gaps,
            coverage=self._calculate_coverage(traces),
            document={"generated_at": datetime.utcnow()}
        )

        return self._store_document(project_id, "RTM", content)

    def generate_gap_analysis(self, project_id: int) -> GeneratedDocument:
        """
        Generate Gap Analysis Report.
        """
        gaps = {
            "requirements_without_design": self._find_unallocated_requirements(project_id),
            "design_without_requirements": self._find_orphan_design(project_id),
            "requirements_without_tests": self._find_untested_requirements(project_id),
            "orphan_tests": self._find_orphan_tests(project_id),
            "cis_without_requirements": self._find_unallocated_cis(project_id)
        }

        template = self.env.get_template("Gap_Analysis_template.md")
        content = template.render(
            project=self._get_project(project_id),
            gaps=gaps,
            summary=self._summarize_gaps(gaps),
            document={"generated_at": datetime.utcnow()}
        )

        return self._store_document(project_id, "GAP_ANALYSIS", content)

    def _register_filters(self):
        """
        Register custom Jinja2 filters.
        """
        self.env.filters["date"] = lambda d: d.strftime("%Y-%m-%d") if d else ""
        self.env.filters["datetime"] = lambda d: d.strftime("%Y-%m-%d %H:%M:%S UTC") if d else ""
```

---

## 7. NLP Wrapper (Optional AI Layer)

### 7.1 NLP Wrapper Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    NLP WRAPPER (OPTIONAL COMPONENT)                         │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        NLPWrapper Service                             │  │
│  │                                                                       │  │
│  │  ┌─────────────────────────────────────────────────────────────┐     │  │
│  │  │  rephrase_question(question, context) -> str                │     │  │
│  │  │  - Takes script question + context                          │     │  │
│  │  │  - Returns natural language variant                         │     │  │
│  │  │  - Falls back to original if AI unavailable                 │     │  │
│  │  └─────────────────────────────────────────────────────────────┘     │  │
│  │                                                                       │  │
│  │  ┌─────────────────────────────────────────────────────────────┐     │  │
│  │  │  interpret_answer(question, answer) -> StructuredData       │     │  │
│  │  │  - Takes free-text answer                                   │     │  │
│  │  │  - Extracts structured data for storage                     │     │  │
│  │  │  - Returns parsed fields for user confirmation              │     │  │
│  │  └─────────────────────────────────────────────────────────────┘     │  │
│  │                                                                       │  │
│  │  ┌─────────────────────────────────────────────────────────────┐     │  │
│  │  │  explain_validation_error(error, context) -> str            │     │  │
│  │  │  - Takes validation error                                   │     │  │
│  │  │  - Returns user-friendly explanation                        │     │  │
│  │  │  - Falls back to original error message                     │     │  │
│  │  └─────────────────────────────────────────────────────────────┘     │  │
│  │                                                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Mode: ENABLED | DISABLED | FALLBACK_ON_ERROR                              │
│                                                                             │
│  When DISABLED: System uses script questions directly, no AI calls         │
└────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 NLP Wrapper Implementation

```python
# backend/services/nlp_wrapper.py

from typing import Optional, Dict, Any
from enum import Enum

class NLPMode(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    FALLBACK_ON_ERROR = "fallback_on_error"

class NLPWrapper:
    """
    Optional AI layer for natural language polish.
    System works fully without this component.
    """

    def __init__(self, mode: NLPMode = NLPMode.DISABLED, ai_service=None):
        self.mode = mode
        self.ai_service = ai_service

    def rephrase_question(self, question: str, context: Dict) -> str:
        """
        Rephrase a script question more naturally.
        Returns original question if AI disabled or unavailable.
        """
        if self.mode == NLPMode.DISABLED:
            return question

        try:
            prompt = f"""
            Rephrase this question naturally based on context.
            Keep the same meaning. Use simple language.

            Question: {question}
            Context: Project is about {context.get('project_description', 'unknown')}.
            Industry: {context.get('industry', 'unknown')}.

            Rephrased question:
            """

            response = self.ai_service.generate(prompt, max_tokens=100)
            return response.strip() or question

        except Exception as e:
            if self.mode == NLPMode.FALLBACK_ON_ERROR:
                return question
            raise

    def interpret_free_text(
        self,
        question_context: str,
        answer: str,
        expected_fields: Dict
    ) -> InterpretationResult:
        """
        Interpret free-text answer to extract structured data.
        Returns extracted fields for user confirmation.
        """
        if self.mode == NLPMode.DISABLED:
            # Return answer as-is in a single field
            return InterpretationResult(
                fields={"raw_text": answer},
                confidence=1.0,
                needs_confirmation=False
            )

        try:
            prompt = f"""
            Extract structured data from this answer.

            Question context: {question_context}
            Answer: {answer}

            Expected fields: {expected_fields}

            Return JSON with extracted fields and confidence (0-1).
            """

            response = self.ai_service.generate(prompt, max_tokens=500)
            parsed = self._parse_json_response(response)

            return InterpretationResult(
                fields=parsed.get("fields", {}),
                confidence=parsed.get("confidence", 0.5),
                needs_confirmation=True  # Always confirm AI interpretations
            )

        except Exception as e:
            if self.mode == NLPMode.FALLBACK_ON_ERROR:
                return InterpretationResult(
                    fields={"raw_text": answer},
                    confidence=1.0,
                    needs_confirmation=False
                )
            raise
```

---

## 8. Database Schema Extensions

### 8.1 Process State Tables

```sql
-- Tables for Process Engine state persistence

-- Process state for each project
CREATE TABLE process_states (
    id SERIAL PRIMARY KEY,
    guid UUID NOT NULL DEFAULT gen_random_uuid(),
    project_id INT NOT NULL REFERENCES projects(id),

    -- Current position in state machine
    current_phase VARCHAR(50) NOT NULL,
    current_sub_phase VARCHAR(50) NOT NULL,
    current_question_id VARCHAR(20),

    -- Question tracking
    questions_answered JSONB NOT NULL DEFAULT '[]',
    questions_skipped JSONB NOT NULL DEFAULT '[]',

    -- Phase completion
    phases_completed JSONB NOT NULL DEFAULT '[]',
    phase_completion_data JSONB NOT NULL DEFAULT '{}',

    -- Context for conditional logic
    context JSONB NOT NULL DEFAULT '{}',

    -- Timestamps
    phase_started_at TIMESTAMP WITH TIME ZONE,
    last_interaction_at TIMESTAMP WITH TIME ZONE,

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    UNIQUE(project_id)
);

-- Interview answers history (for audit trail)
CREATE TABLE interview_answers (
    id SERIAL PRIMARY KEY,
    guid UUID NOT NULL DEFAULT gen_random_uuid(),
    project_id INT NOT NULL REFERENCES projects(id),

    -- Question info
    phase VARCHAR(50) NOT NULL,
    sub_phase VARCHAR(50) NOT NULL,
    question_id VARCHAR(20) NOT NULL,
    question_text TEXT NOT NULL,

    -- Answer info
    answer_raw TEXT NOT NULL,
    answer_transformed JSONB,

    -- Storage info
    target_table VARCHAR(100),
    target_column VARCHAR(100),
    target_record_id INT,

    -- Validation
    validation_passed BOOLEAN NOT NULL,
    validation_errors JSONB,

    -- User info
    answered_by INT REFERENCES users(id),
    answered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- NLP interpretation (if used)
    nlp_interpretation JSONB,
    user_confirmed BOOLEAN DEFAULT TRUE
);

-- Generated documents tracking
CREATE TABLE generated_documents (
    id SERIAL PRIMARY KEY,
    guid UUID NOT NULL DEFAULT gen_random_uuid(),
    project_id INT NOT NULL REFERENCES projects(id),

    -- Document info
    document_type VARCHAR(50) NOT NULL,  -- SRS, HLD, RTM, etc.
    version INT NOT NULL DEFAULT 1,
    content TEXT NOT NULL,

    -- Generation metadata
    template_version VARCHAR(20),
    source_data_hash VARCHAR(64),  -- To detect if regeneration needed

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'draft',  -- draft, needs_review, approved

    -- Timestamps
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by INT REFERENCES users(id),

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Index for quick state lookup
CREATE INDEX idx_process_states_project ON process_states(project_id);
CREATE INDEX idx_interview_answers_project ON interview_answers(project_id);
CREATE INDEX idx_generated_documents_project ON generated_documents(project_id, document_type);
```

---

## 9. Traceability

### 9.1 Requirements to Design Traceability

| Requirement | HLD Section | Implementation |
|-------------|-------------|----------------|
| REQ-SM-001 | Section 3.1 | State Machine Architecture |
| REQ-SM-002 | Section 3.3 | Phase Preconditions |
| REQ-SM-003 | Section 3.1, 3.2 | Sub-phase State Machines |
| REQ-SM-004 | Section 3.2, 8.1 | State Persistence |
| REQ-IS-001 | Section 4.1, 4.2 | Script Structure |
| REQ-IS-002 | Section 4.2 | Project Initialization Script |
| REQ-IS-003 | Section 4.2 | Requirements Script |
| REQ-IS-007 | Section 4.2, 4.3 | Conditional Flow |
| REQ-DC-001 | Section 5.2 | Answer-to-Database Mapping |
| REQ-DC-002 | Section 5.2 | Validation Rules |
| REQ-DC-003 | Section 5.3 | Auto-population |
| REQ-AG-001 | Section 6.1, 6.2 | Template Engine |
| REQ-AG-004 | Section 6.3 | Traceability Matrix |
| REQ-NL-001 | Section 7.1, 7.2 | NLP Wrapper |
| REQ-NL-002 | Section 7.2 | Fallback Behavior |

---

## 10. Open Issues

1. **Script Management UI** - How will scripts be edited? JSON editor? GUI?
2. **Script Versioning** - How to version interview scripts?
3. **Multi-language Support** - How to support question variants in multiple languages?
4. **Template Customization** - Can users customize document templates?
5. **Performance** - Need to benchmark with large number of questions/requirements

---

**END OF PROCESS ENGINE HIGH-LEVEL DESIGN**

---

**Document Status:** Draft
**Next Steps:**
1. Review with user
2. Implement interview script JSON files
3. Build state machine controller
4. Create data capture pipeline
5. Build template engine
6. Test without AI (NLP disabled mode)
