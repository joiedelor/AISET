# AI_INSTRUCTION.md
## Database Schema and Data Formatting Guide for AISET AI

---

## Document Purpose

This document provides the AISET AI with complete knowledge of:
1. Database schema structure (47 tables)
2. Data formatting rules
3. Correct data insertion patterns
4. Validation requirements
5. Business logic constraints

**Target AI:** Claude API (primary), LM Studio (fallback)
**DO-178C Traceability:** REQ-DOC-001, REQ-AI-006, REQ-AI-007, REQ-AI-008

---

## 1. Database Overview

### 1.1 Database Information
- **Database Type:** PostgreSQL 15+
- **Total Tables:** 47
- **Schema Version:** 1.0.0
- **Design Principles:**
  - Hybrid Identifiers: `guid` (UUID) + `display_id` (human-readable)
  - Audit Trail: `created_at`, `updated_at`, `created_by_guid`, `updated_by_guid`
  - Soft Deletes: `deleted_at` (NULL = active)
  - Version Stamping: `version` field for optimistic locking
  - Referential Integrity: All foreign keys enforced

### 1.2 Common Fields (On ALL Tables)

Every table has these standard fields:

```sql
guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid()
display_id           VARCHAR(50) NOT NULL UNIQUE
created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
created_by_guid      UUID REFERENCES users(guid)
updated_by_guid      UUID REFERENCES users(guid)
deleted_at           TIMESTAMP  -- NULL = active, non-NULL = soft deleted
version              INTEGER NOT NULL DEFAULT 1
```

---

## 2. Core Entity Tables

### 2.1 Users Table

**Purpose:** User accounts with authentication

```sql
TABLE users (
    guid                 UUID PRIMARY KEY,
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    username             VARCHAR(100) NOT NULL UNIQUE,
    email                VARCHAR(255) NOT NULL UNIQUE,
    full_name            VARCHAR(255) NOT NULL,
    password_hash        VARCHAR(255) NOT NULL,  -- bcrypt/argon2
    user_status          VARCHAR(50) DEFAULT 'active',
    last_login           TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked_until TIMESTAMP,
    preferences          JSONB DEFAULT '{}'::jsonb,
    ... standard audit fields ...
)
```

**Valid user_status values:** 'active', 'suspended', 'inactive', 'locked'

**Example Data Insertion:**
```json
{
    "display_id": "USER-001",
    "username": "jsmith",
    "email": "john.smith@example.com",
    "full_name": "John Smith",
    "password_hash": "$2b$12$...",  // bcrypt hash
    "user_status": "active",
    "preferences": {
        "theme": "dark",
        "notifications_enabled": true
    }
}
```

### 2.2 Projects Table

**Purpose:** Engineering projects

```sql
TABLE projects (
    guid                 UUID PRIMARY KEY,
    display_id           VARCHAR(50) NOT NULL UNIQUE,  -- e.g., "PROJ-FCS-001"
    name                 VARCHAR(255) NOT NULL,
    project_code         VARCHAR(100) NOT NULL UNIQUE,
    description          TEXT,
    project_type         VARCHAR(100),
    industry_sector      VARCHAR(100),
    safety_critical      BOOLEAN DEFAULT false,
    certification_level  VARCHAR(50),  -- DAL A/B/C/D or SIL 1/2/3/4
    project_status       VARCHAR(50) DEFAULT 'active',
    lifecycle_phase      VARCHAR(100),
    start_date           DATE,
    target_completion    DATE,
    ... standard audit fields ...
)
```

**Valid project_status:** 'active', 'on_hold', 'completed', 'cancelled'
**Valid lifecycle_phase:** 'concept', 'requirements', 'architecture', 'design', 'implementation', 'verification', 'certification', 'production', 'maintenance'
**Valid certification_level:** 'DAL-A', 'DAL-B', 'DAL-C', 'DAL-D', 'SIL-1', 'SIL-2', 'SIL-3', 'SIL-4', 'None'

**Example:**
```json
{
    "display_id": "PROJ-FCS-001",
    "name": "Flight Control System",
    "project_code": "FCS-2025",
    "description": "Primary flight control software for commercial aircraft",
    "project_type": "Software Development",
    "industry_sector": "Aerospace",
    "safety_critical": true,
    "certification_level": "DAL-A",
    "project_status": "active",
    "lifecycle_phase": "requirements"
}
```

### 2.3 Requirements Table

**Purpose:** System requirements

```sql
TABLE requirements (
    guid                 UUID PRIMARY KEY,
    display_id           VARCHAR(50) NOT NULL,  -- e.g., "REQ-FCS-001"
    project_guid         UUID NOT NULL REFERENCES projects(guid),
    requirement_id       VARCHAR(100) NOT NULL,  -- Duplicate of display_id for compatibility
    title                VARCHAR(500) NOT NULL,
    description          TEXT NOT NULL,
    type                 VARCHAR(100) NOT NULL,
    priority             VARCHAR(50) NOT NULL,
    status               VARCHAR(50) DEFAULT 'draft',
    rationale            TEXT,
    acceptance_criteria  TEXT,
    verification_method  VARCHAR(100),
    source               VARCHAR(255),
    confidence_score     NUMERIC(3,2) DEFAULT 1.0,  -- 0.00 to 1.00
    parent_guid          UUID REFERENCES requirements(guid),
    ... standard audit fields ...
)
```

**Valid type:** 'functional', 'performance', 'safety', 'security', 'interface', 'operational', 'design_constraint', 'data'
**Valid priority:** 'critical', 'high', 'medium', 'low'
**Valid status:** 'draft', 'proposed', 'pending_review', 'approved', 'rejected', 'implemented', 'verified'
**Valid verification_method:** 'test', 'analysis', 'inspection', 'demonstration'

**Example:**
```json
{
    "display_id": "REQ-FCS-001",
    "project_guid": "uuid-of-project",
    "requirement_id": "REQ-FCS-001",
    "title": "Autopilot Engagement",
    "description": "The system shall engage the autopilot within 2 seconds of pilot command",
    "type": "functional",
    "priority": "critical",
    "status": "approved",
    "rationale": "Timely autopilot engagement is critical for flight safety",
    "acceptance_criteria": "Measured engagement time < 2 seconds in 100% of test cases",
    "verification_method": "test",
    "source": "Customer Specification CS-100-REQ",
    "confidence_score": 0.95,
    "parent_guid": null
}
```

### 2.4 Configuration Items Table

**Purpose:** Product structure and BOM (34+ metadata fields)

```sql
TABLE configuration_items (
    guid                      UUID PRIMARY KEY,
    display_id                VARCHAR(50) NOT NULL,
    project_guid              UUID NOT NULL REFERENCES projects(guid),
    parent_guid               UUID REFERENCES configuration_items(guid),

    -- Core Identification (5 fields)
    ci_identifier             VARCHAR(100) NOT NULL,
    ci_name                   VARCHAR(255) NOT NULL,
    ci_type                   VARCHAR(100) NOT NULL,
    part_number               VARCHAR(100),
    description               TEXT,

    -- Configuration Management (5 fields)
    baseline_status           VARCHAR(100),
    configuration_control_level INTEGER,
    change_count              INTEGER DEFAULT 0,
    baseline_version          VARCHAR(50),
    effectivity               VARCHAR(255),

    -- Traceability (3 fields)
    parent_requirements       TEXT[],  -- Array of requirement GUIDs
    derived_from              TEXT[],  -- Array of CI GUIDs
    allocated_to              TEXT[],  -- Array of CI GUIDs

    -- Development & Quality (4 fields)
    design_authority          VARCHAR(255),
    responsible_engineer      VARCHAR(255),
    current_lifecycle_phase   VARCHAR(100),
    quality_status            VARCHAR(100),

    -- Change Management (3 fields)
    last_change_date          DATE,
    last_change_reason        TEXT,
    change_approval_status    VARCHAR(100),

    -- Lifecycle & Ownership (4 fields)
    development_status        VARCHAR(100),
    integration_status        VARCHAR(100),
    supplier_source           VARCHAR(255),
    make_or_buy_decision      VARCHAR(50),

    -- Manufacturing (4 fields)
    manufacturing_process     TEXT,
    procurement_status        VARCHAR(100),
    lead_time_days            INTEGER,
    critical_supplier         VARCHAR(255),

    -- Documentation (2 fields)
    associated_documents      TEXT[],
    data_package_references   TEXT[],

    -- Verification & Certification (2 fields)
    verification_status       VARCHAR(100),
    certification_status      VARCHAR(100),

    -- Safety & Security (2 fields)
    safety_classification     VARCHAR(100),
    security_classification   VARCHAR(100),

    -- Data Rights & Export Control (2 fields)
    data_rights_classification VARCHAR(100),
    export_control_classification VARCHAR(100),

    ... standard audit fields ...
)
```

**Valid ci_type:** 'system', 'subsystem', 'assembly', 'component', 'part', 'software', 'hardware', 'document'
**Valid make_or_buy_decision:** 'make', 'buy', 'both', 'TBD'

**Example:**
```json
{
    "display_id": "CI-FCS-CTRL-001",
    "project_guid": "uuid-of-project",
    "parent_guid": "uuid-of-parent-ci",
    "ci_identifier": "FCS-CTRL-001",
    "ci_name": "Flight Control Computer",
    "ci_type": "hardware",
    "part_number": "P/N-12345-A",
    "description": "Primary flight control computer unit",
    "baseline_status": "released",
    "configuration_control_level": 1,
    "design_authority": "ACME Aerospace",
    "responsible_engineer": "Jane Doe",
    "current_lifecycle_phase": "production",
    "safety_classification": "Safety-Critical",
    "certification_status": "DO-254 Certified"
}
```

### 2.5 AI Conversations Table

**Purpose:** Store AI chat sessions

```sql
TABLE ai_conversations (
    guid                 UUID PRIMARY KEY,
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    project_guid         UUID NOT NULL REFERENCES projects(guid),
    conversation_id      INTEGER,  -- Legacy integer ID
    title                VARCHAR(500),
    purpose              VARCHAR(100),
    ai_service           VARCHAR(100),
    model_name           VARCHAR(100),
    conversation_status  VARCHAR(50) DEFAULT 'active',
    context_data         JSONB DEFAULT '{}'::jsonb,
    ... standard audit fields ...
)
```

**Valid purpose:** 'requirements_elicitation', 'design_review', 'traceability_analysis', 'general'
**Valid conversation_status:** 'active', 'paused', 'completed', 'archived'

### 2.6 AI Messages Table

**Purpose:** Individual messages in conversations

```sql
TABLE ai_messages (
    guid                 UUID PRIMARY KEY,
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    conversation_guid    UUID NOT NULL REFERENCES ai_conversations(guid),
    conversation_id      INTEGER,  -- Legacy reference
    role                 VARCHAR(50) NOT NULL,
    content              TEXT NOT NULL,
    message_metadata     JSONB DEFAULT '{}'::jsonb,
    tokens_used          INTEGER,
    ... standard audit fields ...
)
```

**Valid role:** 'user', 'assistant', 'system'

**Example:**
```json
{
    "display_id": "MSG-001",
    "conversation_guid": "uuid-of-conversation",
    "role": "user",
    "content": "Can you describe the project as precisely as you can?",
    "message_metadata": {},
    "tokens_used": 15
}
```

---

## 3. Data Formatting Rules

### 3.1 Display ID Format

**Pattern:** `{PREFIX}-{IDENTIFIER}`

**Standard Prefixes:**
- `USER-XXX` - Users
- `PROJ-XXX` - Projects
- `REQ-XXX-YYY` - Requirements (XXX = project code)
- `CI-XXX-YYY` - Configuration Items
- `CONV-XXX` - Conversations
- `MSG-XXX` - Messages
- `DOC-XXX` - Documents
- `TEST-XXX` - Test Cases
- `TRACE-XXX` - Traceability Links

**Examples:**
- `USER-001`, `USER-002`
- `PROJ-FCS-001`
- `REQ-FCS-001`, `REQ-FCS-002`
- `CI-FCS-CTRL-001`

### 3.2 GUID Generation

- **Always use:** PostgreSQL `gen_random_uuid()` function
- **Format:** Standard UUID v4
- **Example:** `550e8400-e29b-41d4-a716-446655440000`

### 3.3 Timestamp Format

- **Format:** ISO 8601 with timezone
- **Example:** `2025-11-17T14:30:00Z`
- **Database:** Uses `TIMESTAMP` type with `DEFAULT CURRENT_TIMESTAMP`

### 3.4 JSONB Fields

**Common JSONB fields and their formats:**

**User Preferences:**
```json
{
    "theme": "dark",
    "language": "en",
    "notifications_enabled": true,
    "email_notifications": false
}
```

**Project Context (project_context table):**
```json
{
    "safety_criticality": "DAL-A",
    "applicable_standards": ["DO-178C", "DO-254", "ARP4754A"],
    "development_process": "V-Model",
    "team_size": 15,
    "timeline_months": 24
}
```

### 3.5 Array Fields

**Text Array Format (PostgreSQL):**

In database:
```sql
parent_requirements TEXT[] = '{guid1, guid2, guid3}'
```

In JSON API:
```json
"parent_requirements": ["guid1", "guid2", "guid3"]
```

---

## 4. AI Behavior Guidelines

### 4.1 Requirements Extraction

When extracting requirements from user conversation:

**ALWAYS include:**
1. `title` - One-line summary
2. `description` - Detailed requirement statement using "shall" language
3. `type` - One of the valid types
4. `priority` - Based on criticality assessment
5. `confidence_score` - Your confidence (0.0 to 1.0)

**OPTIONAL but recommended:**
6. `rationale` - Why this requirement exists
7. `acceptance_criteria` - How to verify
8. `verification_method` - test/analysis/inspection/demonstration

**NEVER:**
- Make design decisions for the user
- Auto-approve requirements (always needs user review)
- Create requirements without user input

### 4.2 Single Question Rule (REQ-AI-001)

**CRITICAL:** Ask only ONE question at a time

❌ **WRONG:**
```
"What is the system type? What is the safety level? Who is the responsible engineer?"
```

✅ **CORRECT:**
```
"Can you describe the project as precisely as you can?"
... wait for answer ...
"What is the safety criticality level of this system? (e.g., DAL-A, DAL-B, SIL-1, or not safety-critical)"
... wait for answer ...
"Which regulatory standards apply to this project? (e.g., DO-178C, ISO 26262, IEC 61508)"
```

### 4.3 Simple Language (REQ-AI-002)

**Default:** Use simple, non-technical language

❌ **WRONG:**
```
"Please specify the MTBF reliability metric for the distributed fault-tolerant architecture"
```

✅ **CORRECT:**
```
"How reliable does the system need to be? For example, how often can it fail?"
```

**Exception:** Adapt to technical language if user demonstrates expertise

### 4.4 No Design Decisions (REQ-AI-010)

**AI Role:** Facilitator, NOT designer

❌ **WRONG:**
```
"I'll design this as a microservices architecture with Kubernetes orchestration"
```

✅ **CORRECT:**
```
"For this functionality, there are several architectural options:
1. Microservices (more scalable, more complex)
2. Monolithic (simpler, less scalable)
3. Modular monolith (middle ground)

Which approach would you prefer?"
```

### 4.5 Clarification Requests (REQ-AI-013)

When user input is ambiguous:

✅ **ASK FOR CLARIFICATION:**
```
User: "The system needs to be fast"
AI: "When you say 'fast,' could you help me understand:
- Is this about response time (how quickly it responds to user actions)?
- Or throughput (how many operations per second)?
- What would be acceptable performance? (e.g., respond in under 1 second)"
```

---

## 5. Common Database Operations

### 5.1 Creating a New Project

**Step 1:** Insert project record
```sql
INSERT INTO projects (
    guid, display_id, name, project_code, description,
    safety_critical, certification_level, project_status,
    created_by_guid
) VALUES (
    gen_random_uuid(),
    'PROJ-FCS-001',
    'Flight Control System',
    'FCS-2025',
    'Primary flight control software',
    true,
    'DAL-A',
    'active',
    <current_user_guid>
);
```

**Step 2:** Create initial conversation
```sql
INSERT INTO ai_conversations (
    guid, display_id, project_guid, title, purpose, ai_service
) VALUES (
    gen_random_uuid(),
    'CONV-001',
    <project_guid>,
    'Initial Requirements Elicitation',
    'requirements_elicitation',
    'claude'
);
```

### 5.2 Adding a Requirement

```sql
INSERT INTO requirements (
    guid, display_id, project_guid, requirement_id,
    title, description, type, priority, status,
    confidence_score, created_by_guid
) VALUES (
    gen_random_uuid(),
    'REQ-FCS-001',
    <project_guid>,
    'REQ-FCS-001',
    'Autopilot Engagement Time',
    'The system shall engage the autopilot within 2 seconds of pilot command',
    'functional',
    'critical',
    'proposed',
    0.95,
    <ai_service_user_guid>
);
```

### 5.3 Creating Traceability Link

```sql
INSERT INTO traceability_links (
    guid, display_id, project_guid,
    source_type, source_guid,
    target_type, target_guid,
    link_type, confidence_score
) VALUES (
    gen_random_uuid(),
    'TRACE-001',
    <project_guid>,
    'requirement',
    <requirement_guid>,
    'design_component',
    <design_guid>,
    'implements',
    0.90
);
```

---

## 6. Validation Rules

### 6.1 Required Fields

**NEVER omit these fields:**
- `guid` (use gen_random_uuid())
- `display_id` (must be unique within entity type)
- `created_at` (use CURRENT_TIMESTAMP)
- `version` (start at 1)
- `created_by_guid` (reference to user)

### 6.2 Uniqueness Constraints

**Must be unique:**
- `display_id` within each table
- `username` in users table
- `email` in users table
- `project_code` in projects table
- `requirement_id` within a project (compound uniqueness)

### 6.3 Foreign Key Integrity

**Before inserting:**
1. Verify referenced GUID exists
2. Check that reference is not soft-deleted (deleted_at IS NULL)
3. Ensure user has permission to reference entity

### 6.4 Enumeration Validation

**Always validate against allowed values:**
- `type` fields (see valid values per table)
- `status` fields
- `priority` fields
- `verification_method` fields

---

## 7. ARP4754A Process Framework

**AI should reference:** `docs/Level_2_User_Framework/PROJECT_PLAN.md`

**10-Phase Process:**
1. System Function Development
2. System Requirements Capture
3. System Architecture Development
4. System Design
5. Item Requirements Allocation
6. Implementation
7. Integration
8. Verification
9. Certification Liaison
10. Production Transition

**Guide users through appropriate phase based on project lifecycle_phase**

---

## 8. Error Handling

### 8.1 Common Errors to Avoid

❌ **Missing required fields**
❌ **Invalid enumeration values**
❌ **Duplicate display_id**
❌ **Non-existent foreign key reference**
❌ **Violating check constraints**

### 8.2 Error Messages to User

When database operation fails:
```
"I encountered an issue saving that information. The [field_name] needs to be [requirement].
Could you provide [clarification]?"
```

---

## 9. Performance Considerations

### 9.1 Batch Operations

For multiple requirements/CIs:
- Use batch INSERT when creating >5 items
- Wrap in transaction for consistency

### 9.2 Query Optimization

- Use indexed fields for search (guid, display_id, created_at)
- Filter soft-deleted records: `WHERE deleted_at IS NULL`
- Use project_guid to partition data

---

## 10. Security & Permissions

### 10.1 RBAC Awareness (REQ-AI-044)

**Before providing data or performing actions:**
1. Check user's role (from users table → user_roles → roles)
2. Verify team membership if team-scoped
3. Check CI-level ACL for sensitive items

**Roles:**
- Administrator: Full access
- Project Manager: Project-level admin
- Systems Engineer: Full engineering access
- Requirements Engineer: Requirements editing
- Design Engineer: Design editing
- Verification Engineer: Test access
- Read-Only User: View only

### 10.2 Data Classification

**Respect:**
- `safety_classification` (safety-critical data)
- `security_classification` (classified data)
- `export_control_classification` (ITAR/EAR restrictions)
- `data_rights_classification` (proprietary/restricted)

---

## 11. Complete Table List (47 Tables)

### Section 1: Users and Authentication
1. users
2. roles
3. user_roles
4. teams
5. team_members
6. sessions

### Section 2: Projects
7. projects
8. project_context
9. project_standards
10. project_standards_mapping

### Section 3: Requirements
11. requirements
12. requirement_relationships

### Section 4: Design
13. design_components
14. component_relationships
15. interfaces

### Section 5: Configuration Management
16. configuration_items
17. ci_relationships
18. ci_documents
19. baselines
20. baseline_items

### Section 6: Verification
21. test_cases
22. test_results
23. verification_procedures

### Section 7: Traceability
24. traceability_links

### Section 8: Documents
25. documents
26. document_versions
27. document_relationships

### Section 9: AI Conversations
28. ai_conversations
29. ai_messages

### Section 10: Change Management
30. change_requests
31. change_approvals
32. problem_reports

### Section 11: Audit and History
33. audit_trail
34. activity_log

### Section 12: Collaborative Work
35. locks
36. notifications
37. comments
38. work_assignments

### Section 13: Distributed Development
39. instances
40. id_mappings
41. merge_sessions
42. merge_conflicts
43. external_references
44. data_sharing_policies

### Section 14: Access Control
45. ci_acl
46. team_permissions

### Section 15: Quality
47. duplicate_candidates

---

## 12. Quick Reference Card

### Most Common Operations:

**1. Start new project conversation:**
- Create project → Create conversation → First AI message

**2. Extract requirement from conversation:**
- Parse user input → Create requirement record → Link to project

**3. Create traceability:**
- Link requirement → design component with "implements" type

**4. Store AI message:**
- Insert to ai_messages with conversation_guid reference

**5. Soft delete:**
- UPDATE table SET deleted_at = CURRENT_TIMESTAMP WHERE guid = ?

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-17
**Status:** Complete
**Compliance:** REQ-DOC-001 ✅
