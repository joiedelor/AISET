# Software Requirements Specification - Process Engine
## AISET - AI Systems Engineering Tool

---

## Document Control Information

| Item | Value |
|------|-------|
| **Document ID** | AISET-SRS-PE-001 |
| **Document Title** | Process Engine Requirements Specification |
| **Version** | 1.0.0 |
| **Date** | 2025-11-23 |
| **Status** | Draft |
| **Parent Document** | AISET-SRS-001 (Main SRS v1.2.0) |
| **DO-178C Compliance** | Section 5.1 - Software High-Level Requirements |
| **DAL Level** | D (Tool Development) |

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2025-11-23 | Claude + User | Initial creation - Codification of Systems Engineer Process |

---

## 1. Introduction

### 1.1 Purpose

This document specifies the requirements for the AISET **Process Engine** - the core component that codifies the systems engineering process. The Process Engine replaces "AI intelligence" with deterministic, standards-based process execution.

### 1.2 Philosophy: Codification of the Systems Engineer

**Key Insight:** The AISET-AI is NOT an intelligent decision-maker. It is a **rigorous process executor**.

The "intelligence" consists of:
1. **Asking the RIGHT question at the RIGHT time** (following predefined interview scripts)
2. **Listening and capturing** what the human says
3. **Structuring/organizing** captured data according to standards (DO-178C, ARP4754A)
4. **Maintaining configuration** - IDs, versions, traceability links, baselines
5. **Never forgetting** - persistent, complete, consistent records

**The HUMAN does:**
- All creative work (design decisions, architecture choices)
- All technical judgment (safety analysis, trade-offs)
- All approvals (nothing auto-committed)

### 1.3 Scope

This specification covers:
- Process Engine State Machine
- Interview Script Framework
- Data Capture and Validation
- Process Phase Management
- Artifact Generation Rules
- Configuration Management Automation

### 1.4 Relationship to Main SRS

This document extends AISET-SRS-001. Requirements here are numbered REQ-PE-xxx (Process Engine), REQ-SM-xxx (State Machine), REQ-DC-xxx (Data Capture), and REQ-IS-xxx (Interview Scripts).

---

## 2. Process Engine Overview

### 2.1 Core Concept

The Process Engine is a **deterministic state machine** that:
1. Knows exactly what information to collect at each phase
2. Knows exactly what questions to ask
3. Knows exactly where to store captured data
4. Knows exactly what artifacts to generate
5. Knows exactly what validations to apply

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PROCESS ENGINE ARCHITECTURE                     │
│                                                                      │
│  ┌──────────────────┐    ┌──────────────────┐    ┌───────────────┐ │
│  │  Interview       │    │  State Machine   │    │  Data         │ │
│  │  Scripts         │───▶│  Controller      │───▶│  Capture      │ │
│  │  (What to ask)   │    │  (Process flow)  │    │  (Storage)    │ │
│  └──────────────────┘    └──────────────────┘    └───────────────┘ │
│           │                       │                      │          │
│           ▼                       ▼                      ▼          │
│  ┌──────────────────┐    ┌──────────────────┐    ┌───────────────┐ │
│  │  NLP Wrapper     │    │  Validation      │    │  Artifact     │ │
│  │  (Optional AI)   │    │  Engine          │    │  Generator    │ │
│  │  (Rephrasing)    │    │  (Rules)         │    │  (Templates)  │ │
│  └──────────────────┘    └──────────────────┘    └───────────────┘ │
│                                                                      │
│                          ▼                                          │
│                    ┌──────────────────┐                             │
│                    │    PostgreSQL    │                             │
│                    │    Database      │                             │
│                    └──────────────────┘                             │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Process Engine vs AI Engine

| Aspect | Process Engine (Deterministic) | AI Engine (Stochastic) |
|--------|-------------------------------|------------------------|
| **What questions to ask** | Hardcoded scripts | N/A |
| **What order to ask** | State machine | N/A |
| **Where to store data** | Schema mapping | N/A |
| **Validation rules** | Coded rules | N/A |
| **Question phrasing** | Optional | AI rephrases naturally |
| **Handling unexpected input** | Optional | AI interprets |
| **Document generation** | Templates | AI fills content |

**The AI is OPTIONAL** - only needed for natural language polish.

---

## 3. State Machine Requirements (REQ-SM-xxx)

### REQ-SM-001: Development Lifecycle State Machine

**Statement:** The Process Engine shall implement a state machine representing the complete systems engineering development lifecycle with the following phases:

1. **PROJECT_INITIALIZATION** - Project context capture
2. **REQUIREMENTS_ELICITATION** - System and software requirements capture
3. **REQUIREMENTS_ANALYSIS** - Requirements decomposition and refinement
4. **ARCHITECTURE_DEFINITION** - High-level design decisions
5. **DETAILED_DESIGN** - Low-level design capture
6. **IMPLEMENTATION_TRACKING** - Code implementation status
7. **VERIFICATION_PLANNING** - Test planning and case definition
8. **VERIFICATION_EXECUTION** - Test execution and results
9. **CONFIGURATION_MANAGEMENT** - Baseline and change management
10. **CERTIFICATION_PREPARATION** - Compliance evidence gathering

**Priority:** CRITICAL

**Rationale:** Codifies the ARP4754A/DO-178C development process. Each phase has specific data to capture and artifacts to produce.

**Verification Method:** Test (state transitions)

**Source:** ARP4754A Process Model + Discussion 2025-11-23

---

### REQ-SM-002: Phase Preconditions

**Statement:** Each phase transition shall have defined preconditions that must be satisfied before entering the next phase:

| From Phase | To Phase | Preconditions |
|------------|----------|---------------|
| PROJECT_INIT | REQ_ELICITATION | Project context captured (name, DAL/SIL, standards) |
| REQ_ELICITATION | REQ_ANALYSIS | At least 1 requirement captured |
| REQ_ANALYSIS | ARCH_DEFINITION | Requirements classified and prioritized |
| ARCH_DEFINITION | DETAILED_DESIGN | HLD components defined |
| DETAILED_DESIGN | IMPLEMENTATION | LLD components defined |
| VERIFICATION_PLANNING | VERIFICATION_EXEC | Test cases linked to requirements |
| Any phase | CERTIFICATION_PREP | All verification complete |

**Priority:** HIGH

**Rationale:** Ensures process discipline - cannot skip phases without completing required work.

**Verification Method:** Test (precondition validation)

**Source:** DO-178C Process Objectives

---

### REQ-SM-003: Sub-Phase State Machine

**Statement:** Each major phase shall have a sub-phase state machine defining the interview flow within that phase:

```
Example: PROJECT_INITIALIZATION sub-phases
├── INITIAL_DESCRIPTION (open-ended project description)
├── DOMAIN_IDENTIFICATION (industry, system type)
├── SAFETY_CRITICALITY (is it safety-critical?)
├── DAL_SIL_DETERMINATION (what level?)
├── STANDARDS_IDENTIFICATION (which standards apply?)
├── PROCESS_SELECTION (development approach)
├── TEAM_CONTEXT (team size, distribution)
└── INITIALIZATION_COMPLETE
```

**Priority:** CRITICAL

**Rationale:** Breaks complex phases into manageable interview steps.

**Verification Method:** Test (sub-phase transitions)

**Source:** Discussion 2025-11-23

---

### REQ-SM-004: State Persistence

**Statement:** The Process Engine shall persist the current state (phase, sub-phase, answered questions, pending questions) to the database after every user interaction.

**Priority:** CRITICAL

**Rationale:** Enables session resumption at exact point of interruption.

**Verification Method:** Test (session save/restore)

**Source:** REQ-AI-028 (Session State Persistence)

---

### REQ-SM-005: Parallel Phase Support

**Statement:** The Process Engine shall support multiple phases active simultaneously when appropriate (e.g., requirements elicitation can continue while architecture is being defined).

**Priority:** MEDIUM

**Rationale:** Real-world development is iterative, not strictly waterfall.

**Verification Method:** Test (parallel phase execution)

**Source:** ARP4754A iterative development support

---

### REQ-SM-006: Phase Rollback

**Statement:** The Process Engine shall support rollback to a previous phase when requirements change or errors are discovered, with:
- Audit trail of rollback
- Impact analysis on dependent artifacts
- User confirmation required

**Priority:** HIGH

**Rationale:** Supports iterative development and error correction.

**Verification Method:** Test (rollback scenarios)

**Source:** Configuration management best practices

---

## 4. Interview Script Requirements (REQ-IS-xxx)

### REQ-IS-001: Structured Interview Scripts

**Statement:** The Process Engine shall implement structured interview scripts for each sub-phase, where each script defines:
- **Question ID** - Unique identifier
- **Question Text** - The question to ask (can be multiple variants)
- **Expected Data Type** - Text, selection, number, date, etc.
- **Validation Rules** - What constitutes a valid answer
- **Target Field** - Database table and column for storage
- **Next Question Logic** - Conditional branching based on answer
- **Skip Conditions** - When to skip this question

**Priority:** CRITICAL

**Rationale:** Complete specification of interview behavior without AI interpretation.

**Verification Method:** Review (script completeness) + Test (script execution)

**Source:** Discussion 2025-11-23

---

### REQ-IS-002: Project Initialization Interview Script

**Statement:** The Process Engine shall implement a Project Initialization Interview Script with the following questions:

**Stage 1: Initial Capture**
| Q-ID | Question | Data Type | Target |
|------|----------|-----------|--------|
| PI-001 | Describe your project as precisely as you can | Free text | projects.description |
| PI-002 | What is the name of this project? | Text (validated) | projects.name |

**Stage 2: Domain & Safety**
| Q-ID | Question | Data Type | Target |
|------|----------|-----------|--------|
| PI-003 | What industry is this project for? | Selection (Aerospace/Automotive/Medical/Industrial/Rail/Defense/Other) | projects.industry_sector |
| PI-004 | Is this a safety-critical system? | Yes/No | projects.is_safety_critical |
| PI-005 | [If safety-critical] What is the target DAL/SIL level? | Selection (DAL-A/B/C/D or SIL-1/2/3/4) | projects.assurance_level |
| PI-006 | [If safety-critical] What certification authority? | Text | projects.certification_authority |

**Stage 3: Standards & Process**
| Q-ID | Question | Data Type | Target |
|------|----------|-----------|--------|
| PI-007 | Which standards apply to your project? | Multi-select (DO-178C/DO-254/ARP4754A/ISO26262/IEC61508/IEC62304) | project_standards (many-to-many) |
| PI-008 | What development process will you follow? | Selection (V-Model/Iterative/Agile-Compliant/Hybrid) | projects.development_process |
| PI-009 | What is your target completion date? | Date | projects.target_completion_date |

**Stage 4: Team Context**
| Q-ID | Question | Data Type | Target |
|------|----------|-----------|--------|
| PI-010 | How large is your development team? | Selection (1-5/6-20/21-100/100+) | projects.team_size |
| PI-011 | Is development distributed across sites/companies? | Yes/No | projects.is_distributed |
| PI-012 | Will suppliers be contributing? | Yes/No | projects.has_suppliers |

**Priority:** CRITICAL

**Rationale:** Complete specification of project initialization interview.

**Verification Method:** Test (complete interview flow)

**Source:** REQ-AI-032 through REQ-AI-037

---

### REQ-IS-003: Requirements Elicitation Interview Script

**Statement:** The Process Engine shall implement a Requirements Elicitation Interview Script with the following question patterns:

**For Each Requirement:**
| Q-ID | Question | Data Type | Target |
|------|----------|-----------|--------|
| RE-001 | Describe what the system shall do (one capability at a time) | Free text | requirements.description |
| RE-002 | What type of requirement is this? | Selection (Functional/Performance/Interface/Safety/Security/Constraint) | requirements.type |
| RE-003 | What is the priority? | Selection (Critical/High/Medium/Low) | requirements.priority |
| RE-004 | What is the rationale for this requirement? | Free text | requirements.rationale |
| RE-005 | Are there any constraints or assumptions? | Free text | requirements.constraints |
| RE-006 | Which system component does this apply to? | Selection (from PBS) | requirements.allocated_to |
| RE-007 | Is this requirement derived from another? | Selection (from existing reqs) | requirement_traces.parent_id |
| RE-008 | Do you have another requirement to add? | Yes/No | (loop control) |

**Priority:** CRITICAL

**Rationale:** Structured capture of requirements with all DO-178C required attributes.

**Verification Method:** Test (requirement capture flow)

**Source:** DO-178C Table A-2 (Requirements attributes)

---

### REQ-IS-004: Design Capture Interview Script

**Statement:** The Process Engine shall implement a Design Capture Interview Script with the following question patterns:

**For Each Design Component:**
| Q-ID | Question | Data Type | Target |
|------|----------|-----------|--------|
| DC-001 | What is the name of this design component? | Text | design_components.name |
| DC-002 | Describe this component's purpose | Free text | design_components.description |
| DC-003 | What requirements does this component address? | Multi-select (from reqs) | design_traces.requirement_id |
| DC-004 | What are the interfaces to other components? | Structured (from/to/type) | component_interfaces |
| DC-005 | What data does this component process? | Structured | component_data_flows |
| DC-006 | What design decisions were made? | Free text | design_decisions.description |
| DC-007 | What were the alternatives considered? | Free text | design_decisions.alternatives |
| DC-008 | Why was this approach chosen? | Free text | design_decisions.rationale |

**Priority:** HIGH

**Rationale:** Structured capture of design decisions with traceability.

**Verification Method:** Test (design capture flow)

**Source:** DO-178C Table A-4 (Design attributes)

---

### REQ-IS-005: Configuration Item Interview Script

**Statement:** The Process Engine shall implement a Configuration Item capture script for the 34+ CI fields defined in REQ-DB-038:

**Core Identification (Required):**
| Q-ID | Field | Data Type |
|------|-------|-----------|
| CI-001 | CI Name | Text |
| CI-002 | CI Type | Selection (Hardware/Software/Document/Assembly/Part) |
| CI-003 | Part Number | Text (validated format) |
| CI-004 | Description | Free text |

**Classification (Required for safety-critical):**
| Q-ID | Field | Data Type |
|------|-------|-----------|
| CI-005 | Control Level | Selection (1-5) |
| CI-006 | Safety Classification | Selection (Critical/Major/Minor/None) |
| CI-007 | Security Classification | Selection (Public/Internal/Confidential/Secret) |

**Lifecycle (Auto-populated with manual override):**
| Q-ID | Field | Data Type |
|------|-------|-----------|
| CI-008 | Lifecycle Phase | Selection (Development/Integration/Verification/Production/Obsolete) |
| CI-009 | Development Status | Selection (Planned/InProgress/Complete) |
| CI-010 | Baseline Status | Selection (None/Proposed/Approved/Frozen) |

*[Continue for all 34+ fields...]*

**Priority:** HIGH

**Rationale:** Complete CI data capture per REQ-DB-038.

**Verification Method:** Test (CI capture completeness)

**Source:** REQ-DB-038, CONFIGURATION_ITEM_MANAGEMENT.md

---

### REQ-IS-006: Question Variants for Natural Language

**Statement:** Each interview question shall have multiple natural language variants that convey the same meaning, allowing the system to vary phrasing:

**Example for PI-004 (Safety Critical):**
- Variant 1: "Is this a safety-critical system?"
- Variant 2: "Does this system have safety implications?"
- Variant 3: "Could a failure of this system cause harm to people or property?"
- Variant 4: "Are there safety requirements for this system?"

**Priority:** MEDIUM

**Rationale:** Improves user experience without requiring AI for rephrasing.

**Verification Method:** Review (variant quality)

**Source:** REQ-AI-002 (Simple Language)

---

### REQ-IS-007: Conditional Question Flow

**Statement:** The Interview Script shall support conditional question flow based on previous answers:

```
IF answer(PI-004) == "No" THEN
    SKIP questions PI-005, PI-006
    SET projects.assurance_level = "None"
ENDIF

IF answer(PI-003) == "Aerospace" THEN
    DEFAULT projects.applicable_standards = ["DO-178C", "ARP4754A"]
    ASK question PI-005 with options ["DAL-A", "DAL-B", "DAL-C", "DAL-D"]
ENDIF

IF answer(PI-003) == "Automotive" THEN
    DEFAULT projects.applicable_standards = ["ISO 26262"]
    ASK question PI-005 with options ["ASIL-A", "ASIL-B", "ASIL-C", "ASIL-D"]
ENDIF
```

**Priority:** HIGH

**Rationale:** Tailors interview to project context, reduces irrelevant questions.

**Verification Method:** Test (conditional flow scenarios)

**Source:** REQ-AI-036 (Tool Configuration based on context)

---

### REQ-IS-008: Interview Progress Tracking

**Statement:** The Process Engine shall track interview progress including:
- Total questions in current script
- Questions answered
- Questions skipped (with reason)
- Questions remaining
- Estimated completion percentage

**Priority:** MEDIUM

**Rationale:** User needs visibility into interview length and progress.

**Verification Method:** Test (progress calculation)

**Source:** User experience requirement

---

## 5. Data Capture Requirements (REQ-DC-xxx)

### REQ-DC-001: Answer-to-Database Mapping

**Statement:** Every interview question shall have a defined mapping to database storage:

```python
class QuestionMapping:
    question_id: str          # e.g., "PI-004"
    table_name: str           # e.g., "projects"
    column_name: str          # e.g., "is_safety_critical"
    data_type: str            # e.g., "boolean"
    transformation: Callable  # e.g., lambda x: x.lower() == "yes"
    validation: Callable      # e.g., lambda x: x in ["yes", "no"]
```

**Priority:** CRITICAL

**Rationale:** Deterministic storage - no AI interpretation of where data goes.

**Verification Method:** Review (mapping completeness) + Test (data storage)

**Source:** REQ-AI-007 (Data Formatting Knowledge), REQ-AI-008 (Database Mapping Knowledge)

---

### REQ-DC-002: Input Validation Rules

**Statement:** The Process Engine shall validate all user input against defined rules before storage:

| Validation Type | Rule | Error Message |
|-----------------|------|---------------|
| Required | Field must not be empty | "This field is required" |
| Text Length | min/max characters | "Must be between X and Y characters" |
| Pattern | Regex match | "Must match format: XXX" |
| Selection | Must be from allowed values | "Please select one of: X, Y, Z" |
| Reference | Must exist in referenced table | "Referenced item not found" |
| Unique | Must not duplicate existing | "A [item] with this [field] already exists" |
| Date Range | Must be within allowed range | "Date must be between X and Y" |

**Priority:** CRITICAL

**Rationale:** Data quality enforcement at entry point.

**Verification Method:** Test (validation scenarios)

**Source:** REQ-BE-010 (Input Validation)

---

### REQ-DC-003: Automatic Field Population

**Statement:** The Process Engine shall automatically populate fields based on rules:

| Auto-Field | Rule |
|------------|------|
| requirements.requirement_id | Generate next sequential ID (e.g., REQ-FN-042) |
| requirements.created_at | Current timestamp |
| requirements.created_by | Current user ID |
| requirements.version | 1 (initial) |
| requirements.status | "draft" (initial) |
| configuration_items.guid | Generate UUID v4 |
| configuration_items.display_id | Generate from template (e.g., CI-HW-001) |

**Priority:** HIGH

**Rationale:** Reduce user burden, ensure consistency.

**Verification Method:** Test (auto-population)

**Source:** REQ-DB-052 (Hybrid Identifier System)

---

### REQ-DC-004: Requirement Format Enforcement

**Statement:** The Process Engine shall enforce requirement statement format:
- Must contain "shall" statement
- Must be testable (single verifiable behavior)
- Must not be ambiguous (no "and/or", "etc.", "as appropriate")
- Must have single subject

**Warning Patterns:**
- "The system shall X and shall Y" → Split into two requirements
- "The system may..." → Not a requirement (optional)
- "The system should..." → Ambiguous priority
- "...as needed..." → Ambiguous condition

**Priority:** HIGH

**Rationale:** DO-178C requires unambiguous, testable requirements.

**Verification Method:** Test (format validation)

**Source:** DO-178C Table A-2 Objective 1

---

### REQ-DC-005: Traceability Link Creation

**Statement:** The Process Engine shall automatically create traceability links when:
- A requirement references another requirement (derives-from)
- A design component references a requirement (satisfies)
- A test case references a requirement (verifies)
- A CI is allocated to a requirement

**Priority:** CRITICAL

**Rationale:** Automatic traceability maintenance per DO-178C.

**Verification Method:** Test (link creation)

**Source:** REQ-AI-027 (Traceability Maintenance)

---

### REQ-DC-006: Change Detection and Versioning

**Statement:** When a captured artifact is modified, the Process Engine shall:
1. Detect which fields changed
2. Increment version number
3. Store previous version in history
4. Record change timestamp and user
5. Flag dependent artifacts for review

**Priority:** HIGH

**Rationale:** Configuration management and audit trail.

**Verification Method:** Test (change detection)

**Source:** REQ-DB-023 (Requirement History), REQ-DB-042 (CI Change History)

---

## 6. Artifact Generation Requirements (REQ-AG-xxx)

### REQ-AG-001: Template-Based Document Generation

**Statement:** The Process Engine shall generate documents from database content using predefined templates:

| Document | Template | Data Source |
|----------|----------|-------------|
| SRS | SRS_template.md | requirements table |
| HLD | HLD_template.md | design_components table |
| RTM | RTM_template.md | requirement_traces table |
| CI List | CI_List_template.md | configuration_items table |
| Test Plan | TestPlan_template.md | test_plans, test_cases tables |

**Priority:** HIGH

**Rationale:** Deterministic document generation - no AI interpretation.

**Verification Method:** Test (document generation)

**Source:** REQ-AI-025 (Automatic Document Updates)

---

### REQ-AG-002: Document Template Structure

**Statement:** Each document template shall define:
- Document header (title, version, date, author)
- Section structure
- Data placeholders with database queries
- Formatting rules (Markdown)
- Table layouts
- Appendix structure

**Example SRS Template Section:**
```markdown
## {{section_number}}. {{requirement_type}} Requirements

{% for req in requirements.filter(type=requirement_type) %}
### {{req.requirement_id}}: {{req.title}}

**Statement:** {{req.description}}

**Priority:** {{req.priority}}

**Rationale:** {{req.rationale}}

**Verification Method:** {{req.verification_method}}

---
{% endfor %}
```

**Priority:** HIGH

**Rationale:** Standardized document structure.

**Verification Method:** Review (template completeness)

**Source:** DO-178C document standards

---

### REQ-AG-003: Incremental Document Updates

**Statement:** When data changes, the Process Engine shall:
1. Identify affected document sections
2. Regenerate only changed sections
3. Mark document as "updated - needs review"
4. Log what changed in document history

**Priority:** MEDIUM

**Rationale:** Efficient document maintenance.

**Verification Method:** Test (incremental updates)

**Source:** REQ-AI-026 (Review Marking)

---

### REQ-AG-004: Traceability Matrix Generation

**Statement:** The Process Engine shall automatically generate and maintain:
- Requirements-to-Design Traceability Matrix
- Requirements-to-Test Traceability Matrix
- Design-to-Code Traceability Matrix
- Bi-directional completeness report (gaps highlighted)

**Priority:** CRITICAL

**Rationale:** DO-178C mandates complete traceability.

**Verification Method:** Test (matrix generation)

**Source:** REQ-DB-012 (Bidirectional Traceability)

---

### REQ-AG-005: Gap Analysis Report

**Statement:** The Process Engine shall generate Gap Analysis reports identifying:
- Requirements without design allocation
- Design components without requirements
- Requirements without test coverage
- Orphaned test cases
- CIs without requirement allocation

**Priority:** HIGH

**Rationale:** Process compliance verification.

**Verification Method:** Test (gap detection)

**Source:** REQ-DB-014 (Coverage Analysis)

---

## 7. Process Phase Requirements (REQ-PP-xxx)

### REQ-PP-001: Phase-Specific Behaviors

**Statement:** The Process Engine shall exhibit different behaviors based on current phase:

| Phase | Primary Actions | Allowed Artifacts | Blocked Actions |
|-------|-----------------|-------------------|-----------------|
| PROJECT_INIT | Context capture | Project record | Create requirements |
| REQ_ELICITATION | Capture requirements | Requirements | Create design |
| REQ_ANALYSIS | Classify, decompose | Derived requirements | Create code |
| ARCH_DEFINITION | Capture HLD | Design components | Detailed design |
| DETAILED_DESIGN | Capture LLD | Detailed design | Implementation |
| VERIFICATION | Capture test cases | Test cases, results | N/A |

**Priority:** HIGH

**Rationale:** Phase discipline prevents out-of-order artifact creation.

**Verification Method:** Test (phase constraints)

**Source:** DO-178C process model

---

### REQ-PP-002: Phase Completion Criteria

**Statement:** Each phase shall have defined completion criteria that must be satisfied:

| Phase | Completion Criteria |
|-------|---------------------|
| PROJECT_INIT | All required context captured, DAL/SIL determined |
| REQ_ELICITATION | All known requirements captured, user confirms complete |
| REQ_ANALYSIS | All requirements classified, prioritized, allocated |
| ARCH_DEFINITION | All HLD components defined, 100% requirement coverage |
| DETAILED_DESIGN | All LLD defined, interfaces specified |
| VERIFICATION | All test cases defined, linked to requirements |

**Priority:** HIGH

**Rationale:** Phase gates ensure process compliance.

**Verification Method:** Test (completion validation)

**Source:** DO-178C phase objectives

---

### REQ-PP-003: Phase Artifact Checklist

**Statement:** For each phase, the Process Engine shall display a checklist of required artifacts:

**Example: REQUIREMENTS_ELICITATION Phase Checklist:**
- [ ] Functional requirements captured (at least 1)
- [ ] Performance requirements reviewed
- [ ] Interface requirements identified
- [ ] Safety requirements identified (if safety-critical)
- [ ] Requirements prioritized
- [ ] Requirements allocated to system components
- [ ] Traceability to parent requirements established
- [ ] SRS document generated

**Priority:** MEDIUM

**Rationale:** User guidance on phase deliverables.

**Verification Method:** Test (checklist display)

**Source:** DO-178C lifecycle data requirements

---

## 8. NLP Wrapper Requirements (REQ-NL-xxx)

### REQ-NL-001: Optional AI for Natural Language

**Statement:** The Process Engine shall support an optional NLP Wrapper that uses AI to:
- Rephrase questions more naturally based on context
- Interpret free-text answers and suggest structured data
- Handle unexpected user input gracefully
- Generate user-friendly explanations of validation errors

**AI is NOT required for core functionality.**

**Priority:** MEDIUM

**Rationale:** Improves user experience but system works without it.

**Verification Method:** Test (with and without NLP wrapper)

**Source:** Discussion 2025-11-23

---

### REQ-NL-002: Fallback to Script Questions

**Statement:** If AI/NLP is unavailable, the Process Engine shall:
- Use the first variant of each question
- Present validation errors as-is
- Continue all operations normally

**Priority:** HIGH

**Rationale:** System must function without AI dependency.

**Verification Method:** Test (AI-disabled mode)

**Source:** Discussion 2025-11-23

---

### REQ-NL-003: AI Interpretation Confirmation

**Statement:** When AI interprets user input to extract structured data, the Process Engine shall:
- Show the user what was extracted
- Allow user to confirm or correct
- Never auto-commit AI interpretations

**Priority:** CRITICAL

**Rationale:** Human approval required for all data storage (REQ-AI-017).

**Verification Method:** Test (confirmation workflow)

**Source:** REQ-AI-017 (User Review of AI Updates)

---

## 9. Requirements Summary

### 9.1 Requirements Count

| Category | Count | Range |
|----------|-------|-------|
| State Machine (REQ-SM) | 6 | REQ-SM-001 to REQ-SM-006 |
| Interview Scripts (REQ-IS) | 8 | REQ-IS-001 to REQ-IS-008 |
| Data Capture (REQ-DC) | 6 | REQ-DC-001 to REQ-DC-006 |
| Artifact Generation (REQ-AG) | 5 | REQ-AG-001 to REQ-AG-005 |
| Process Phase (REQ-PP) | 3 | REQ-PP-001 to REQ-PP-003 |
| NLP Wrapper (REQ-NL) | 3 | REQ-NL-001 to REQ-NL-003 |
| **TOTAL** | **31** | |

### 9.2 Priority Distribution

| Priority | Count |
|----------|-------|
| CRITICAL | 11 |
| HIGH | 14 |
| MEDIUM | 6 |

---

## 10. Traceability to Main SRS

### 10.1 Requirements Supported

These Process Engine requirements provide implementation detail for:

| Process Engine Req | Supports Main SRS Req |
|--------------------|----------------------|
| REQ-SM-001 | REQ-AI-014 (ARP4754 Process Knowledge) |
| REQ-IS-002 | REQ-AI-032 to REQ-AI-037 (Project Initialization) |
| REQ-IS-003 | REQ-AI-011 (Question-Based Elicitation) |
| REQ-DC-001 | REQ-AI-006, REQ-AI-007, REQ-AI-008 (Database Knowledge) |
| REQ-DC-004 | REQ-AI-001 (Single Question), REQ-AI-002 (Simple Language) |
| REQ-AG-001 | REQ-AI-025 (Automatic Document Updates) |
| REQ-AG-004 | REQ-AI-027 (Traceability Maintenance) |
| REQ-NL-003 | REQ-AI-017 (User Review Required) |

---

## Appendix A: Interview Script JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Interview Script",
  "type": "object",
  "properties": {
    "script_id": {"type": "string"},
    "phase": {"type": "string"},
    "sub_phase": {"type": "string"},
    "questions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "question_id": {"type": "string"},
          "variants": {"type": "array", "items": {"type": "string"}},
          "data_type": {"enum": ["text", "selection", "multi_select", "number", "date", "boolean"]},
          "options": {"type": "array", "items": {"type": "string"}},
          "required": {"type": "boolean"},
          "validation": {
            "type": "object",
            "properties": {
              "min_length": {"type": "integer"},
              "max_length": {"type": "integer"},
              "pattern": {"type": "string"},
              "allowed_values": {"type": "array"}
            }
          },
          "target": {
            "type": "object",
            "properties": {
              "table": {"type": "string"},
              "column": {"type": "string"},
              "transformation": {"type": "string"}
            }
          },
          "conditions": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "depends_on": {"type": "string"},
                "operator": {"enum": ["equals", "not_equals", "contains", "in"]},
                "value": {},
                "action": {"enum": ["skip", "require", "show", "hide"]}
              }
            }
          }
        },
        "required": ["question_id", "variants", "data_type", "target"]
      }
    }
  }
}
```

---

**END OF PROCESS ENGINE REQUIREMENTS SPECIFICATION**

---

**Document Status:** Draft
**Next Steps:**
1. Review and approval
2. Integrate with main SRS
3. Create HLD section for Process Engine architecture
4. Implement interview scripts as JSON data files
5. Build state machine framework
