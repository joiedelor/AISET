# AISET - High-Level Design (HLD)

**Document Type:** [Level 1] AISET Tool Development - DO-178C DAL D
**Document Version:** 1.2.0
**Last Updated:** 2025-11-22
**Status:** Draft - In Review
**Applicable Standards:** DO-178C (Software), ARP4754A (System), DO-254 (Hardware reference)

---

## Document Control

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2025-11-16 | Claude + User | Initial HLD creation - Architecture definition |
| 1.1.0 | 2025-11-22 | Claude + User | Added Project Initialization Interview Flow (Section 5.1), conversation persistence architecture |
| 1.2.0 | 2025-11-22 | Claude + User | Added AI Controller Architecture (4.5), Guardrails Middleware (4.6), AI Roles (4.7), Micro-Interaction Pattern (4.8) |

### Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Design Lead | TBD | | |
| Safety Engineer | TBD | | |
| Quality Assurance | TBD | | |

---

## 1. Introduction

### 1.1 Purpose

This High-Level Design (HLD) document describes the software architecture of the AISET (AI Systems Engineering Tool) application. AISET is an enterprise collaborative platform designed to automate requirements elicitation, design documentation, configuration management, and traceability management for safety-critical systems development.

This document satisfies DO-178C objectives for High-Level Requirements and Architecture Design.

### 1.2 Scope

**In Scope:**
- AISET tool architecture (frontend, backend, database, AI engine)
- Component interactions and interfaces
- Data flow and control flow
- Technology stack and design rationale
- Enterprise collaborative and distributed architecture
- Configuration Item (CI) management architecture
- Multi-user concurrent access architecture
- Multi-instance distributed development architecture

**Out of Scope:**
- Low-level design details (see LLD documents)
- User system designs (what AISET helps users create)
- Detailed database schema (see Database LLD)
- Detailed API specifications (see Interface Specifications)

### 1.3 Applicable Documents

**External Standards:**
- DO-178C: Software Considerations in Airborne Systems and Equipment Certification
- ARP4754A: Guidelines for Development of Civil Aircraft and Systems
- DO-254: Design Assurance Guidance for Airborne Electronic Hardware
- ISO 26262: Road vehicles - Functional safety (reference)
- IEC 62304: Medical device software (reference)

**Internal AISET Documents:**
- `REQUIREMENTS.md` (v0.8.0) - 167 requirements
- `02_REQUIREMENTS/SRS_Software_Requirements_Specification.md` (planned)
- `03_DESIGN/LLD_Database_Schema_Design.md` (planned)
- `docs/Level_1_AISET_Development/DATABASE_SCHEMA.md` (existing reference)
- `docs/Level_2_User_Framework/CONFIGURATION_ITEM_MANAGEMENT.md` (CI reference framework)

### 1.4 Definitions and Acronyms

| Term | Definition |
|------|------------|
| AISET | AI Systems Engineering Tool |
| CI | Configuration Item - an aggregation of hardware/software that satisfies an end use function |
| DAL | Development Assurance Level (DO-178C: A, B, C, D) |
| SIL | Safety Integrity Level (ISO 26262, IEC 62304) |
| BOM | Bill of Materials |
| PBS | Product Breakdown Structure |
| HLD | High-Level Design |
| LLD | Low-Level Design |
| RBAC | Role-Based Access Control |
| GUID | Globally Unique Identifier (128-bit UUID) |
| ACL | Access Control List |

---

## 2. System Overview

### 2.1 AISET Mission

AISET is designed to reduce engineering overhead by 50-70% while maintaining full compliance with aerospace and safety-critical standards. It achieves this through:

1. **AI-assisted requirements elicitation** - Natural language conversation to capture requirements
2. **Automated document generation** - Requirements, design, verification docs from database
3. **Intelligent traceability** - Automatic bi-directional traceability maintenance
4. **Configuration management** - Comprehensive CI lifecycle tracking (34+ fields)
5. **Collaborative development** - Multi-user concurrent access with pessimistic locking
6. **Distributed development** - Multi-instance with intelligent merge capabilities

### 2.2 Target Users

**Primary Users:**
- Systems Engineers (may or may not be experts in systems engineering methodology)
- Requirements Engineers
- Design Engineers
- Verification Engineers
- Configuration Managers
- Project Managers

**Secondary Users:**
- Certification Authorities (read-only access to generated documentation)
- Suppliers and Subcontractors (limited access to assigned work)
- External Reviewers

### 2.3 Usage Scenarios

AISET supports three primary deployment models:

**Scenario 1: Centralized (Single Team)**
- One team, one database instance
- Sequential or lightly concurrent work
- Typical: Small projects, single company, co-located team

**Scenario 2: Concurrent (Multiple Users, Same Database)**
- Multiple users working simultaneously
- Same database instance
- Pessimistic locking (check-out/check-in) prevents conflicts
- Work partitioning by CI assignment
- Typical: Medium/large projects, single site, multiple engineers

**Scenario 3: Distributed (Multiple Instances)**
- Multiple isolated AISET instances (different databases)
- Each instance owned by different team/company/site
- Milestone-based data export/import
- Intelligent merge with AI-assisted conflict resolution
- Typical: Prime contractor + suppliers, multi-site development, multi-company programs

### 2.4 Development Assurance Level

**AISET Tool Qualification:**
- AISET itself is developed to **DO-178C DAL D** (Design Assurance Level D)
- AISET is a **development tool**, not airborne software
- Tool qualification required if AISET eliminates, reduces, or automates verification processes

**User Projects Supported:**
- AISET shall support user projects at **any DAL** (A, B, C, D) or SIL level
- AISET adapts documentation rigor based on user project DAL/SIL
- AISET cannot reduce the rigor required by user's project DAL

---

## 3. System Architecture

### 3.1 Architectural Overview

AISET follows a **4-tier enterprise architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                    TIER 1: PRESENTATION                     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         React Frontend (TypeScript)                 │   │
│  │  - Project Dashboard    - CI Management UI          │   │
│  │  - Dual Interface       - Check-out/Check-in UI     │   │
│  │  - Document Viewer      - Merge Review UI           │   │
│  │  - Chat Interface       - RBAC Management UI        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTPS/REST API
┌─────────────────────────────────────────────────────────────┐
│                   TIER 2: APPLICATION                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │       FastAPI Backend (Python 3.12+)                │   │
│  │  - REST API Endpoints   - Lock Management           │   │
│  │  - Business Logic       - Merge Engine              │   │
│  │  - Session Management   - RBAC Enforcement          │   │
│  │  - Workflow Engine      - Export/Import             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          AI Engine Integration                      │   │
│  │  - Claude API (primary)                             │   │
│  │  - LM Studio / Mistral (local fallback)             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ SQL/ORM
┌─────────────────────────────────────────────────────────────┐
│                     TIER 3: DATA                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         PostgreSQL Database (15+)                   │   │
│  │  - 42+ tables (ARP4754/DO-178C/DO-254 schema)       │   │
│  │  - Hybrid ID system (GUID + Display ID)             │   │
│  │  - Lock management tables                           │   │
│  │  - Session tracking tables                          │   │
│  │  - RBAC tables (users, roles, permissions)          │   │
│  │  - Merge metadata tables                            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ Backup/Replication
┌─────────────────────────────────────────────────────────────┐
│                   TIER 4: PERSISTENCE                       │
│                                                             │
│  - File Storage (uploaded documents, exports)               │
│  - Database Backups                                         │
│  - Audit Logs                                               │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Component Interaction Flow

**Typical User Workflow:**

1. **User authenticates** → Frontend → Backend validates → Creates session
2. **User initiates conversation** → Frontend chat → Backend → AI Engine
3. **AI asks question** → Backend stores message → Frontend displays
4. **User responds** → Frontend → Backend → AI processes → Updates database
5. **AI extracts requirements** → Backend writes to database → Marks for review
6. **User reviews changes** → Frontend document list → Approve/reject
7. **User checks out CI** → Frontend → Backend acquires lock → Updates lock table
8. **User edits CI** → Frontend → Backend validates lock ownership → Updates database
9. **User checks in CI** → Frontend → Backend releases lock → Increments version
10. **User exports data** → Backend queries database → Generates export package → File storage

---

## 4. Component Design

### 4.1 Frontend (Presentation Tier)

**Technology:** React 18 + TypeScript 5 + Vite

**Responsibilities:**
- User interface rendering
- User input capture and validation
- API communication (REST)
- Client-side state management
- Real-time update display
- Document preview and rendering

**Key Modules:**

#### 4.1.1 Project Dashboard
- Display project status, DAL/SIL level, applicable standards
- Show active conversations, recent documents, pending reviews
- Display CI status summary (checked out, under review, released)
- **Traces to:** REQ-FE-009

#### 4.1.2 Dual Interface (Chat + Proposal)
- Left panel: AI conversation interface
- Right panel: Proposal/document preview
- Real-time synchronization
- **Traces to:** REQ-FE-008

#### 4.1.3 Product Structure Tree
- Hierarchical display of product breakdown (PBS)
- Expandable/collapsible tree view
- Drag-and-drop CI organization
- Context menu (check-out, view, edit, delete)
- **Traces to:** REQ-FE-010

#### 4.1.4 BOM Editor
- Table view of Bill of Materials
- Filter by BOM type (engineering, manufacturing, service, as-built)
- Inline editing with validation
- **Traces to:** REQ-FE-011

#### 4.1.5 CI Management Table
- Comprehensive CI table view (34+ fields)
- Sortable, filterable columns
- Status indicators (baseline, control level, verification status)
- **Traces to:** REQ-FE-013

#### 4.1.6 Check-out/Check-in Interface
- Visual indicators for locked CIs
- Check-out dialog (reason, estimated duration)
- Check-in dialog (summary of changes)
- Lock timeout warnings
- **Traces to:** REQ-FE-014, REQ-FE-023

#### 4.1.7 Merge Review UI
- Side-by-side comparison of conflicting data
- AI suggestion display with confidence scores
- Conflict resolution controls (accept source, accept target, manual merge)
- **Traces to:** REQ-FE-015, REQ-FE-016, REQ-FE-021

#### 4.1.8 RBAC Management UI
- User management (create, edit, assign roles)
- Team management
- Permission assignment (CI-level ACL)
- **Traces to:** REQ-FE-020

**Design Decisions:**
- **React** chosen for component reusability and strong TypeScript support
- **Vite** chosen for fast development builds
- **REST API** chosen over GraphQL for simplicity and DO-178C tool qualification
- Client-side state managed by React Context (not Redux) for reduced complexity

### 4.2 Backend (Application Tier)

**Technology:** Python 3.12+ with FastAPI framework

**Responsibilities:**
- REST API endpoint implementation
- Business logic execution
- Database transaction management
- AI engine integration
- Session state management
- Lock management and conflict detection
- Merge engine implementation
- RBAC enforcement
- Workflow orchestration
- Export/import data exchange

**Key Modules:**

#### 4.2.1 API Layer
- RESTful endpoints following OpenAPI 3.0 spec
- Request validation (Pydantic models)
- Response serialization
- Error handling and logging
- Authentication middleware (JWT tokens)
- Authorization middleware (RBAC checks)

#### 4.2.2 Session Manager
- Create/resume AI conversations
- Maintain conversation context
- Store user session state (active locks, current CI, permissions)
- Session timeout handling
- **Traces to:** REQ-BE-011, REQ-DB-053

#### 4.2.3 Lock Manager (Pessimistic Locking)
- Check-out: Acquire exclusive lock on CI
- Check-in: Release lock, increment version
- Lock timeout detection
- Lock ownership validation
- Force unlock (admin only)
- **Traces to:** REQ-BE-016, REQ-DB-054

#### 4.2.4 Conflict Detector (Optimistic Locking)
- Version stamp comparison
- Detect concurrent modifications
- Flag conflicts for resolution
- **Traces to:** REQ-BE-017

#### 4.2.5 Work Assignment Engine
- Assign CIs to users/teams
- Partition work to prevent concurrent editing
- Workload balancing queries
- **Traces to:** REQ-BE-018, REQ-DB-055

#### 4.2.6 Export/Import Engine
- Export data from database to portable format (JSON/XML)
- Include source instance metadata
- Import data from external AISET instance
- Validate import package integrity
- **Traces to:** REQ-BE-019, REQ-DB-066

#### 4.2.7 Intelligent Merge Engine
- **5 Conflict Types:**
  1. **ID Collision:** Same CI ID, different data
  2. **Duplicate Items:** Different IDs, same physical item
  3. **Field Conflicts:** Same CI, different field values
  4. **Broken References:** Source CI references non-existent requirement
  5. **Circular Dependencies:** Merge creates circular parent-child relationships

- **Resolution Strategies:**
  - Automatic (no conflicts): New CIs auto-add, identical CIs skip
  - AI-assisted: Invoke AI for conflict analysis and suggestion
  - Rule-based: Apply configured rules (newer wins, certified wins, etc.)
  - Manual: Present conflict to user for decision

- **Traces to:** REQ-BE-021, REQ-AI-041, REQ-DB-063

#### 4.2.8 RBAC Enforcement Engine
- Validate user permissions before operations
- **7 Role Types:**
  1. Administrator (full access)
  2. Manager (project-level control)
  3. Senior Engineer (create/modify/review)
  4. Engineer (create/modify own work)
  5. Reviewer (read + comment + approve)
  6. Viewer (read-only)
  7. External Stakeholder (limited read access)

- **3 Permission Levels:**
  1. User-level (role-based)
  2. Team-level (team membership)
  3. CI-level (granular ACL per CI)

- **Traces to:** REQ-BE-024, REQ-DB-057, REQ-DB-058, REQ-DB-059

#### 4.2.9 Duplicate Detection Engine
- Analyze CIs from different instances
- Compare: name, part number, description, supplier, specifications
- Calculate similarity score
- Flag potential duplicates for review
- **Traces to:** REQ-BE-027, REQ-AI-042, REQ-DB-070

**Design Decisions:**
- **FastAPI** chosen for automatic OpenAPI spec generation and async support
- **Python** chosen for strong AI/ML library ecosystem and rapid development
- **Pydantic** for data validation (type safety without TypeScript compilation)
- **Async/await** for concurrent request handling
- **Transaction management** using context managers for ACID compliance

### 4.3 Database (Data Tier)

**Technology:** PostgreSQL 15+

**Responsibilities:**
- Persistent data storage
- Data integrity enforcement (constraints, triggers)
- Transaction management (ACID compliance)
- Query optimization (indexes, views)
- Audit trail maintenance
- Backup and recovery

**Schema Overview:**
- **42+ tables** implementing full ARP4754/DO-178C/DO-254 compliance
- **Hybrid identifier system** on all entities:
  - `guid` (UUID, 128-bit) - Primary key, globally unique
  - `display_id` (VARCHAR) - Human-readable ID for UI
- **Soft deletes** on all major entities (not hard delete)
- **Audit columns** on all tables (created_at, updated_at, created_by, updated_by)
- **Version stamping** on all CIs for optimistic locking

**Major Table Groups:**

1. **Core Project Tables** (projects, standards, lifecycles)
2. **Requirements Tables** (requirements, traceability)
3. **Design Tables** (design_elements, design_reviews)
4. **CI Management Tables** (configuration_items, bom, suppliers)
5. **Verification Tables** (test_plans, test_cases, test_results)
6. **Documentation Tables** (documents, document_associations)
7. **AI Conversation Tables** (ai_conversations, ai_messages)
8. **Collaboration Tables** (locks, sessions, work_assignments)
9. **RBAC Tables** (users, roles, teams, permissions, ci_acl)
10. **Merge Tables** (merge_sessions, conflicts, id_mappings, source_instances)
11. **Audit Tables** (activity_log, audit_trail)

**Detailed schema:** See `03_DESIGN/LLD_Database_Schema_Design.md`

**Design Decisions:**
- **PostgreSQL** chosen for:
  - ACID compliance (critical for safety-critical documentation)
  - JSON support (flexible storage of AI context, merge metadata)
  - Advanced indexing (GIN, GiST for full-text search)
  - Mature backup/replication
  - Strong constraint enforcement (foreign keys, check constraints)
- **Hybrid IDs** prevent collision during multi-instance merge
- **Soft deletes** preserve audit trail
- **No ORM-generated schemas** - explicit DDL for DO-178C traceability

### 4.4 AI Engine (Intelligence Layer)

**Technology:** Claude API (primary), LM Studio/Mistral (local fallback)

**Responsibilities:**
- Natural language understanding
- Requirements extraction from conversation
- Design gap analysis
- Merge conflict resolution suggestions
- Duplicate CI detection
- Document generation assistance

**Integration Approach:**
- Backend calls AI via HTTP API
- AI responses parsed and structured by backend
- AI context stored in database (ai_conversations table)
- AI does NOT directly access database
- Backend provides AI with necessary context (PROJECT_PLAN.md, current requirements, etc.)

**AI Capabilities:**

#### 4.4.1 Requirements Elicitation
- Ask one question at a time
- Extract requirements from user responses
- Classify requirements (functional, performance, safety, interface)
- Assign requirement IDs
- **Traces to:** REQ-AI-001 through REQ-AI-010

#### 4.4.2 Project Initialization Interview
- Structured questioning (Foundation → Planning → Execution)
- Determine safety criticality, DAL/SIL
- Identify applicable standards
- Recommend development process
- **Draft project creation:** Creates project record with status "initializing" on first message
- **Conversation persistence:** All messages saved to ai_conversations/ai_messages tables
- **Context memory:** Full conversation history passed to AI for continuity
- **Traces to:** REQ-AI-032 through REQ-AI-037, REQ-AI-028 through REQ-AI-030, REQ-BE-030

#### 4.4.3 Product Structure Extraction
- Parse user-provided documents (BOM, product spec)
- Extract hierarchical product structure
- Identify CIs and relationships
- **Traces to:** REQ-AI-038, REQ-AI-039

#### 4.4.4 AI-Assisted Merge Conflict Resolution
- Analyze conflicting CI data from different instances
- Identify conflict type
- Suggest resolution with confidence score
- Provide rationale
- **Traces to:** REQ-AI-041

#### 4.4.5 Duplicate Detection
- Compare CIs from different instances
- Identify potential duplicates based on semantic similarity
- Suggest merge or keep separate
- **Traces to:** REQ-AI-042

**Design Decisions:**
- **Claude API** chosen for superior context window and instruction-following
- **Local fallback** (LM Studio/Mistral) for air-gapped environments
- **Backend-mediated** (not direct DB access) for security and traceability
- **Structured outputs** (JSON) for reliable parsing

---

### 4.5 AI Controller Architecture

The AI Controller is the critical component that enables stateless AI operation with full context awareness.

#### 4.5.1 Core Principle: Stateless AI with External Memory

```
┌─────────────────────────────────────────────────────────────┐
│                    AI ARCHITECTURE                          │
│                                                             │
│  ┌─────────────┐    ┌──────────────────┐    ┌───────────┐ │
│  │  Frontend   │───▶│   AI Controller  │───▶│    LLM    │ │
│  │  (React)    │    │  (Context Build) │    │ (Stateless)│ │
│  └─────────────┘    └──────────────────┘    └───────────┘ │
│         ▲                    │                     │       │
│         │                    ▼                     │       │
│         │           ┌──────────────────┐          │       │
│         │           │    PostgreSQL    │          │       │
│         │           │  (State Storage) │◀─────────┘       │
│         │           └──────────────────┘                  │
│         │                    │                            │
│         └────────────────────┘                            │
│              (Response via API)                           │
└─────────────────────────────────────────────────────────────┘
```

**Key Insight:** The LLM is stateless - it has no memory between calls. All project context is stored in PostgreSQL and rebuilt for every AI interaction.

**Traces to:** REQ-AI-045 (Stateless AI with External Context)

#### 4.5.2 Context Snapshot Builder

The `get_ai_context()` function constructs the complete context for each AI call:

```python
def get_ai_context(project_id: int, work_item_id: int = None) -> AIContext:
    """
    Build complete context snapshot for AI call.

    Returns:
        AIContext containing:
        - project_metadata: Project name, DAL/SIL, standards, domain
        - relevant_requirements: Requirements related to current work item
        - current_work_item: Active requirement/CI/document being edited
        - conversation_history: Last N messages (configurable)
        - system_instructions: AI guardrails and behavior rules
    """
```

**Context Elements:**

| Element | Source | Max Tokens |
|---------|--------|------------|
| System Instructions | Static prompts | ~500 |
| Project Metadata | projects table | ~200 |
| Current Work Item | requirements/CIs | ~500 |
| Relevant History | ai_messages | ~2000 |
| Related Requirements | requirements | ~1000 |
| **Total Budget** | | ~4200 |

**Token Management:**
- Context truncated to fit model's max window
- Most recent history prioritized
- Summarization for older context if needed

**Traces to:** REQ-AI-046 (Context Snapshot Builder)

#### 4.5.3 Dynamic System Prompt Construction

Every AI call receives a dynamically constructed system prompt:

```
SYSTEM PROMPT STRUCTURE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ROLE DEFINITION]
You are the AISET {role_name} assistant.

[BEHAVIOR RULES]
- Ask only ONE question at a time
- PROPOSE options, never DECIDE
- Use simple, clear language
- Follow DO-178C compliance guidelines

[PROJECT CONTEXT]
Project: {project_name}
Standards: {applicable_standards}
DAL/SIL: {assurance_level}
Domain: {industry_domain}

[CURRENT WORK ITEM]
{work_item_details}

[CONVERSATION HISTORY]
{last_n_messages}

[SPECIFIC INSTRUCTIONS FOR THIS CALL]
{task_specific_instructions}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Traces to:** REQ-AI-047 (Dynamic System Prompt Construction)

---

### 4.6 AI Guardrails Middleware

The Guardrails Middleware validates all AI responses before returning to users.

#### 4.6.1 Guardrails Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 GUARDRAILS MIDDLEWARE                       │
│                                                             │
│  AI Response ──▶ ┌─────────────────────────────────────┐   │
│                  │  1. Decision Detection Guard        │   │
│                  │     - Block "You must...", "Best is"│   │
│                  ├─────────────────────────────────────┤   │
│                  │  2. Single Question Guard           │   │
│                  │     - Count "?" ≤ 1                 │   │
│                  ├─────────────────────────────────────┤   │
│                  │  3. Complexity Guard                │   │
│                  │     - Check sentence length         │   │
│                  │     - Flag jargon                   │   │
│                  └─────────────────────────────────────┘   │
│                              │                             │
│                    ┌─────────┴─────────┐                   │
│                    ▼                   ▼                   │
│               [PASS]              [BLOCK]                  │
│            Return to user      Request AI retry            │
│                                or return safe message      │
└─────────────────────────────────────────────────────────────┘
```

#### 4.6.2 Guard Implementations

**1. Decision Detection Guard (REQ-AI-049)**

```python
BLOCKED_PATTERNS = [
    r"you must choose",
    r"you should use",
    r"the best .* is",
    r"the correct .* is",
    r"i recommend you",
    r"you need to"
]

def check_decision_guard(response: str) -> GuardResult:
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, response.lower()):
            return GuardResult(
                passed=False,
                reason=f"Decision detected: {pattern}",
                action="retry_with_softer_prompt"
            )
    return GuardResult(passed=True)
```

**2. Single Question Guard (REQ-AI-050)**

```python
def check_question_guard(response: str) -> GuardResult:
    question_count = response.count("?")
    if question_count > 1:
        return GuardResult(
            passed=False,
            reason=f"Multiple questions: {question_count}",
            action="truncate_to_first_question"
        )
    return GuardResult(passed=True)
```

**3. Complexity Guard (REQ-AI-051)**

```python
def check_complexity_guard(response: str) -> GuardResult:
    sentences = response.split(".")
    avg_length = sum(len(s.split()) for s in sentences) / len(sentences)

    if avg_length > 25:  # More than 25 words per sentence
        return GuardResult(
            passed=False,
            reason=f"High complexity: {avg_length:.1f} words/sentence",
            action="flag_for_simplification"
        )
    return GuardResult(passed=True)
```

**Traces to:** REQ-AI-048 through REQ-AI-051

---

### 4.7 AI Role Architecture

Three distinct AI roles with separate static system prompts.

#### 4.7.1 Role Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AI ROLES                                 │
│                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐         │
│  │  SYSTEM ENGINEER AI │  │  DOCUMENT WRITER AI │         │
│  │                     │  │                     │         │
│  │  Input: User answers│  │  Input: Structured  │         │
│  │  Output: Questions, │  │         entities    │         │
│  │          Requirements│  │  Output: Markdown   │         │
│  │                     │  │          documents  │         │
│  └─────────────────────┘  └─────────────────────┘         │
│                                                             │
│  ┌─────────────────────┐                                   │
│  │  CODE ASSISTANT AI  │                                   │
│  │                     │                                   │
│  │  Input: File/func   │                                   │
│  │         specification│                                   │
│  │  Output: Code edits │                                   │
│  │          (single file)│                                  │
│  └─────────────────────┘                                   │
└─────────────────────────────────────────────────────────────┘
```

#### 4.7.2 Role Prompts (Static)

**System Engineer AI Prompt:**
```
You are the AISET System Engineer assistant.

CAPABILITIES:
- Ask clarifying questions about requirements
- Identify gaps in requirements
- Classify requirements (functional, performance, safety)
- Suggest requirement decomposition

CONSTRAINTS:
- Ask ONE question at a time
- NEVER generate code
- NEVER generate documents
- ONLY propose, never decide
- Use simple language
```

**Document Writer AI Prompt:**
```
You are the AISET Document Writer assistant.

CAPABILITIES:
- Generate SRS sections from requirements
- Generate SDD sections from design elements
- Generate RTM (Requirements Traceability Matrix)
- Format output in Markdown

CONSTRAINTS:
- NEVER ask questions
- NEVER make design decisions
- ONLY generate documents from provided data
- Follow DO-178C document templates
```

**Code Assistant AI Prompt:**
```
You are the AISET Code Assistant.

CAPABILITIES:
- Generate Python/TypeScript code
- Edit existing files
- Add new functions/classes
- Write unit tests

CONSTRAINTS:
- Work on ONE file at a time
- Use ONLY existing models and architecture
- NEVER modify database schema
- NEVER modify API contracts without approval
- Follow project coding standards
```

**Traces to:** REQ-AI-052 through REQ-AI-055

---

### 4.8 Micro-Interaction Pattern

#### 4.8.1 Interaction Flow

```
┌─────────────────────────────────────────────────────────────┐
│              MICRO-INTERACTION LOOP                         │
│                                                             │
│     ┌──────────┐        ┌──────────┐        ┌──────────┐  │
│     │   AI     │        │  Human   │        │   AI     │  │
│     │ Question │───────▶│  Answer  │───────▶│ Question │  │
│     └──────────┘        └──────────┘        └──────────┘  │
│          │                   │                   │         │
│          ▼                   ▼                   ▼         │
│     ┌─────────────────────────────────────────────────┐   │
│     │              DATABASE (ai_messages)             │   │
│     │   - Store every message                         │   │
│     │   - Store every decision                        │   │
│     │   - Rebuild context for next call               │   │
│     └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Benefits:**
1. AI never needs long-term memory
2. Every interaction is auditable
3. Matches DO-178C "single change - human approval" pattern
4. Context can be rebuilt at any time

**Traces to:** REQ-AI-056 through REQ-AI-058

---

## 5. Data Flow

### 5.1 Project Initialization Interview Flow

```
User starts wizard → Frontend → POST /api/v1/projects/initialize
                                      ↓
                         Backend: Create draft project (status="initializing")
                                      ↓
                         Backend: Create ai_conversation record
                                      ↓
                         Backend: Save user message to ai_messages
                                      ↓
                         Backend: Load full conversation history
                                      ↓
                         Backend → AI Engine (with conversation history)
                                      ↓
                         AI generates contextual response
                                      ↓
                         Backend: Save AI response to ai_messages
                                      ↓
                         Backend: Update conversation context
                                      ↓
                         Return: project_id, conversation_id, next_question
                                      ↓
                         Frontend: Display response, track IDs for next call
```

**Key Design Points:**
- Project and conversation created on FIRST message (not after completion)
- Full conversation history passed to AI enables memory/context
- Frontend tracks project_id and conversation_id for subsequent calls
- **Traces to:** REQ-AI-028, REQ-AI-029, REQ-AI-030, REQ-BE-030, REQ-DB-018, REQ-DB-034

### 5.2 Requirements Elicitation Flow

```
User Input → Frontend → Backend → AI Engine
                                      ↓
                            AI extracts requirement
                                      ↓
                    Backend writes to 'requirements' table
                                      ↓
                    Backend marks document for review
                                      ↓
                    Backend returns AI response
                                      ↓
                    Frontend displays response + updated document list
```

### 5.3 Check-out/Check-in Flow (Pessimistic Locking)

**Check-out:**
```
User clicks "Check-out" → Frontend → Backend Lock Manager
                                            ↓
                                    Check if CI locked?
                                    ↓ No          ↓ Yes
                            Create lock        Return error
                            (ci_locks table)   (locked by X)
                                    ↓
                            Return success
                                    ↓
                            Frontend shows "Checked out by YOU"
```

**Check-in:**
```
User clicks "Check-in" → Frontend → Backend Lock Manager
                                            ↓
                                    Validate lock ownership
                                    ↓ Valid       ↓ Invalid
                            Delete lock        Return error
                            Increment version
                            Update audit trail
                                    ↓
                            Return success
                                    ↓
                            Frontend shows "Available"
```

### 5.3 Multi-Instance Merge Flow

**Export (Source Instance):**
```
User → Export CIs → Backend Export Engine
                            ↓
                    Query database (CIs + related data)
                            ↓
                    Include source instance metadata
                            ↓
                    Generate export package (JSON/XML)
                            ↓
                    User downloads file
```

**Import (Target Instance):**
```
User uploads export file → Backend Import Engine
                                    ↓
                            Validate package integrity
                                    ↓
                            Parse and analyze CIs
                                    ↓
                            Detect conflicts (5 types)
                                    ↓
                            No conflicts?    Conflicts?
                            ↓                ↓
                    Auto-merge           Invoke Merge Engine
                    (new CIs,            (AI-assisted or manual)
                     identical CIs)              ↓
                            ↓                Present conflicts to user
                            ↓                User resolves
                            ↓                ↓
                    Write to database (with source instance tracking)
                            ↓
                    Update id_mapping table
                            ↓
                    Store merge metadata
                            ↓
                    Return success + conflict report
```

### 5.4 RBAC Authorization Flow

```
User requests operation → Backend API endpoint
                                    ↓
                        Authentication (JWT validation)
                                    ↓
                        Retrieve user roles + teams
                                    ↓
                        Check operation permission:
                        1. User-level role permissions
                        2. Team-level permissions
                        3. CI-level ACL (if CI operation)
                                    ↓
                        Authorized?  Not authorized?
                        ↓            ↓
                Execute         Return 403 Forbidden
                operation
                        ↓
                Log in activity_log
                        ↓
                Return result
```

---

## 6. External Interfaces

### 6.1 User Interface (Frontend ↔ User)

**Input Devices:**
- Keyboard (text entry, shortcuts)
- Mouse (navigation, selection)
- File upload (drag-and-drop or file picker)

**Output Devices:**
- Display (1920x1080 minimum recommended)
- PDF generation for document export

**Accessibility:**
- WCAG 2.1 AA compliance (planned)
- Keyboard navigation support
- Screen reader compatibility (planned)

### 6.2 REST API (Frontend ↔ Backend)

**Protocol:** HTTPS (TLS 1.2 or higher)
**Data Format:** JSON
**Authentication:** JWT (JSON Web Token)
**API Specification:** OpenAPI 3.0

**Key Endpoint Categories:**
- `/api/projects/` - Project management
- `/api/conversations/` - AI conversation management
- `/api/requirements/` - Requirements CRUD
- `/api/cis/` - Configuration Item management
- `/api/locks/` - Lock management (check-out/check-in)
- `/api/merge/` - Import/export and merge operations
- `/api/users/` - User and RBAC management

**Detailed API spec:** See `03_DESIGN/Interface_Specifications/API_Specification.md` (planned)

### 6.3 AI API (Backend ↔ AI Engine)

**Claude API:**
- Protocol: HTTPS
- Authentication: API key
- Rate limiting: Configurable
- Timeout: 60 seconds
- Retry strategy: Exponential backoff

**Local AI (LM Studio/Mistral):**
- Protocol: HTTP (localhost only)
- Port: Configurable (default 1234)
- No authentication (localhost trusted)

### 6.4 Database Interface (Backend ↔ Database)

**Protocol:** PostgreSQL wire protocol (TCP/IP)
**Port:** 5432 (default)
**Authentication:** Username/password (from environment variables)
**Connection Pooling:** Yes (managed by backend)
**ORM:** SQLAlchemy (planned) or raw SQL with parameterized queries

### 6.5 File Storage Interface

**Local Filesystem:**
- Uploaded documents stored in `/uploads/`
- Export packages stored in `/exports/`
- Logs stored in `/logs/`

**Planned Cloud Storage:**
- S3-compatible API (optional)
- For backup and distributed deployment

---

## 7. Design Constraints and Assumptions

### 7.1 Constraints

**Performance:**
- Support up to 100 concurrent users (same database instance)
- API response time < 1 second (95th percentile)
- Database query time < 500ms (95th percentile)
- AI response time < 30 seconds (conversational queries)

**Scalability:**
- Database size: Up to 1TB (single instance)
- Number of projects: Up to 1000 per instance
- Number of CIs per project: Up to 100,000
- Number of requirements per project: Up to 50,000

**Security:**
- Authentication required for all operations
- RBAC enforced at API level and database level
- Audit trail for all data modifications
- No plaintext password storage (hashed with bcrypt/argon2)
- HTTPS required for frontend-backend communication

**Deployment:**
- Platform: Linux (Ubuntu 20.04+), Windows (WSL2), macOS
- Python version: 3.12+
- Node.js version: 18+
- PostgreSQL version: 15+
- Browser support: Chrome 100+, Firefox 100+, Edge 100+, Safari 15+

**DO-178C Compliance:**
- AISET developed to DAL D
- Formal requirements (SRS)
- Design documentation (this HLD + LLD)
- Code reviews required
- Unit testing required
- Traceability matrix maintained

### 7.2 Assumptions

1. **Network Availability:** Users have reliable network connection to backend
2. **AI API Availability:** Claude API available with acceptable uptime (or local fallback configured)
3. **Database Reliability:** PostgreSQL configured with backups and replication
4. **User Training:** Users receive basic training on AISET usage
5. **Data Ownership:** Each AISET instance has clear data ownership (company/team/site)
6. **Export Security:** Export files transmitted securely between instances
7. **Clock Synchronization:** All AISET instances have synchronized clocks (NTP) for merge conflict resolution

---

## 8. Design Decisions and Rationale

### 8.1 Technology Stack Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|-------------------------|
| React (Frontend) | Strong TypeScript support, component reusability, large ecosystem | Vue.js (less enterprise adoption), Angular (steeper learning curve) |
| FastAPI (Backend) | Automatic OpenAPI generation, async support, Python ecosystem | Django (heavier), Flask (less async support), Node.js/Express (prefer Python for AI) |
| PostgreSQL (Database) | ACID compliance, JSON support, mature, strong constraints | MySQL (weaker JSON), MongoDB (no ACID for multi-doc transactions), SQLite (not enterprise-scale) |
| Claude API (AI) | Superior context window, instruction-following, reasoning | OpenAI GPT-4 (considered), Local-only models (lower quality) |
| REST API | Simplicity, DO-178C tool qualification easier | GraphQL (more complex), gRPC (less browser support) |

### 8.2 Architecture Pattern Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|-------------------------|
| 4-tier architecture | Separation of concerns, testability, scalability | Monolith (not scalable), Microservices (too complex for DAL D) |
| Hybrid IDs (GUID + Display) | Collision-free merge + human readability | GUID only (not human-friendly), Sequential IDs (collisions during merge) |
| Pessimistic locking (check-out/check-in) | Prevent conflicts in concurrent scenarios, PLM industry standard | Optimistic-only (too many conflicts), No locking (data corruption risk) |
| Backend-mediated AI | Security, traceability, auditability | Direct DB access by AI (security risk, untraced changes) |
| Soft deletes | Audit trail preservation, regulatory compliance | Hard deletes (lose history), Archive tables (complexity) |

### 8.3 Collaborative Architecture Decisions

| Decision | Rationale | User Input |
|----------|-----------|------------|
| Support BOTH concurrent AND distributed | User requirement for all scenarios | Q1: "Both equally important" |
| Milestone-based merge (not real-time sync) | Stability, controlled integration points | Q3: "Milestone-based merges" |
| Semi-automatic merge (AI suggests, human approves) | Balance automation with safety oversight | Q4: "Semi-automatic merge" |
| Complex RBAC (7 roles, 3 permission levels) | Enterprise requirements, supplier access control | Q6: "Complex access control" |

---

## 9. Safety and Security Considerations

### 9.1 Safety

**AISET Tool Safety (DAL D):**
- AISET is a development tool, not airborne software
- Tool qualification required if verification automation used
- Incorrect AISET operation could introduce errors into user's safety-critical system

**Mitigations:**
- User review required for all AI-generated content (REQ-AI-025)
- Documents marked "needs review" after AI modification
- Audit trail of all changes
- Traceability to source (manual input vs AI-generated)

**User System Safety:**
- AISET shall NOT make safety-critical decisions
- AISET shall NOT automatically approve verification results
- AISET shall NOT bypass user project DAL requirements

### 9.2 Security

**Threats:**
1. Unauthorized access to safety-critical data
2. Data corruption (malicious or accidental)
3. Data exfiltration (export to unauthorized parties)
4. Injection attacks (SQL, XSS, command injection)
5. Session hijacking

**Mitigations:**
1. RBAC with CI-level ACL (REQ-DB-059)
2. Audit trail + activity log (REQ-DB-064, REQ-DB-068)
3. Export requires authorization, logged in audit trail
4. Parameterized SQL queries, input validation, output sanitization
5. JWT with short expiration, HTTPS only, secure cookie flags

**Security Testing:**
- Penetration testing (planned)
- OWASP Top 10 vulnerability scanning (planned)
- Code security review (planned)

---

## 10. Traceability to Requirements

### 10.1 High-Level Traceability

This HLD addresses the following requirement categories from REQUIREMENTS.md v0.8.0:

| Requirement Category | HLD Section | Notes |
|---------------------|-------------|-------|
| REQ-AI-001 to REQ-AI-044 | Section 4.4 (AI Engine) | AI capabilities and integration |
| REQ-FE-001 to REQ-FE-023 | Section 4.1 (Frontend) | UI components and interfaces |
| REQ-BE-001 to REQ-BE-029 | Section 4.2 (Backend) | Business logic modules |
| REQ-DB-001 to REQ-DB-070 | Section 4.3 (Database) | Database architecture overview |

### 10.2 Key Architectural Requirements

| Requirement ID | Requirement Summary | HLD Section |
|----------------|---------------------|-------------|
| REQ-AI-032 to REQ-AI-037 | Project initialization interview | 4.4.2 |
| REQ-AI-038 to REQ-AI-040 | Product structure extraction | 4.4.3 |
| REQ-AI-041 | AI-assisted merge conflict resolution | 4.2.7, 4.4.4 |
| REQ-FE-008 | Dual interface (chat + proposal) | 4.1.2 |
| REQ-FE-010 | Product structure tree UI | 4.1.3 |
| REQ-FE-014 | Check-out/check-in UI | 4.1.6 |
| REQ-BE-016 | Pessimistic locking | 4.2.3 |
| REQ-BE-021 | Intelligent merge engine | 4.2.7 |
| REQ-BE-024 | RBAC enforcement | 4.2.8 |
| REQ-DB-052 | Hybrid identifier system | 4.3 |
| REQ-DB-054 | Lock management | 4.3 |
| REQ-DB-057 to REQ-DB-059 | RBAC tables | 4.3 |

**Detailed traceability matrix:** See `08_TRACEABILITY/Requirements_to_Design_Traceability.md` (planned)

---

## 11. Design Verification

### 11.1 Verification Strategy

This HLD will be verified through:

1. **Design Review** - Formal review by design team, safety engineer, QA
2. **HLD-to-Requirements Traceability Analysis** - Ensure all requirements addressed
3. **Architecture Consistency Analysis** - Ensure components interact as specified
4. **Interface Definition Review** - Ensure interfaces well-defined and complete
5. **Safety/Security Review** - Ensure safety and security considerations addressed

### 11.2 Design Review Checklist

- [ ] All requirements from REQUIREMENTS.md v0.8.0 addressed
- [ ] Component responsibilities clearly defined
- [ ] Interfaces between components specified
- [ ] Data flow documented
- [ ] Technology choices justified
- [ ] Design constraints identified
- [ ] Assumptions documented
- [ ] Safety considerations addressed
- [ ] Security considerations addressed
- [ ] Traceability to requirements established
- [ ] Compliance with DO-178C DAL D objectives

---

## 12. Open Issues and Future Work

### 12.1 Open Issues

1. **Cloud deployment architecture** - Not yet specified (single-server only)
2. **Disaster recovery** - Backup/restore procedures not detailed
3. **Performance benchmarking** - Performance targets defined but not validated
4. **AI prompt engineering** - AI prompts not yet formalized in design
5. **API versioning strategy** - API version management not specified

### 12.2 Future Enhancements (Out of Scope for v1.0)

1. **Real-time collaboration** - Google Docs-style simultaneous editing
2. **Mobile app** - Native iOS/Android apps
3. **Offline mode** - Work without network, sync later
4. **Advanced analytics** - Project dashboards with charts, metrics
5. **Integration with PLM systems** - Siemens Teamcenter, PTC Windchill connectors

---

## 13. References

### 13.1 AISET Internal Documents

- REQUIREMENTS.md v0.8.0
- ROLEPLAY_RULES.md
- ROLEPLAY_SESSION.md
- Claude.md
- PROJECT_STATUS.md
- DOCUMENTATION_LEVELS.md
- docs/Level_2_User_Framework/CONFIGURATION_ITEM_MANAGEMENT.md
- docs/Level_1_AISET_Development/DATABASE_SCHEMA.md

### 13.2 External Standards

- DO-178C: Software Considerations in Airborne Systems and Equipment Certification, RTCA, 2011
- ARP4754A: Guidelines for Development of Civil Aircraft and Systems, SAE International, 2010
- DO-254: Design Assurance Guidance for Airborne Electronic Hardware, RTCA, 2000
- ISO 26262: Road vehicles - Functional safety, ISO, 2018
- IEC 62304: Medical device software - Software life cycle processes, IEC, 2006

---

**END OF HIGH-LEVEL DESIGN DOCUMENT**

---

**Document Status:** Draft - Awaiting Review
**Next Steps:**
1. Review and approval by design team
2. Create Database LLD (detailed schema design)
3. Create Interface Specifications (detailed API spec)
4. Create traceability matrix (Requirements → HLD)
5. Update as design evolves
