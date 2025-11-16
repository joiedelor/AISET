# AISET - Database Low-Level Design (LLD)
## Database Schema Design

**Document Type:** [Level 1] AISET Tool Development - DO-178C DAL D
**Document Version:** 1.0.0
**Last Updated:** 2025-11-16
**Status:** Draft - In Review
**Applicable Standards:** DO-178C (Software), SQL:2016, PostgreSQL 15+

---

## Document Control

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2025-11-16 | Claude + User | Initial Database LLD creation |

### Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Database Architect | TBD | | |
| Design Lead | TBD | | |
| Quality Assurance | TBD | | |

---

## 1. Introduction

### 1.1 Purpose

This Database Low-Level Design (LLD) document provides the detailed database schema design for the AISET (AI Systems Engineering Tool) PostgreSQL database. This document specifies all tables, columns, data types, constraints, indexes, and relationships required to support AISET's enterprise collaborative functionality.

This document satisfies DO-178C objectives for Low-Level Design and provides traceability from database requirements (REQ-DB-001 through REQ-DB-070) to implementation.

### 1.2 Scope

**In Scope:**
- All database tables (42+ tables)
- Table columns with data types and constraints
- Primary keys, foreign keys, unique constraints
- Indexes for performance optimization
- Database triggers (if any)
- Stored procedures (if any)
- Hybrid identifier system implementation
- Lock management schema
- RBAC schema (users, roles, permissions)
- Merge metadata schema
- Audit trail schema

**Out of Scope:**
- Application-level business logic (see HLD Section 4.2)
- ORM model definitions (backend code)
- Database deployment procedures
- Backup and recovery procedures

### 1.3 Database Technology

**Database Management System:** PostgreSQL 15.0 or higher

**Rationale:**
- ACID compliance (critical for safety-critical documentation)
- Advanced data types (JSON, JSONB, UUID, ARRAY)
- Full-text search capabilities
- Strong constraint enforcement
- Mature replication and backup
- Open source with strong community support

### 1.4 Design Principles

1. **Hybrid Identifiers on All Entities:**
   - `guid` (UUID) - Primary key, globally unique across all AISET instances
   - `display_id` (VARCHAR) - Human-readable identifier for UI display

2. **Audit Trail on All Tables:**
   - `created_at` (TIMESTAMP) - Record creation timestamp
   - `updated_at` (TIMESTAMP) - Last modification timestamp
   - `created_by_guid` (UUID FK) - User who created record
   - `updated_by_guid` (UUID FK) - User who last modified record

3. **Soft Deletes (No Hard Deletes):**
   - `deleted_at` (TIMESTAMP NULL) - Null if active, timestamp if deleted
   - Queries filter `WHERE deleted_at IS NULL` to exclude deleted records

4. **Version Stamping for Optimistic Locking:**
   - `version` (INTEGER) - Incremented on each update
   - Used to detect concurrent modifications

5. **Referential Integrity:**
   - All foreign keys enforced with `ON DELETE` and `ON UPDATE` actions
   - Cascading deletes avoided (use soft deletes)

6. **Normalization:**
   - Database normalized to 3NF (Third Normal Form)
   - Denormalization used sparingly for performance (documented)

---

## 2. Database Schema Overview

### 2.1 Schema Organization

AISET database contains **47 tables** organized into 11 functional groups:

| Group | Tables | Purpose |
|-------|--------|---------|
| **1. Core Project** | 3 tables | Projects, standards, lifecycles |
| **2. Requirements** | 4 tables | Requirements, traceability |
| **3. Design** | 3 tables | Design elements, reviews |
| **4. CI Management** | 8 tables | Configuration items, BOM, suppliers |
| **5. Verification** | 5 tables | Test plans, cases, results |
| **6. Documentation** | 3 tables | Documents, associations |
| **7. AI Conversation** | 3 tables | Conversations, messages, context |
| **8. Collaboration** | 4 tables | Locks, sessions, work assignments |
| **9. RBAC** | 7 tables | Users, roles, teams, permissions, ACL |
| **10. Merge Management** | 5 tables | Merge sessions, conflicts, ID mappings, source tracking |
| **11. Audit & Compliance** | 2 tables | Activity log, audit trail |

**Total:** 47 tables

### 2.2 Hybrid Identifier System

**Every entity uses hybrid identifiers:**

```sql
CREATE TABLE example_table (
    -- Hybrid Identifier System
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,

    -- Business columns
    ...

    -- Audit Trail (standard on all tables)
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP NULL,
    version              INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_example_display_id ON example_table(display_id);
CREATE INDEX idx_example_deleted_at ON example_table(deleted_at) WHERE deleted_at IS NULL;
```

**Hybrid ID Benefits:**
- **GUID (Primary Key):** Globally unique, collision-free during multi-instance merge
- **Display ID:** Human-readable (e.g., "REQ-SYS-001", "CI-SW-042")
- **Traceability:** Display ID used in documents, GUID used internally

**Traces to:** REQ-DB-052

---

## 3. Detailed Table Specifications

### GROUP 1: CORE PROJECT TABLES

#### 3.1 Table: `projects`

Stores top-level project information.

**Traces to:** REQ-DB-001, REQ-DB-035

```sql
CREATE TABLE projects (
    -- Hybrid Identifier
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,  -- e.g., "PROJ-001", "FURN-001"

    -- Project Identification
    project_code         VARCHAR(100) NOT NULL UNIQUE,
    project_name         VARCHAR(255) NOT NULL,
    description          TEXT,

    -- Project Context (REQ-DB-035 - Project initialization)
    safety_critical      BOOLEAN NOT NULL DEFAULT FALSE,
    dal_level            VARCHAR(10) CHECK (dal_level IN ('A', 'B', 'C', 'D', 'N/A')),
    sil_level            VARCHAR(10) CHECK (sil_level IN ('ASIL-A', 'ASIL-B', 'ASIL-C', 'ASIL-D', 'SIL-1', 'SIL-2', 'SIL-3', 'SIL-4', 'N/A')),
    domain               VARCHAR(50),  -- 'aerospace', 'automotive', 'medical', 'industrial', 'other'
    product_type         VARCHAR(100), -- What is being developed
    architecture_type    VARCHAR(100), -- System architecture approach
    requirements_source  VARCHAR(100), -- How requirements will be captured
    supply_chain         VARCHAR(100), -- Internal, suppliers, mixed
    team_size           INTEGER,
    verification_approach VARCHAR(100), -- Verification strategy
    lifecycle_model     VARCHAR(100),  -- V-model, Agile, Waterfall, etc.
    risk_level          VARCHAR(50),   -- HIGH, MEDIUM, LOW

    -- Status
    status               VARCHAR(50) NOT NULL DEFAULT 'active',  -- active, on_hold, completed, archived

    -- Audit Trail
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP NULL,
    version              INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_projects_display_id ON projects(display_id);
CREATE INDEX idx_projects_code ON projects(project_code);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_dal ON projects(dal_level);
CREATE INDEX idx_projects_deleted_at ON projects(deleted_at) WHERE deleted_at IS NULL;
```

#### 3.2 Table: `project_standards`

Stores applicable standards for each project (many-to-many relationship).

**Traces to:** REQ-DB-036

```sql
CREATE TABLE project_standards (
    -- Hybrid Identifier
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,

    -- Relationships
    project_guid         UUID NOT NULL REFERENCES projects(guid),

    -- Standard Information
    standard_name        VARCHAR(100) NOT NULL,  -- e.g., "DO-178C", "ISO 26262", "IEC 62304"
    standard_version     VARCHAR(50),
    compliance_level     VARCHAR(50),  -- Level of compliance required
    mandatory            BOOLEAN NOT NULL DEFAULT TRUE,
    notes                TEXT,

    -- Audit Trail
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP NULL,
    version              INTEGER NOT NULL DEFAULT 1,

    UNIQUE(project_guid, standard_name)
);

CREATE INDEX idx_project_standards_project ON project_standards(project_guid);
CREATE INDEX idx_project_standards_standard ON project_standards(standard_name);
```

#### 3.3 Table: `lifecycles`

Defines development lifecycle phases for projects.

```sql
CREATE TABLE lifecycles (
    -- Hybrid Identifier
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,

    -- Relationships
    project_guid         UUID NOT NULL REFERENCES projects(guid),

    -- Lifecycle Information
    phase_name           VARCHAR(100) NOT NULL,  -- e.g., "Planning", "Requirements", "Design", "Implementation"
    phase_order          INTEGER NOT NULL,
    phase_status         VARCHAR(50),  -- not_started, in_progress, completed
    start_date           DATE,
    end_date             DATE,

    -- Audit Trail
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP NULL,
    version              INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_lifecycles_project ON lifecycles(project_guid);
CREATE INDEX idx_lifecycles_phase_order ON lifecycles(project_guid, phase_order);
```

---

### GROUP 2: REQUIREMENTS TABLES

#### 3.4 Table: `requirements`

Stores all project requirements.

**Traces to:** REQ-DB-002

```sql
CREATE TABLE requirements (
    -- Hybrid Identifier
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,  -- e.g., "REQ-SYS-001", "REQ-SW-042"

    -- Relationships
    project_guid         UUID NOT NULL REFERENCES projects(guid),
    parent_guid          UUID REFERENCES requirements(guid),  -- For hierarchical requirements

    -- Requirement Content
    requirement_text     TEXT NOT NULL,
    requirement_type     VARCHAR(50),  -- functional, performance, interface, safety, security, etc.
    category             VARCHAR(100),
    priority             VARCHAR(20) CHECK (priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    rationale            TEXT,

    -- Verification
    verification_method  VARCHAR(100),  -- test, analysis, inspection, demonstration
    verification_status  VARCHAR(50) DEFAULT 'not_verified',  -- not_verified, in_progress, verified, failed

    -- Review Status
    review_status        VARCHAR(50) DEFAULT 'draft',  -- draft, under_review, approved, rejected
    reviewed_by_guid     UUID REFERENCES users(guid),
    review_date          TIMESTAMP,
    review_comments      TEXT,

    -- Source Tracking
    source               VARCHAR(100),  -- 'user_input', 'AI_extracted', 'imported', 'derived'
    source_document      VARCHAR(255),

    -- Audit Trail
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP NULL,
    version              INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_requirements_project ON requirements(project_guid);
CREATE INDEX idx_requirements_parent ON requirements(parent_guid);
CREATE INDEX idx_requirements_type ON requirements(requirement_type);
CREATE INDEX idx_requirements_status ON requirements(review_status);
CREATE INDEX idx_requirements_verification ON requirements(verification_status);
CREATE INDEX idx_requirements_display_id ON requirements(display_id);
```

#### 3.5 Table: `traceability_links`

Stores traceability relationships between entities.

**Traces to:** REQ-DB-003

```sql
CREATE TABLE traceability_links (
    -- Hybrid Identifier
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,

    -- Relationships (polymorphic - can link any entity type)
    source_guid          UUID NOT NULL,
    source_type          VARCHAR(50) NOT NULL,  -- 'requirement', 'design_element', 'test_case', 'configuration_item'
    target_guid          UUID NOT NULL,
    target_type          VARCHAR(50) NOT NULL,

    -- Link Information
    link_type            VARCHAR(50) NOT NULL,  -- 'derives_from', 'verifies', 'implements', 'allocated_to'
    rationale            TEXT,

    -- Audit Trail
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP NULL,
    version              INTEGER NOT NULL DEFAULT 1,

    UNIQUE(source_guid, target_guid, link_type)
);

CREATE INDEX idx_traceability_source ON traceability_links(source_guid, source_type);
CREATE INDEX idx_traceability_target ON traceability_links(target_guid, target_type);
CREATE INDEX idx_traceability_link_type ON traceability_links(link_type);
```

#### 3.6 Table: `requirement_changes`

Tracks changes to requirements over time.

```sql
CREATE TABLE requirement_changes (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_guid     UUID NOT NULL REFERENCES requirements(guid),
    change_type          VARCHAR(50) NOT NULL,  -- 'created', 'modified', 'approved', 'rejected', 'deleted'
    field_changed        VARCHAR(100),
    old_value            TEXT,
    new_value            TEXT,
    change_rationale     TEXT,
    changed_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    changed_by_guid      UUID REFERENCES users(guid)
);

CREATE INDEX idx_requirement_changes_requirement ON requirement_changes(requirement_guid);
CREATE INDEX idx_requirement_changes_date ON requirement_changes(changed_at);
```

---

### GROUP 3: DESIGN TABLES

#### 3.7 Table: `design_elements`

Stores design information.

```sql
CREATE TABLE design_elements (
    -- Hybrid Identifier
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,  -- e.g., "DES-SW-001"

    -- Relationships
    project_guid         UUID NOT NULL REFERENCES projects(guid),
    parent_guid          UUID REFERENCES design_elements(guid),

    -- Design Content
    element_name         VARCHAR(255) NOT NULL,
    element_type         VARCHAR(50),  -- 'architecture', 'component', 'interface', 'algorithm'
    description          TEXT,
    design_level         VARCHAR(50),  -- 'high_level', 'low_level'

    -- Review Status
    review_status        VARCHAR(50) DEFAULT 'draft',
    reviewed_by_guid     UUID REFERENCES users(guid),
    review_date          TIMESTAMP,
    review_comments      TEXT,

    -- Audit Trail
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP NULL,
    version              INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_design_elements_project ON design_elements(project_guid);
CREATE INDEX idx_design_elements_parent ON design_elements(parent_guid);
CREATE INDEX idx_design_elements_type ON design_elements(element_type);
```

---

### GROUP 4: CONFIGURATION ITEM MANAGEMENT TABLES

**Traces to:** REQ-DB-037 through REQ-DB-051

#### 3.8 Table: `configuration_items` (Core CI Table)

Stores all Configuration Items with 34+ fields.

**Traces to:** REQ-DB-037, REQ-DB-038

```sql
CREATE TABLE configuration_items (
    -- Hybrid Identifier (REQ-DB-052)
    guid                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id                VARCHAR(50) NOT NULL UNIQUE,  -- e.g., "CI-SW-001", "CI-HW-042"

    -- Relationships
    project_guid              UUID NOT NULL REFERENCES projects(guid),
    parent_guid               UUID REFERENCES configuration_items(guid),  -- Hierarchical structure

    -- Core Identification (Fields 1-5 from CI spec)
    ci_identifier             VARCHAR(100) NOT NULL,  -- Structured alphanumeric code
    ci_name                   VARCHAR(255) NOT NULL,
    ci_type                   VARCHAR(50) NOT NULL,  -- Software, Hardware, Document, Data, Firmware, Subsystem
    description               TEXT,
    item_category             VARCHAR(100),  -- COTS, custom-developed, supplier-provided, open-source

    -- Configuration Management (Fields 6-10)
    control_level             INTEGER CHECK (control_level BETWEEN 1 AND 5),  -- 1=highest, 5=uncontrolled
    baseline_status           VARCHAR(50),  -- draft, under_review, released, obsolete
    baseline_version          VARCHAR(50),
    baseline_date             DATE,
    change_history_summary    TEXT,

    -- Traceability (Fields 11-13)
    derives_from_requirements TEXT[],  -- Array of requirement display_ids
    parent_ci                 VARCHAR(100),  -- Parent CI identifier (for hierarchical view)
    child_cis                 TEXT[],  -- Array of child CI identifiers

    -- Development & Quality (Fields 14-17)
    development_status        VARCHAR(50),  -- concept, design, development, verification, production, obsolete
    quality_status            VARCHAR(50),  -- not_reviewed, under_review, approved, rejected
    dal_sil_level            VARCHAR(20),   -- Inherited from project or CI-specific
    criticality               VARCHAR(50),  -- safety-critical, mission-critical, non-critical

    -- Change Management (Fields 18-20)
    change_requests           JSONB,  -- Array of change request references
    deviations                JSONB,  -- Approved deviations from requirements
    waivers                   JSONB,  -- Approved waivers

    -- Lifecycle & Ownership (Fields 21-24)
    lifecycle_phase           VARCHAR(100),
    responsible_engineer_guid UUID REFERENCES users(guid),
    responsible_team_guid     UUID REFERENCES teams(guid),
    supplier_guid             UUID REFERENCES suppliers(guid),

    -- Manufacturing & Production (Fields 25-28)
    part_number               VARCHAR(100),
    serial_number             VARCHAR(100),
    manufacturing_date        DATE,
    lot_batch_number          VARCHAR(100),

    -- Documentation (Fields 29-30)
    associated_documents      TEXT[],  -- Array of document references
    drawings_schematics       TEXT[],

    -- Verification & Certification (Fields 31-32)
    verification_status       VARCHAR(50),  -- not_verified, in_progress, verified, failed
    certification_status      VARCHAR(50),  -- not_certified, in_progress, certified, expired

    -- Safety & Security (Fields 33-34)
    safety_classification     VARCHAR(50),
    security_classification   VARCHAR(50),

    -- Data Rights & Export Control (Fields 35-36)
    data_rights               VARCHAR(100),  -- proprietary, government, open-source, limited-rights
    export_control            VARCHAR(100),  -- ITAR, EAR, none

    -- Audit Trail
    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid           UUID REFERENCES users(guid),
    updated_by_guid           UUID REFERENCES users(guid),
    deleted_at                TIMESTAMP NULL,
    version                   INTEGER NOT NULL DEFAULT 1  -- For optimistic locking
);

CREATE INDEX idx_ci_project ON configuration_items(project_guid);
CREATE INDEX idx_ci_parent ON configuration_items(parent_guid);
CREATE INDEX idx_ci_type ON configuration_items(ci_type);
CREATE INDEX idx_ci_display_id ON configuration_items(display_id);
CREATE INDEX idx_ci_control_level ON configuration_items(control_level);
CREATE INDEX idx_ci_baseline_status ON configuration_items(baseline_status);
CREATE INDEX idx_ci_development_status ON configuration_items(development_status);
CREATE INDEX idx_ci_part_number ON configuration_items(part_number);
CREATE INDEX idx_ci_responsible_engineer ON configuration_items(responsible_engineer_guid);
CREATE INDEX idx_ci_responsible_team ON configuration_items(responsible_team_guid);
CREATE INDEX idx_ci_supplier ON configuration_items(supplier_guid);
```

#### 3.9 Table: `bill_of_materials` (BOM)

Stores BOM relationships between CIs.

**Traces to:** REQ-DB-039

```sql
CREATE TABLE bill_of_materials (
    -- Hybrid Identifier
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,

    -- Relationships
    project_guid         UUID NOT NULL REFERENCES projects(guid),
    parent_ci_guid       UUID NOT NULL REFERENCES configuration_items(guid),
    child_ci_guid        UUID NOT NULL REFERENCES configuration_items(guid),

    -- BOM Details
    bom_type             VARCHAR(50) NOT NULL,  -- engineering, manufacturing, service, as_built
    quantity             INTEGER NOT NULL DEFAULT 1,
    position_reference   VARCHAR(100),  -- Where item is installed
    find_number          VARCHAR(50),   -- Drawing find/item number
    notes                TEXT,

    -- Audit Trail
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP NULL,
    version              INTEGER NOT NULL DEFAULT 1,

    UNIQUE(parent_ci_guid, child_ci_guid, bom_type)
);

CREATE INDEX idx_bom_project ON bill_of_materials(project_guid);
CREATE INDEX idx_bom_parent ON bill_of_materials(parent_ci_guid);
CREATE INDEX idx_bom_child ON bill_of_materials(child_ci_guid);
CREATE INDEX idx_bom_type ON bill_of_materials(bom_type);
```

#### 3.10 Table: `suppliers`

Stores supplier information.

**Traces to:** REQ-DB-040

```sql
CREATE TABLE suppliers (
    -- Hybrid Identifier
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,

    -- Supplier Information
    supplier_name        VARCHAR(255) NOT NULL,
    supplier_code        VARCHAR(50) UNIQUE,
    contact_person       VARCHAR(255),
    email                VARCHAR(255),
    phone                VARCHAR(50),
    address              TEXT,

    -- Qualification
    supplier_status      VARCHAR(50),  -- approved, conditional, not_approved, suspended
    qualification_date   DATE,
    qualification_expiry DATE,
    notes                TEXT,

    -- Audit Trail
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP NULL,
    version              INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_suppliers_code ON suppliers(supplier_code);
CREATE INDEX idx_suppliers_status ON suppliers(supplier_status);
```

#### 3.11 Table: `ci_baselines`

Tracks baseline history for CIs.

**Traces to:** REQ-DB-041

```sql
CREATE TABLE ci_baselines (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ci_guid              UUID NOT NULL REFERENCES configuration_items(guid),
    baseline_name        VARCHAR(100) NOT NULL,  -- e.g., "PDR Baseline", "CDR Baseline", "Production Release 1.0"
    baseline_date        DATE NOT NULL,
    baseline_status      VARCHAR(50),  -- proposed, approved, released
    approved_by_guid     UUID REFERENCES users(guid),
    approval_date        DATE,
    notes                TEXT,
    snapshot             JSONB,  -- Full CI state at baseline (JSON snapshot)
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ci_baselines_ci ON ci_baselines(ci_guid);
CREATE INDEX idx_ci_baselines_date ON ci_baselines(baseline_date);
```

---

### GROUP 5: COLLABORATION TABLES

**Traces to:** REQ-DB-053 through REQ-DB-056

#### 3.12 Table: `user_sessions`

Tracks active user sessions.

**Traces to:** REQ-DB-053

```sql
CREATE TABLE user_sessions (
    -- Hybrid Identifier
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,

    -- Relationships
    user_guid            UUID NOT NULL REFERENCES users(guid),
    project_guid         UUID REFERENCES projects(guid),

    -- Session Information
    session_token        VARCHAR(255) NOT NULL UNIQUE,  -- JWT token or session ID
    ip_address           INET,
    user_agent           TEXT,
    login_time           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    logout_time          TIMESTAMP,
    session_status       VARCHAR(50) DEFAULT 'active',  -- active, expired, logged_out

    -- Session Context (what user is working on)
    current_ci_guid      UUID REFERENCES configuration_items(guid),
    current_conversation_guid UUID REFERENCES ai_conversations(guid),

    -- Audit
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_user ON user_sessions(user_guid);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_status ON user_sessions(session_status);
CREATE INDEX idx_sessions_last_activity ON user_sessions(last_activity);
```

#### 3.13 Table: `ci_locks` (Pessimistic Locking)

Manages check-out/check-in locks on CIs.

**Traces to:** REQ-DB-054, REQ-BE-016

```sql
CREATE TABLE ci_locks (
    -- Hybrid Identifier
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,

    -- Relationships
    ci_guid              UUID NOT NULL UNIQUE REFERENCES configuration_items(guid),  -- UNIQUE: One lock per CI
    locked_by_guid       UUID NOT NULL REFERENCES users(guid),
    session_guid         UUID REFERENCES user_sessions(guid),

    -- Lock Information
    lock_type            VARCHAR(50) NOT NULL DEFAULT 'exclusive',  -- exclusive (for check-out)
    lock_reason          TEXT,
    estimated_duration   INTERVAL,  -- How long user expects to hold lock

    -- Lock Timestamps
    locked_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lock_expires_at      TIMESTAMP,  -- Auto-release if expired

    -- Audit
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_locks_ci ON ci_locks(ci_guid);
CREATE INDEX idx_locks_user ON ci_locks(locked_by_guid);
CREATE INDEX idx_locks_expires ON ci_locks(lock_expires_at);
```

#### 3.14 Table: `work_assignments`

Assigns CIs to users/teams for work partitioning.

**Traces to:** REQ-DB-055, REQ-BE-018

```sql
CREATE TABLE work_assignments (
    -- Hybrid Identifier
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,

    -- Relationships
    project_guid         UUID NOT NULL REFERENCES projects(guid),
    ci_guid              UUID REFERENCES configuration_items(guid),  -- Can be NULL for task-level assignments
    assigned_to_user_guid UUID REFERENCES users(guid),
    assigned_to_team_guid UUID REFERENCES teams(guid),
    assigned_by_guid     UUID REFERENCES users(guid),

    -- Assignment Details
    assignment_type      VARCHAR(50),  -- 'development', 'review', 'verification', 'documentation'
    priority             VARCHAR(20) CHECK (priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    due_date             DATE,
    assignment_status    VARCHAR(50) DEFAULT 'assigned',  -- assigned, in_progress, completed, cancelled
    completion_date      DATE,
    notes                TEXT,

    -- Audit Trail
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP NULL,
    version              INTEGER NOT NULL DEFAULT 1,

    CHECK (assigned_to_user_guid IS NOT NULL OR assigned_to_team_guid IS NOT NULL)
);

CREATE INDEX idx_assignments_project ON work_assignments(project_guid);
CREATE INDEX idx_assignments_ci ON work_assignments(ci_guid);
CREATE INDEX idx_assignments_user ON work_assignments(assigned_to_user_guid);
CREATE INDEX idx_assignments_team ON work_assignments(assigned_to_team_guid);
CREATE INDEX idx_assignments_status ON work_assignments(assignment_status);
```

---

### GROUP 6: RBAC (Role-Based Access Control) TABLES

**Traces to:** REQ-DB-057 through REQ-DB-061

#### 3.15 Table: `users`

Stores user accounts.

**Traces to:** REQ-DB-057

```sql
CREATE TABLE users (
    -- Hybrid Identifier
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,  -- e.g., "USER-001"

    -- User Identification
    username             VARCHAR(100) NOT NULL UNIQUE,
    email                VARCHAR(255) NOT NULL UNIQUE,
    full_name            VARCHAR(255) NOT NULL,
    password_hash        VARCHAR(255) NOT NULL,  -- bcrypt/argon2 hash

    -- User Status
    user_status          VARCHAR(50) DEFAULT 'active',  -- active, suspended, inactive, locked
    last_login           TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked_until TIMESTAMP,

    -- User Preferences
    preferences          JSONB,  -- UI preferences, notification settings, etc.

    -- Audit Trail
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP NULL,
    version              INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(user_status);
```

#### 3.16 Table: `roles`

Defines user roles (7 role types).

**Traces to:** REQ-DB-057, REQ-BE-024

```sql
CREATE TABLE roles (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    role_name            VARCHAR(50) NOT NULL UNIQUE,  -- Administrator, Manager, Senior_Engineer, Engineer, Reviewer, Viewer, External
    role_description     TEXT,
    permissions          JSONB NOT NULL,  -- Array of permission strings
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_roles_name ON roles(role_name);
```

#### 3.17 Table: `user_roles`

Assigns roles to users (many-to-many).

```sql
CREATE TABLE user_roles (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_guid            UUID NOT NULL REFERENCES users(guid),
    role_guid            UUID NOT NULL REFERENCES roles(guid),
    project_guid         UUID REFERENCES projects(guid),  -- Role can be project-specific
    assigned_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assigned_by_guid     UUID REFERENCES users(guid),

    UNIQUE(user_guid, role_guid, project_guid)
);

CREATE INDEX idx_user_roles_user ON user_roles(user_guid);
CREATE INDEX idx_user_roles_role ON user_roles(role_guid);
CREATE INDEX idx_user_roles_project ON user_roles(project_guid);
```

#### 3.18 Table: `teams`

Defines teams (groups of users).

**Traces to:** REQ-DB-058

```sql
CREATE TABLE teams (
    -- Hybrid Identifier
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,

    -- Team Information
    team_name            VARCHAR(100) NOT NULL,
    team_description     TEXT,
    project_guid         UUID REFERENCES projects(guid),
    team_lead_guid       UUID REFERENCES users(guid),

    -- Audit Trail
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP NULL,
    version              INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_teams_project ON teams(project_guid);
CREATE INDEX idx_teams_lead ON teams(team_lead_guid);
```

#### 3.19 Table: `team_members`

Assigns users to teams (many-to-many).

```sql
CREATE TABLE team_members (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_guid            UUID NOT NULL REFERENCES teams(guid),
    user_guid            UUID NOT NULL REFERENCES users(guid),
    joined_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    added_by_guid        UUID REFERENCES users(guid),

    UNIQUE(team_guid, user_guid)
);

CREATE INDEX idx_team_members_team ON team_members(team_guid);
CREATE INDEX idx_team_members_user ON team_members(user_guid);
```

#### 3.20 Table: `team_permissions`

Assigns permissions to teams.

**Traces to:** REQ-DB-058

```sql
CREATE TABLE team_permissions (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_guid            UUID NOT NULL REFERENCES teams(guid),
    permission_type      VARCHAR(100) NOT NULL,  -- 'read_all_cis', 'edit_assigned_cis', 'approve_reviews', etc.
    resource_type        VARCHAR(50),  -- What this permission applies to
    granted_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    granted_by_guid      UUID REFERENCES users(guid)
);

CREATE INDEX idx_team_permissions_team ON team_permissions(team_guid);
```

#### 3.21 Table: `ci_access_control_list` (CI-Level ACL)

Granular access control per CI.

**Traces to:** REQ-DB-059

```sql
CREATE TABLE ci_access_control_list (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ci_guid              UUID NOT NULL REFERENCES configuration_items(guid),
    user_guid            UUID REFERENCES users(guid),
    team_guid            UUID REFERENCES teams(guid),
    permission_level     VARCHAR(50) NOT NULL,  -- 'read', 'write', 'approve', 'admin'
    granted_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    granted_by_guid      UUID REFERENCES users(guid),
    expires_at           TIMESTAMP,  -- Optional expiration

    CHECK (user_guid IS NOT NULL OR team_guid IS NOT NULL)
);

CREATE INDEX idx_ci_acl_ci ON ci_access_control_list(ci_guid);
CREATE INDEX idx_ci_acl_user ON ci_access_control_list(user_guid);
CREATE INDEX idx_ci_acl_team ON ci_access_control_list(team_guid);
```

---

### GROUP 7: MERGE MANAGEMENT TABLES

**Traces to:** REQ-DB-062 through REQ-DB-067

#### 3.22 Table: `source_instances`

Tracks different AISET instances (for distributed development).

**Traces to:** REQ-DB-062

```sql
CREATE TABLE source_instances (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    instance_name        VARCHAR(100) NOT NULL UNIQUE,  -- e.g., "SUPPLIER_A", "SITE_TOULOUSE", "PRIME_CONTRACTOR"
    instance_description TEXT,
    organization         VARCHAR(255),
    contact_email        VARCHAR(255),
    instance_url         VARCHAR(500),
    instance_guid        UUID UNIQUE,  -- GUID of this instance in its own database
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_source_instances_name ON source_instances(instance_name);
```

#### 3.23 Table: `id_mappings`

Maps external IDs to internal GUIDs after merge.

**Traces to:** REQ-DB-063

```sql
CREATE TABLE id_mappings (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_instance_guid UUID NOT NULL REFERENCES source_instances(guid),
    entity_type          VARCHAR(50) NOT NULL,  -- 'configuration_item', 'requirement', 'design_element', etc.
    source_guid          UUID NOT NULL,  -- GUID in source instance
    source_display_id    VARCHAR(100),   -- Display ID in source instance
    target_guid          UUID NOT NULL,  -- GUID in this instance (after merge)
    target_display_id    VARCHAR(100),   -- Display ID in this instance (may have instance prefix)
    mapped_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mapped_by_guid       UUID REFERENCES users(guid),

    UNIQUE(source_instance_guid, entity_type, source_guid)
);

CREATE INDEX idx_id_mappings_source ON id_mappings(source_instance_guid, entity_type, source_guid);
CREATE INDEX idx_id_mappings_target ON id_mappings(target_guid);
```

#### 3.24 Table: `merge_sessions`

Tracks merge operations between instances.

**Traces to:** REQ-DB-064

```sql
CREATE TABLE merge_sessions (
    -- Hybrid Identifier
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,

    -- Merge Information
    source_instance_guid UUID NOT NULL REFERENCES source_instances(guid),
    import_file_path     VARCHAR(500),
    import_file_hash     VARCHAR(64),  -- SHA-256 hash for integrity

    -- Merge Status
    merge_status         VARCHAR(50) DEFAULT 'in_progress',  -- in_progress, completed, failed, rolled_back
    started_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at         TIMESTAMP,
    initiated_by_guid    UUID REFERENCES users(guid),

    -- Merge Statistics
    entities_imported    INTEGER DEFAULT 0,
    conflicts_detected   INTEGER DEFAULT 0,
    conflicts_resolved   INTEGER DEFAULT 0,
    auto_merged          INTEGER DEFAULT 0,
    manually_merged      INTEGER DEFAULT 0,

    -- Merge Notes
    notes                TEXT,
    error_log            TEXT,

    -- Audit
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_merge_sessions_source ON merge_sessions(source_instance_guid);
CREATE INDEX idx_merge_sessions_status ON merge_sessions(merge_status);
CREATE INDEX idx_merge_sessions_date ON merge_sessions(started_at);
```

#### 3.25 Table: `merge_conflicts`

Stores detected conflicts during merge.

**Traces to:** REQ-DB-065, REQ-AI-041

```sql
CREATE TABLE merge_conflicts (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merge_session_guid   UUID NOT NULL REFERENCES merge_sessions(guid),

    -- Conflict Information
    conflict_type        VARCHAR(50) NOT NULL,  -- 'id_collision', 'duplicate_item', 'field_conflict', 'broken_reference', 'circular_dependency'
    entity_type          VARCHAR(50) NOT NULL,  -- 'configuration_item', 'requirement', etc.
    source_guid          UUID,  -- GUID from import file
    target_guid          UUID,  -- Existing GUID in this database

    -- Conflict Details
    field_name           VARCHAR(100),
    source_value         TEXT,
    target_value         TEXT,
    conflict_description TEXT,

    -- Resolution
    resolution_status    VARCHAR(50) DEFAULT 'unresolved',  -- unresolved, ai_suggested, manually_resolved, auto_resolved
    resolution_strategy  VARCHAR(50),  -- 'accept_source', 'accept_target', 'manual_merge', 'create_new'
    ai_suggestion        TEXT,  -- AI-generated suggestion
    ai_confidence        NUMERIC(3,2),  -- 0.00 to 1.00
    ai_rationale         TEXT,
    resolved_value       TEXT,
    resolved_at          TIMESTAMP,
    resolved_by_guid     UUID REFERENCES users(guid),

    -- Audit
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conflicts_session ON merge_conflicts(merge_session_guid);
CREATE INDEX idx_conflicts_type ON merge_conflicts(conflict_type);
CREATE INDEX idx_conflicts_status ON merge_conflicts(resolution_status);
```

#### 3.26 Table: `duplicate_candidates`

Stores potential duplicate CIs detected across instances.

**Traces to:** REQ-DB-070, REQ-AI-042

```sql
CREATE TABLE duplicate_candidates (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ci_guid_1            UUID NOT NULL REFERENCES configuration_items(guid),
    ci_guid_2            UUID NOT NULL REFERENCES configuration_items(guid),

    -- Similarity Analysis
    similarity_score     NUMERIC(3,2),  -- 0.00 to 1.00
    similarity_factors   JSONB,  -- Which fields match (name, part_number, description, etc.)
    ai_analysis          TEXT,  -- AI analysis of similarity
    ai_recommendation    VARCHAR(50),  -- 'merge', 'keep_separate', 'needs_review'
    ai_confidence        NUMERIC(3,2),

    -- Resolution
    duplicate_status     VARCHAR(50) DEFAULT 'pending_review',  -- pending_review, confirmed_duplicate, not_duplicate, merged
    reviewed_by_guid     UUID REFERENCES users(guid),
    reviewed_at          TIMESTAMP,
    resolution_notes     TEXT,

    -- Audit
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (ci_guid_1 < ci_guid_2),  -- Prevent duplicate pairs (A,B) and (B,A)
    UNIQUE(ci_guid_1, ci_guid_2)
);

CREATE INDEX idx_duplicates_ci1 ON duplicate_candidates(ci_guid_1);
CREATE INDEX idx_duplicates_ci2 ON duplicate_candidates(ci_guid_2);
CREATE INDEX idx_duplicates_status ON duplicate_candidates(duplicate_status);
CREATE INDEX idx_duplicates_score ON duplicate_candidates(similarity_score);
```

---

### GROUP 8: AI CONVERSATION TABLES

**Traces to:** REQ-DB-004 through REQ-DB-008

#### 3.27 Table: `ai_conversations`

Stores AI conversation sessions.

**Traces to:** REQ-DB-004

```sql
CREATE TABLE ai_conversations (
    -- Hybrid Identifier
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,

    -- Relationships
    project_guid         UUID NOT NULL REFERENCES projects(guid),
    user_guid            UUID NOT NULL REFERENCES users(guid),

    -- Conversation Information
    conversation_title   VARCHAR(255),
    conversation_purpose TEXT,
    conversation_status  VARCHAR(50) DEFAULT 'active',  -- active, paused, completed, archived

    -- AI Configuration
    ai_service           VARCHAR(50) DEFAULT 'claude',  -- claude, lm_studio, mistral
    ai_model             VARCHAR(100),  -- e.g., 'claude-sonnet-4-5', 'mistral-7b'

    -- Conversation Context
    context              JSONB,  -- Current context (requirements list, open questions, etc.)

    -- Audit Trail
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP NULL,
    version              INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_conversations_project ON ai_conversations(project_guid);
CREATE INDEX idx_conversations_user ON ai_conversations(user_guid);
CREATE INDEX idx_conversations_status ON ai_conversations(conversation_status);
```

#### 3.28 Table: `ai_messages`

Stores individual messages in conversations.

**Traces to:** REQ-DB-005

```sql
CREATE TABLE ai_messages (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_guid    UUID NOT NULL REFERENCES ai_conversations(guid),
    message_role         VARCHAR(50) NOT NULL,  -- 'user', 'assistant', 'system'
    message_content      TEXT NOT NULL,
    message_metadata     JSONB,  -- Attachments, extracted data, etc.
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation ON ai_messages(conversation_guid);
CREATE INDEX idx_messages_created ON ai_messages(created_at);
```

---

### GROUP 9: AUDIT & COMPLIANCE TABLES

**Traces to:** REQ-DB-064, REQ-DB-068

#### 3.29 Table: `activity_log`

Logs all user activities.

**Traces to:** REQ-DB-068

```sql
CREATE TABLE activity_log (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_guid            UUID REFERENCES users(guid),
    session_guid         UUID REFERENCES user_sessions(guid),
    project_guid         UUID REFERENCES projects(guid),

    -- Activity Information
    activity_type        VARCHAR(100) NOT NULL,  -- 'login', 'logout', 'create_ci', 'edit_ci', 'check_out', 'check_in', 'merge', etc.
    entity_type          VARCHAR(50),  -- Type of entity affected
    entity_guid          UUID,  -- GUID of affected entity
    entity_display_id    VARCHAR(100),

    -- Activity Details
    activity_description TEXT,
    activity_result      VARCHAR(50),  -- 'success', 'failed', 'unauthorized'
    ip_address           INET,
    user_agent           TEXT,

    -- Audit
    occurred_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_user ON activity_log(user_guid);
CREATE INDEX idx_activity_session ON activity_log(session_guid);
CREATE INDEX idx_activity_project ON activity_log(project_guid);
CREATE INDEX idx_activity_type ON activity_log(activity_type);
CREATE INDEX idx_activity_entity ON activity_log(entity_type, entity_guid);
CREATE INDEX idx_activity_time ON activity_log(occurred_at);
```

#### 3.30 Table: `audit_trail`

Comprehensive audit trail for all data modifications (more detailed than activity_log).

**Traces to:** REQ-DB-064

```sql
CREATE TABLE audit_trail (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- What changed
    table_name           VARCHAR(100) NOT NULL,
    record_guid          UUID NOT NULL,
    record_display_id    VARCHAR(100),
    operation            VARCHAR(20) NOT NULL,  -- 'INSERT', 'UPDATE', 'DELETE'

    -- Change Details
    changed_fields       JSONB,  -- {"field_name": {"old": "...", "new": "..."}, ...}
    full_record_before   JSONB,  -- Complete record state before change
    full_record_after    JSONB,  -- Complete record state after change

    -- Who, When, Why
    changed_by_guid      UUID REFERENCES users(guid),
    changed_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    change_reason        TEXT,  -- Optional rationale for change
    session_guid         UUID REFERENCES user_sessions(guid),

    -- Source Tracking
    change_source        VARCHAR(50),  -- 'user_manual', 'ai_generated', 'import', 'system'
    source_instance_guid UUID REFERENCES source_instances(guid)  -- If from merge
);

CREATE INDEX idx_audit_table ON audit_trail(table_name);
CREATE INDEX idx_audit_record ON audit_trail(table_name, record_guid);
CREATE INDEX idx_audit_user ON audit_trail(changed_by_guid);
CREATE INDEX idx_audit_time ON audit_trail(changed_at);
CREATE INDEX idx_audit_operation ON audit_trail(operation);
```

---

### GROUP 10: NOTIFICATIONS & COMMENTS

**Traces to:** REQ-DB-060, REQ-DB-061

#### 3.31 Table: `notifications`

Stores user notifications.

**Traces to:** REQ-DB-060

```sql
CREATE TABLE notifications (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_guid            UUID NOT NULL REFERENCES users(guid),
    notification_type    VARCHAR(50) NOT NULL,  -- 'lock_expiring', 'review_required', 'assignment', 'mention', 'merge_conflict'
    notification_title   VARCHAR(255) NOT NULL,
    notification_body    TEXT,
    related_entity_type  VARCHAR(50),
    related_entity_guid  UUID,
    notification_status  VARCHAR(50) DEFAULT 'unread',  -- unread, read, dismissed
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    read_at              TIMESTAMP,
    dismissed_at         TIMESTAMP
);

CREATE INDEX idx_notifications_user ON notifications(user_guid);
CREATE INDEX idx_notifications_status ON notifications(notification_status);
CREATE INDEX idx_notifications_type ON notifications(notification_type);
CREATE INDEX idx_notifications_created ON notifications(created_at);
```

#### 3.32 Table: `comments`

Stores comments on entities (CIs, requirements, etc.).

**Traces to:** REQ-DB-061

```sql
CREATE TABLE comments (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type          VARCHAR(50) NOT NULL,  -- 'configuration_item', 'requirement', 'design_element', etc.
    entity_guid          UUID NOT NULL,
    parent_comment_guid  UUID REFERENCES comments(guid),  -- For threaded comments
    author_guid          UUID NOT NULL REFERENCES users(guid),
    comment_text         TEXT NOT NULL,
    comment_type         VARCHAR(50),  -- 'general', 'question', 'issue', 'approval', 'rejection'
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at           TIMESTAMP NULL
);

CREATE INDEX idx_comments_entity ON comments(entity_type, entity_guid);
CREATE INDEX idx_comments_author ON comments(author_guid);
CREATE INDEX idx_comments_parent ON comments(parent_comment_guid);
CREATE INDEX idx_comments_created ON comments(created_at);
```

---

### GROUP 11: ADDITIONAL TABLES (from existing schema)

#### 3.33 Table: `documents`

Stores document metadata.

**Traces to:** REQ-DB-006

```sql
CREATE TABLE documents (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    project_guid         UUID NOT NULL REFERENCES projects(guid),
    document_type        VARCHAR(100),
    document_title       VARCHAR(255) NOT NULL,
    file_path            VARCHAR(500),
    review_status        VARCHAR(50) DEFAULT 'draft',
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP NULL,
    version              INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_documents_project ON documents(project_guid);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_status ON documents(review_status);
```

#### 3.34 Table: `document_associations`

Links documents to entities.

**Traces to:** REQ-DB-007

```sql
CREATE TABLE document_associations (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_guid        UUID NOT NULL REFERENCES documents(guid),
    entity_type          VARCHAR(50) NOT NULL,
    entity_guid          UUID NOT NULL,
    association_type     VARCHAR(100),
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid)
);

CREATE INDEX idx_doc_assoc_document ON document_associations(document_guid);
CREATE INDEX idx_doc_assoc_entity ON document_associations(entity_type, entity_guid);
```

---

## 4. Database Triggers and Procedures

### 4.1 Automatic Timestamp Updates

**Trigger: update_updated_at**

Updates `updated_at` timestamp on every UPDATE.

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at column
-- Example for configuration_items:
CREATE TRIGGER update_configuration_items_updated_at
    BEFORE UPDATE ON configuration_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- (Repeat for all tables)
```

### 4.2 Lock Expiration Check

**Procedure: check_expired_locks**

Automatically releases expired locks.

```sql
CREATE OR REPLACE FUNCTION check_expired_locks()
RETURNS void AS $$
BEGIN
    DELETE FROM ci_locks
    WHERE lock_expires_at < CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Schedule as cron job or call periodically from backend
```

### 4.3 Soft Delete Filter Views

**Create views that automatically filter soft-deleted records:**

```sql
CREATE VIEW active_configuration_items AS
SELECT * FROM configuration_items
WHERE deleted_at IS NULL;

-- (Create for all tables with soft deletes)
```

---

## 5. Indexes and Performance Optimization

### 5.1 Index Strategy

**Primary Indexes (Already defined above):**
- Primary keys (GUID) - Clustered index on all tables
- Display IDs - Unique index on all tables
- Foreign keys - Index on all foreign key columns
- Soft delete - Partial index `WHERE deleted_at IS NULL`
- Status fields - Index on frequently queried status columns

**Full-Text Search Indexes:**

```sql
-- For searching CI names and descriptions
CREATE INDEX idx_ci_fulltext ON configuration_items
USING GIN(to_tsvector('english', ci_name || ' ' || COALESCE(description, '')));

-- For searching requirements
CREATE INDEX idx_req_fulltext ON requirements
USING GIN(to_tsvector('english', requirement_text));
```

**JSONB Indexes:**

```sql
-- For querying JSONB columns
CREATE INDEX idx_ci_change_requests ON configuration_items USING GIN(change_requests);
CREATE INDEX idx_users_preferences ON users USING GIN(preferences);
```

### 5.2 Query Optimization Guidelines

1. **Always filter soft-deleted records:** `WHERE deleted_at IS NULL`
2. **Use GUID for joins** (primary key), not display_id
3. **Use prepared statements** to prevent SQL injection
4. **Use connection pooling** (backend responsibility)
5. **Limit result sets** with LIMIT/OFFSET for pagination

---

## 6. Data Integrity Constraints

### 6.1 Referential Integrity

**All foreign keys enforce referential integrity:**
- `ON DELETE RESTRICT` (default) - Prevent deletion if referenced
- `ON UPDATE CASCADE` - Cascade updates to dependent rows

**Exception:** Soft deletes mean ON DELETE is rarely triggered.

### 6.2 Check Constraints

**Examples defined above:**
- `priority CHECK (priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'))`
- `control_level CHECK (control_level BETWEEN 1 AND 5)`
- `similarity_score CHECK (similarity_score BETWEEN 0.00 AND 1.00)`

### 6.3 Unique Constraints

**Examples:**
- `UNIQUE(username)` in `users`
- `UNIQUE(project_guid, standard_name)` in `project_standards`
- `UNIQUE(ci_guid)` in `ci_locks` (one lock per CI)

---

## 7. Traceability Matrix: Requirements → Database Tables

| Requirement ID | Requirement Summary | Database Tables |
|----------------|---------------------|-----------------|
| REQ-DB-001 | Store projects | `projects` |
| REQ-DB-002 | Store requirements | `requirements` |
| REQ-DB-003 | Store traceability | `traceability_links` |
| REQ-DB-004 | Store AI conversations | `ai_conversations` |
| REQ-DB-005 | Store AI messages | `ai_messages` |
| REQ-DB-006 | Store documents | `documents` |
| REQ-DB-007 | Link documents to entities | `document_associations` |
| REQ-DB-035 | Store project context | `projects` (project context fields) |
| REQ-DB-036 | Store standards mapping | `project_standards` |
| REQ-DB-037 | Store product structure | `configuration_items` (parent_guid) |
| REQ-DB-038 | Store item metadata | `configuration_items` (34+ fields) |
| REQ-DB-039 | Store BOM | `bill_of_materials` |
| REQ-DB-040 | Store supplier info | `suppliers` |
| REQ-DB-041 | CI baseline tracking | `ci_baselines` |
| REQ-DB-052 | Hybrid ID system | All tables (`guid` + `display_id`) |
| REQ-DB-053 | Session management | `user_sessions` |
| REQ-DB-054 | Lock management | `ci_locks` |
| REQ-DB-055 | Work assignment | `work_assignments` |
| REQ-DB-056 | Comments | `comments` |
| REQ-DB-057 | User & role management | `users`, `roles`, `user_roles` |
| REQ-DB-058 | Team permissions | `teams`, `team_members`, `team_permissions` |
| REQ-DB-059 | CI-level ACL | `ci_access_control_list` |
| REQ-DB-060 | Notifications | `notifications` |
| REQ-DB-061 | Comments | `comments` |
| REQ-DB-062 | Instance tracking | `source_instances` |
| REQ-DB-063 | ID mapping | `id_mappings` |
| REQ-DB-064 | Merge metadata | `merge_sessions`, `audit_trail` |
| REQ-DB-065 | Conflict storage | `merge_conflicts` |
| REQ-DB-066 | External references | `traceability_links`, `id_mappings` |
| REQ-DB-068 | Activity log | `activity_log` |
| REQ-DB-070 | Duplicate detection | `duplicate_candidates` |

**Complete traceability matrix:** See `08_TRACEABILITY/Requirements_to_Database_Traceability.md` (planned)

---

## 8. Database Deployment

### 8.1 Schema Initialization

**DDL Script:** `backend/database/schema.sql`

```sql
-- Create all tables in order (respecting foreign key dependencies)
-- 1. Users (no dependencies)
-- 2. Projects
-- 3. Source instances
-- 4. ...
-- (Full DDL script to be generated from this LLD)
```

### 8.2 Migration Strategy

**Tool:** Alembic (Python database migration tool)

**Migration Files:** `backend/database/migrations/`

```
migrations/
├── versions/
│   ├── 001_initial_schema.py
│   ├── 002_add_project_context.py
│   ├── 003_add_ci_management.py
│   ├── 004_add_collaboration_tables.py
│   └── ...
```

**Migration Process:**
1. Development: Generate migration from model changes
2. Review: Manual review of migration script
3. Test: Apply to test database
4. Production: Apply to production database with backup

### 8.3 Test Data

**Test Data Script:** `backend/database/test_data.sql`

**Existing Test Data:**
- Project: FURN-001 (ID: 3) - Furniture Building Project
- Conversation ID: 1
- Messages in `ai_messages`

---

## 9. Security Considerations

### 9.1 SQL Injection Prevention

**Mitigation:**
- Use parameterized queries (prepared statements) exclusively
- Never concatenate user input into SQL strings
- ORM (if used) must be configured to use parameterized queries

### 9.2 Access Control

**Database-Level:**
- Application database user has limited privileges (no DROP, ALTER on production)
- Read-only user for reporting/analytics
- Admin user for migrations only

**Application-Level:**
- RBAC enforced by backend before database queries
- ACL checked for CI-level operations
- Audit trail logs all access

### 9.3 Sensitive Data

**Password Storage:**
- Passwords hashed with bcrypt or argon2 (never plaintext)
- Hash stored in `users.password_hash`

**PII (Personally Identifiable Information):**
- Email addresses in `users` table
- Consider encryption-at-rest for compliance (GDPR, HIPAA)

---

## 10. Open Issues and Future Enhancements

### 10.1 Open Issues

1. **Database partitioning strategy** - For very large projects (>100k CIs)
2. **Replication configuration** - Master-slave or multi-master for HA
3. **Backup schedule** - Automated backup frequency and retention
4. **Performance benchmarking** - Validate query performance under load
5. **Encryption at rest** - Database-level encryption for sensitive data

### 10.2 Future Enhancements

1. **Time-travel queries** - Query historical state of database
2. **Change Data Capture (CDC)** - Real-time change streaming
3. **Advanced analytics tables** - Pre-aggregated data for dashboards
4. **Graph database integration** - For complex traceability graph queries

---

## 11. References

### 11.1 Internal Documents

- `03_DESIGN/HLD_High_Level_Design.md` - AISET High-Level Design
- `REQUIREMENTS.md` v0.8.0 - All database requirements (REQ-DB-001 through REQ-DB-070)
- `docs/Level_2_User_Framework/CONFIGURATION_ITEM_MANAGEMENT.md` - CI field specifications
- `docs/Level_1_AISET_Development/DATABASE_SCHEMA.md` - Existing reference (to be updated)

### 11.2 External Standards

- PostgreSQL 15 Documentation: https://www.postgresql.org/docs/15/
- SQL:2016 Standard
- DO-178C: Software Considerations in Airborne Systems and Equipment Certification

---

**END OF DATABASE LOW-LEVEL DESIGN DOCUMENT**

---

**Document Status:** Draft - Awaiting Review

**Next Steps:**
1. Review and approval by database architect
2. Generate DDL script from this LLD
3. Create Alembic migration files
4. Update DATABASE_SCHEMA.md reference document
5. Create traceability matrix (Requirements → Tables → Columns)
6. Implement and test schema in development environment
