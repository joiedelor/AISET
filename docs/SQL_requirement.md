requirement for the database.
I want to make a tool that will be maintained by an AI but checked by human. can you define the database structure for that. The following requirement shall be fulfilled:

The database shall store all requirement from a project including the one for the system for the software and for the hardware.
The database shall store all requirement from the project including the one for the physical part of the system (structure, aerodynamic, eme, etc…).

The database shall store all design data from the project by direct text or by reference for the data that cannot be store in text format (3d drawings, models, etc…).

The database shall enable to allocate the responsibility in accordance to S1000D.

The database shall enable to allocate the workpages in charge in accordance with MIL STD‐881

For system It shall enable to follow the strict design definition rules from ARP4754
For Software It shall enable to follow the strict design definition rules from DO178C
For Hardware It shall enable to follow the strict design definition rules from DO254


For system It shall enable to follow the strict requirement validation rules from ARP4754
For Software It shall enable to follow the strict requirement validation rules from DO178C
For Hardware It shall enable to follow the strict requirement validation rules from DO254

For system It shall follow enable to the strict requirement verification rules from ARP4754
For Software It shall follow enable to the strict requirement verification rules from DO178C
For Hardware It shall follow enable to the strict requirement verification rules from DO254


For system It shall follow enable to the strict configuration rules from ARP4754
For Software It shall follow enable to the strict configuration rules from DO178C
For Hardware It shall follow enable to the strict configuration rules from DO254
Process
AI Design Process Workflow (Full Table Usage)
1️⃣ Project & User Setup
1.	Create a PROJECT entry.
2.	Register all human and AI users in USER.
3.	Define WBS_NODE tree for the project.
4.	Assign roles using S1000D_RESP.
________________________________________
2️⃣ Requirement Management
1.	Add REQUIREMENT entries with level (system/software/hardware) and discipline.
2.	Classify each requirement via REQUIREMENT_TYPE.
3.	Allocate responsibilities:
o	ALLOCATION links requirement → WBS_NODE → S1000D_RESP.
4.	If requirements are derived from others, create REQUIREMENT_DERIVATION.
5.	Maintain traceability:
o	TRACELINK requirement → requirement or requirement → design item.
________________________________________
3️⃣ Artifact & Design Management
For each requirement:
1.	Create ARTIFACT (text document, 3D model, code, schema) linked to the project.
2.	Create DESIGN_ITEM referencing the artifact.
3.	For software:
o	Create SOFTWARE_ITEM, then SOFTWARE_DESIGN, then SOFTWARE_CODE.
4.	For hardware:
o	Create HARDWARE_ITEM, then HARDWARE_DESIGN, then HARDWARE_IMPLEMENTATION.
5.	Add metadata (DAL, design level, version, project, discipline).
________________________________________
4️⃣ Verification & Validation
1.	For each design item:
o	Create VERIFICATION (method, environment, linked baseline).
o	Create VALIDATION to link requirement → verification.
2.	Maintain TRACELINK between requirement → design → verification → validation.
3.	Record verification coverage using COVERAGE for software and verification items.
________________________________________
5️⃣ Baseline & Versioning
1.	Create BASELINE for design/versioned delivery.
2.	Store all versioned entities in ENTITY_VERSION.
3.	Link versioned entities to BASELINE_ITEM for traceability.
4.	Any design change triggers:
o	CHANGE_REQUEST
o	Human APPROVAL
o	Update BASELINE and BASELINE_ITEM.
________________________________________
6️⃣ Reviews & Lifecycle Deliverables
1.	Schedule REVIEW entries for key milestones.
2.	Add REVIEW_ITEM for each entity under review.
3.	Create LIFECYCLE_DELIVERABLE for deliverables like manuals, schematics, software packages.
4.	Track all actions in AUDIT_LOG.
________________________________________
7️⃣ AI Job Management
1.	All AI actions are queued in AI_JOB (create/update/design/verification).
2.	AI reads requirement metadata, rules, and allocations.
3.	Performs creation/proposal of artifacts, design items, SW/HW items.
4.	Updates TRACELINK, COVERAGE, ENTITY_VERSION, BASELINE_ITEM.
5.	Logs actions in AUDIT_LOG.
6.	Submits APPROVAL for human validation where required.
________________________________________
8️⃣ End-to-End Traceability
•	REQUIREMENT → DESIGN_ITEM → ARTIFACT → VERIFICATION → VALIDATION → COVERAGE
•	All entities versioned via ENTITY_VERSION and baselines (BASELINE + BASELINE_ITEM)
•	All human and AI actions logged in AUDIT_LOG
•	Changes tracked via CHANGE_REQUEST + APPROVAL


 
erDiagram

erDiagram
    USER ||--o{ REQUIREMENT : "creates"
    USER ||--o{ VERIFICATION : "owns"
    USER ||--o{ APPROVAL : "approves"
    USER ||--o{ AUDIT_LOG : "acts"
    USER ||--o{ REVIEW : "conducts"

    PROJECT ||--o{ REQUIREMENT : "has"
    PROJECT ||--o{ ARTIFACT : "has"
    PROJECT ||--o{ WBS_NODE : "has"
    PROJECT ||--o{ SOFTWARE_ITEM : "has"
    PROJECT ||--o{ HARDWARE_ITEM : "has"
    PROJECT ||--o{ BASELINE : "has"
    PROJECT ||--o{ CHANGE_REQUEST : "has"
    PROJECT ||--o{ REVIEW : "has"
    PROJECT ||--o{ LIFECYCLE_DELIVERABLE : "has"
    PROJECT ||--o{ VERIFICATION : "has"

    REQUIREMENT_TYPE ||--o{ REQUIREMENT : "classifies"

    REQUIREMENT ||--o{ ALLOCATION : "allocated to"
    REQUIREMENT ||--o{ TRACELINK : "source/target"
    REQUIREMENT ||--o{ VALIDATION : "validated by"
    REQUIREMENT ||--o{ REQUIREMENT_DERIVATION : "parent/child"

    ARTIFACT ||--o{ DESIGN_ITEM : "implements"
    ARTIFACT ||--o{ VERIFICATION : "used in"
    ARTIFACT ||--o{ TRACELINK : "trace link"

    WBS_NODE ||--o{ ALLOCATION : "workpage assignment"
    WBS_NODE ||--o{ WBS_NODE : "parent"

    S1000D_RESP ||--o{ ALLOCATION : "responsibility"

    DESIGN_ITEM ||--o{ TRACELINK : "traceability"

    VERIFICATION ||--o{ VALIDATION : "feeds"
    VERIFICATION ||--o{ TRACELINK : "verifies"
    VERIFICATION ||--o{ COVERAGE : "coverage"

    BASELINE ||--o{ BASELINE_ITEM : "contains"

    ENTITY_VERSION ||--o{ BASELINE_ITEM : "versioned"

    CHANGE_REQUEST ||--o{ APPROVAL : "requires"
    CHANGE_REQUEST ||--o{ AUDIT_LOG : "logged"

    REVIEW ||--o{ REVIEW_ITEM : "contains"

    SOFTWARE_ITEM ||--o{ SOFTWARE_DESIGN : "has"
    SOFTWARE_ITEM ||--o{ SOFTWARE_CODE : "has"
    SOFTWARE_ITEM ||--o{ COVERAGE : "covered by"

    HARDWARE_ITEM ||--o{ HARDWARE_DESIGN : "has"
    HARDWARE_ITEM ||--o{ HARDWARE_IMPLEMENTATION : "has"

    AI_JOB ||--o{ AUDIT_LOG : "logged by"

    PROJECT {
        uuid id PK
        text code
        text name
        text description
    }

    USER {
        uuid id PK
        text username
        text full_name
        text email
        text role
    }

    REQUIREMENT_TYPE {
        int id PK
        text code
        text name
    }

    REQUIREMENT {
        uuid id PK
        text req_id
        text title
        text description
        text status
        text level
        text discipline
        text origin
        text dal
        int version
        jsonb metadata
        boolean approval_required
        uuid project_id FK
    }

    REQUIREMENT_DERIVATION {
        uuid id PK
        uuid parent_req_id FK
        uuid child_req_id FK
        text rationale
    }

    WBS_NODE {
        uuid id PK
        text code
        text title
        uuid parent_id FK
        jsonb metadata
        uuid project_id FK
    }

    S1000D_RESP {
        uuid id PK
        text dm_id
        text role
        text role_code
        text organization
        uuid contact_user_id FK
        uuid project_id FK
    }

    ALLOCATION {
        uuid id PK
        uuid requirement_id FK
        uuid wbs_node_id FK
        uuid s1000d_resp_id FK
        text allocation_type
    }

    ARTIFACT {
        uuid id PK
        text title
        text kind
        text storage_type
        text external_uri
        int version
        jsonb metadata
        uuid project_id FK
    }

    DESIGN_ITEM {
        uuid id PK
        text code
        text discipline
        uuid artifact_id FK
        int version
        jsonb metadata
    }

    SOFTWARE_ITEM {
        uuid id PK
        text identifier
        text dal
        text type
        int version
        jsonb metadata
        uuid project_id FK
    }

    SOFTWARE_DESIGN {
        uuid id PK
        uuid software_item_id FK
        text design_level
        text description
        jsonb metadata
    }

    SOFTWARE_CODE {
        uuid id PK
        uuid software_item_id FK
        text language
        text repo_uri
        text version
        jsonb metadata
    }

    HARDWARE_ITEM {
        uuid id PK
        text identifier
        text dal
        text type
        int version
        jsonb metadata
        uuid project_id FK
    }

    HARDWARE_DESIGN {
        uuid id PK
        uuid hardware_item_id FK
        text design_level
        text description
        jsonb metadata
    }

    HARDWARE_IMPLEMENTATION {
        uuid id PK
        uuid hardware_item_id FK
        text type
        text version
        text repo_uri
        jsonb metadata
    }

    BASELINE {
        uuid id PK
        text name
        text description
        uuid project_id FK
    }

    ENTITY_VERSION {
        uuid id PK
        text entity_type
        uuid entity_id
        int version_number
        jsonb snapshot
        timestamptz created_at
        uuid created_by FK
    }

    BASELINE_ITEM {
        uuid id PK
        text item_type
        uuid item_id
        uuid entity_version_id FK
        jsonb metadata
    }

    VERIFICATION {
        uuid id PK
        text code
        text method
        text method_details
        text environment
        uuid config_baseline_id FK
        uuid testbench_artifact_id FK
        int version
        jsonb result
        boolean approval_required
        uuid project_id FK
    }

    VALIDATION {
        uuid id PK
        uuid requirement_id FK
        uuid verification_id FK
        text verdict
        text context
        text acceptance_criteria
        uuid verifier_user_id FK
        date verdict_date
    }

    TRACELINK {
        uuid id PK
        text src_type
        uuid src_id
        text dst_type
        uuid dst_id
        text link_type
    }

    CHANGE_REQUEST {
        uuid id PK
        text cr_id
        text title
        text description
        text status
        uuid project_id FK
    }

    APPROVAL {
        uuid id PK
        text entity_type
        uuid entity_id
        uuid approved_by FK
        text verdict
    }

    AUDIT_LOG {
        bigserial id PK
        uuid actor_id FK
        text actor_type
        text action
        text target_type
        uuid target_id
        jsonb payload
    }

    REVIEW {
        uuid id PK
        text name
        text type
        date date
        uuid conducted_by FK
        text notes
        uuid project_id FK
    }

    REVIEW_ITEM {
        uuid id PK
        uuid review_id FK
        text entity_type
        uuid entity_id
        text findings
        text status
    }

    COVERAGE {
        uuid id PK
        uuid verification_id FK
        uuid software_item_id FK
        text type
        float percentage
        jsonb details
    }

    LIFECYCLE_DELIVERABLE {
        uuid id PK
        text type
        text title
        text version
        text status
        uuid project_id FK
    }

    AI_JOB {
        uuid id PK
        text job_type
        jsonb payload
        text status
        timestamptz created_at
        uuid executed_by FK
    }
 
Code for PostgreSQL:
-- =============================================
-- PostgreSQL DDL for ARP4754 / DO-178C / DO-254 compliant database
-- Production-ready: indexes, unique constraints, foreign key cascading
-- =============================================

-- Users
CREATE TABLE "user" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL UNIQUE,
    full_name TEXT,
    email TEXT UNIQUE,
    role TEXT NOT NULL -- 'human', 'ai_agent'
);

-- Projects
CREATE TABLE project (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL UNIQUE,
    name TEXT,
    description TEXT
);

-- Requirement Types
CREATE TABLE requirement_type (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT
);

-- Requirements
CREATE TABLE requirement (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    req_id TEXT NOT NULL,
    title TEXT,
    description TEXT,
    status TEXT,
    level TEXT,           -- system, software, hardware
    discipline TEXT,
    origin TEXT,
    dal TEXT,             -- A-E for SW/HW items
    version INT DEFAULT 1,
    metadata JSONB,
    approval_required BOOLEAN DEFAULT TRUE,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE
);

-- Index for fast search
CREATE INDEX idx_requirement_req_id ON requirement(req_id);
CREATE INDEX idx_requirement_project_id ON requirement(project_id);

-- Requirement Derivation
CREATE TABLE requirement_derivation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_req_id UUID REFERENCES requirement(id) ON DELETE CASCADE,
    child_req_id UUID REFERENCES requirement(id) ON DELETE CASCADE,
    rationale TEXT,
    UNIQUE (parent_req_id, child_req_id)
);

-- WBS Nodes
CREATE TABLE wbs_node (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL,
    title TEXT,
    parent_id UUID REFERENCES wbs_node(id) ON DELETE CASCADE,
    metadata JSONB,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE
);

CREATE INDEX idx_wbs_code_project ON wbs_node(code, project_id);

-- S1000D Responsibility
CREATE TABLE s1000d_resp (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dm_id TEXT,
    role TEXT,
    role_code TEXT,
    organization TEXT,
    contact_user_id UUID REFERENCES "user"(id) ON DELETE SET NULL,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE
);

-- Artifacts
CREATE TABLE artifact (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    kind TEXT,
    storage_type TEXT,
    external_uri TEXT,
    version INT DEFAULT 1,
    metadata JSONB,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE,
    UNIQUE(title, project_id)
);

CREATE INDEX idx_artifact_title ON artifact(title);

-- Design Items
CREATE TABLE design_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT,
    discipline TEXT,
    artifact_id UUID REFERENCES artifact(id) ON DELETE CASCADE,
    version INT DEFAULT 1,
    metadata JSONB
);

CREATE INDEX idx_design_item_code ON design_item(code);

-- Software Items
CREATE TABLE software_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identifier TEXT NOT NULL,
    dal TEXT,
    type TEXT,
    version INT DEFAULT 1,
    metadata JSONB,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE,
    UNIQUE(identifier, project_id)
);

CREATE INDEX idx_software_identifier ON software_item(identifier);

CREATE TABLE software_design (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    software_item_id UUID REFERENCES software_item(id) ON DELETE CASCADE,
    design_level TEXT,   -- HLR, LLR
    description TEXT,
    metadata JSONB
);

CREATE TABLE software_code (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    software_item_id UUID REFERENCES software_item(id) ON DELETE CASCADE,
    language TEXT,
    repo_uri TEXT,
    version TEXT,
    metadata JSONB
);

-- Hardware Items
CREATE TABLE hardware_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identifier TEXT NOT NULL,
    dal TEXT,
    type TEXT,
    version INT DEFAULT 1,
    metadata JSONB,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE,
    UNIQUE(identifier, project_id)
);

CREATE INDEX idx_hardware_identifier ON hardware_item(identifier);

CREATE TABLE hardware_design (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hardware_item_id UUID REFERENCES hardware_item(id) ON DELETE CASCADE,
    design_level TEXT,
    description TEXT,
    metadata JSONB
);

CREATE TABLE hardware_implementation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hardware_item_id UUID REFERENCES hardware_item(id) ON DELETE CASCADE,
    type TEXT,
    version TEXT,
    repo_uri TEXT,
    metadata JSONB
);

-- Baselines
CREATE TABLE baseline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE,
    UNIQUE(name, project_id)
);

CREATE INDEX idx_baseline_name_project ON baseline(name, project_id);

-- Entity Versions
CREATE TABLE entity_version (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    version_number INT DEFAULT 1,
    snapshot JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES "user"(id)
);

-- Allocations
CREATE TABLE allocation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID REFERENCES requirement(id) ON DELETE CASCADE,
    wbs_node_id UUID REFERENCES wbs_node(id) ON DELETE CASCADE,
    s1000d_resp_id UUID REFERENCES s1000d_resp(id) ON DELETE SET NULL,
    allocation_type TEXT
);

-- Verification
CREATE TABLE verification (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT,
    method TEXT,
    method_details TEXT,
    environment TEXT,
    config_baseline_id UUID REFERENCES baseline(id) ON DELETE SET NULL,
    testbench_artifact_id UUID REFERENCES artifact(id) ON DELETE SET NULL,
    version INT DEFAULT 1,
    result JSONB,
    approval_required BOOLEAN DEFAULT TRUE,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE
);

CREATE INDEX idx_verification_code_project ON verification(code, project_id);

-- Validation
CREATE TABLE validation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID REFERENCES requirement(id) ON DELETE CASCADE,
    verification_id UUID REFERENCES verification(id) ON DELETE CASCADE,
    verdict TEXT,
    context TEXT,
    acceptance_criteria TEXT,
    verifier_user_id UUID REFERENCES "user"(id) ON DELETE SET NULL,
    verdict_date DATE
);

-- Trace Links
CREATE TABLE tracelink (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    src_type TEXT,
    src_id UUID,
    dst_type TEXT,
    dst_id UUID,
    link_type TEXT
);

-- Baseline Items
CREATE TABLE baseline_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_type TEXT,
    item_id UUID,
    entity_version_id UUID REFERENCES entity_version(id),
    metadata JSONB
);

-- Change Requests
CREATE TABLE change_request (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cr_id TEXT NOT NULL,
    title TEXT,
    description TEXT,
    status TEXT,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE,
    UNIQUE(cr_id, project_id)
);

-- Approvals
CREATE TABLE approval (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT,
    entity_id UUID,
    approved_by UUID REFERENCES "user"(id) ON DELETE SET NULL,
    verdict TEXT
);

-- Audit Logs
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    actor_id UUID REFERENCES "user"(id) ON DELETE SET NULL,
    actor_type TEXT, -- human or ai_agent
    action TEXT,
    target_type TEXT,
    target_id UUID,
    payload JSONB
);

-- Reviews
CREATE TABLE review (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT,
    type TEXT,
    date DATE,
    conducted_by UUID REFERENCES "user"(id) ON DELETE SET NULL,
    notes TEXT,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE
);

CREATE TABLE review_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID REFERENCES review(id) ON DELETE CASCADE,
    entity_type TEXT,
    entity_id UUID,
    findings TEXT,
    status TEXT
);

-- Coverage
CREATE TABLE coverage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    verification_id UUID REFERENCES verification(id) ON DELETE CASCADE,
    software_item_id UUID REFERENCES software_item(id) ON DELETE CASCADE,
    type TEXT,
    percentage FLOAT,
    details JSONB
);

-- Lifecycle Deliverables
CREATE TABLE lifecycle_deliverable (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT,
    title TEXT,
    version TEXT,
    status TEXT,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE
);

-- AI Job Queue
CREATE TABLE ai_job (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type TEXT,
    payload JSONB,
    status TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    executed_by UUID REFERENCES "user"(id) ON DELETE SET NULL
);

-- =============================================
-- End of production-ready schema
-- =============================================
