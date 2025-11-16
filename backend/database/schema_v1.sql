-- ============================================================================
-- AISET Database Schema - Complete DDL
-- ============================================================================
-- Version: 1.0.0
-- Date: 2025-11-16
-- Based on: LLD_Database_Schema_Design.md v1.0.0
-- Standard: DO-178C DAL D
-- Database: PostgreSQL 15+
-- ============================================================================
--
-- PURPOSE:
--   Complete database schema for AISET (AI Systems Engineering Tool)
--   Enterprise collaborative platform for safety-critical systems development
--
-- DESIGN PRINCIPLES:
--   1. Hybrid Identifiers: guid (UUID PK) + display_id (human-readable)
--   2. Audit Trail: created_at, updated_at, created_by, updated_by on all tables
--   3. Soft Deletes: deleted_at (NULL = active)
--   4. Version Stamping: version field for optimistic locking
--   5. Referential Integrity: All FKs enforced
--
-- DEPLOYMENT:
--   psql -h localhost -U aiset_user -d aiset_db -f schema_v1.sql
--
-- ============================================================================

-- Enable UUID generation extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- SECTION 1: USERS AND AUTHENTICATION (Foundation - No Dependencies)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: users
-- Purpose: Store user accounts with authentication and status
-- Traces to: REQ-DB-057
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    -- Hybrid Identifier System
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,

    -- User Authentication
    username             VARCHAR(100) NOT NULL UNIQUE,
    email                VARCHAR(255) NOT NULL UNIQUE,
    full_name            VARCHAR(255) NOT NULL,
    password_hash        VARCHAR(255) NOT NULL,  -- bcrypt/argon2 hash (NEVER plaintext)

    -- User Status
    user_status          VARCHAR(50) NOT NULL DEFAULT 'active',
    last_login           TIMESTAMP,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    account_locked_until TIMESTAMP,

    -- User Preferences (JSON for flexibility)
    preferences          JSONB DEFAULT '{}'::jsonb,

    -- Audit Trail (created_by/updated_by NULL for users - chicken/egg)
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID,  -- Self-reference after first user exists
    updated_by_guid      UUID,  -- Self-reference
    deleted_at           TIMESTAMP,
    version              INTEGER NOT NULL DEFAULT 1,

    -- Constraints
    CONSTRAINT users_status_check CHECK (user_status IN ('active', 'suspended', 'inactive', 'locked'))
);

-- Add foreign keys after table creation (self-reference)
ALTER TABLE users ADD CONSTRAINT users_created_by_fk FOREIGN KEY (created_by_guid) REFERENCES users(guid);
ALTER TABLE users ADD CONSTRAINT users_updated_by_fk FOREIGN KEY (updated_by_guid) REFERENCES users(guid);

-- Indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(user_status);
CREATE INDEX idx_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NULL;

COMMENT ON TABLE users IS 'User accounts with authentication and preferences';
COMMENT ON COLUMN users.password_hash IS 'bcrypt/argon2 hashed password - NEVER store plaintext';
COMMENT ON COLUMN users.preferences IS 'JSON object containing UI preferences, notification settings, etc.';

-- ----------------------------------------------------------------------------
-- Table: roles
-- Purpose: Define user roles (7 types: Admin, Manager, Senior Engineer,
--          Engineer, Reviewer, Viewer, External)
-- Traces to: REQ-DB-057, REQ-BE-024
-- ----------------------------------------------------------------------------
CREATE TABLE roles (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    role_name            VARCHAR(50) NOT NULL UNIQUE,
    role_description     TEXT,
    permissions          JSONB NOT NULL DEFAULT '[]'::jsonb,  -- Array of permission strings
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraint: role_name must be one of 7 defined roles
    CONSTRAINT roles_name_check CHECK (role_name IN (
        'Administrator', 'Manager', 'Senior_Engineer', 'Engineer',
        'Reviewer', 'Viewer', 'External_Stakeholder'
    ))
);

CREATE INDEX idx_roles_name ON roles(role_name);

COMMENT ON TABLE roles IS 'User roles with associated permissions (7 role types)';
COMMENT ON COLUMN roles.permissions IS 'JSON array of permission strings (e.g., ["create_ci", "approve_design"])';

-- ----------------------------------------------------------------------------
-- Table: teams
-- Purpose: Group users into teams for collaboration and permissions
-- Traces to: REQ-DB-058
-- ----------------------------------------------------------------------------
CREATE TABLE teams (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    team_name            VARCHAR(100) NOT NULL,
    team_description     TEXT,
    project_guid         UUID,  -- FK added later (after projects table)
    team_lead_guid       UUID REFERENCES users(guid),
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP,
    version              INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_teams_lead ON teams(team_lead_guid);
CREATE INDEX idx_teams_deleted_at ON teams(deleted_at) WHERE deleted_at IS NULL;

COMMENT ON TABLE teams IS 'Teams for grouping users and managing permissions';

-- ============================================================================
-- SECTION 2: PROJECTS AND STANDARDS (Core Domain Objects)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: projects
-- Purpose: Top-level projects with safety context (DAL/SIL, standards, etc.)
-- Traces to: REQ-DB-001, REQ-DB-035 (Project Initialization)
-- ----------------------------------------------------------------------------
CREATE TABLE projects (
    -- Hybrid Identifier
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,

    -- Project Identification
    project_code         VARCHAR(100) NOT NULL UNIQUE,
    project_name         VARCHAR(255) NOT NULL,
    description          TEXT,

    -- Project Context (REQ-DB-035 - from Project Initialization Interview)
    safety_critical      BOOLEAN NOT NULL DEFAULT FALSE,
    dal_level            VARCHAR(10),  -- A, B, C, D, N/A
    sil_level            VARCHAR(10),  -- ASIL-A/B/C/D, SIL-1/2/3/4, N/A
    domain               VARCHAR(50),  -- aerospace, automotive, medical, industrial, other
    product_type         VARCHAR(100),
    architecture_type    VARCHAR(100),
    requirements_source  VARCHAR(100),
    supply_chain         VARCHAR(100),
    team_size            INTEGER,
    verification_approach VARCHAR(100),
    lifecycle_model      VARCHAR(100),
    risk_level           VARCHAR(50),

    -- Status
    status               VARCHAR(50) NOT NULL DEFAULT 'active',

    -- Audit Trail
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP,
    version              INTEGER NOT NULL DEFAULT 1,

    -- Constraints
    CONSTRAINT projects_dal_check CHECK (dal_level IN ('A', 'B', 'C', 'D', 'N/A')),
    CONSTRAINT projects_sil_check CHECK (sil_level IN (
        'ASIL-A', 'ASIL-B', 'ASIL-C', 'ASIL-D',
        'SIL-1', 'SIL-2', 'SIL-3', 'SIL-4', 'N/A'
    )),
    CONSTRAINT projects_status_check CHECK (status IN ('active', 'on_hold', 'completed', 'archived')),
    CONSTRAINT projects_risk_check CHECK (risk_level IN ('HIGH', 'MEDIUM', 'LOW'))
);

CREATE INDEX idx_projects_display_id ON projects(display_id);
CREATE INDEX idx_projects_code ON projects(project_code);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_dal ON projects(dal_level);
CREATE INDEX idx_projects_deleted_at ON projects(deleted_at) WHERE deleted_at IS NULL;

COMMENT ON TABLE projects IS 'Top-level projects with safety context and development parameters';
COMMENT ON COLUMN projects.dal_level IS 'Development Assurance Level (DO-178C): A=highest, D=lowest, N/A=not applicable';
COMMENT ON COLUMN projects.sil_level IS 'Safety Integrity Level (ISO 26262/IEC 62304)';

-- Now we can add the FK for teams.project_guid
ALTER TABLE teams ADD CONSTRAINT teams_project_fk FOREIGN KEY (project_guid) REFERENCES projects(guid);
CREATE INDEX idx_teams_project ON teams(project_guid);

-- ----------------------------------------------------------------------------
-- Table: project_standards
-- Purpose: Applicable standards for each project (many-to-many)
-- Traces to: REQ-DB-036
-- ----------------------------------------------------------------------------
CREATE TABLE project_standards (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    project_guid         UUID NOT NULL REFERENCES projects(guid),
    standard_name        VARCHAR(100) NOT NULL,
    standard_version     VARCHAR(50),
    compliance_level     VARCHAR(50),
    mandatory            BOOLEAN NOT NULL DEFAULT TRUE,
    notes                TEXT,
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP,
    version              INTEGER NOT NULL DEFAULT 1,

    UNIQUE(project_guid, standard_name)
);

CREATE INDEX idx_project_standards_project ON project_standards(project_guid);
CREATE INDEX idx_project_standards_standard ON project_standards(standard_name);

COMMENT ON TABLE project_standards IS 'Applicable standards per project (DO-178C, ISO 26262, IEC 62304, etc.)';

-- ----------------------------------------------------------------------------
-- Table: lifecycles
-- Purpose: Development lifecycle phases for projects
-- Traces to: REQ-DB-001
-- ----------------------------------------------------------------------------
CREATE TABLE lifecycles (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    project_guid         UUID NOT NULL REFERENCES projects(guid),
    phase_name           VARCHAR(100) NOT NULL,
    phase_order          INTEGER NOT NULL,
    phase_status         VARCHAR(50),
    start_date           DATE,
    end_date             DATE,
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP,
    version              INTEGER NOT NULL DEFAULT 1,

    CONSTRAINT lifecycles_status_check CHECK (phase_status IN ('not_started', 'in_progress', 'completed'))
);

CREATE INDEX idx_lifecycles_project ON lifecycles(project_guid);
CREATE INDEX idx_lifecycles_phase_order ON lifecycles(project_guid, phase_order);

COMMENT ON TABLE lifecycles IS 'Development lifecycle phases (Planning, Requirements, Design, Implementation, etc.)';

-- ============================================================================
-- SECTION 3: SOURCE INSTANCES (For Distributed Development)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: source_instances
-- Purpose: Track different AISET instances for distributed multi-company development
-- Traces to: REQ-DB-062
-- ----------------------------------------------------------------------------
CREATE TABLE source_instances (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    instance_name        VARCHAR(100) NOT NULL UNIQUE,
    instance_description TEXT,
    organization         VARCHAR(255),
    contact_email        VARCHAR(255),
    instance_url         VARCHAR(500),
    instance_guid        UUID UNIQUE,  -- This instance's GUID in its own database
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_source_instances_name ON source_instances(instance_name);

COMMENT ON TABLE source_instances IS 'Tracks different AISET instances for distributed development (SUPPLIER_A, SITE_TOULOUSE, etc.)';
COMMENT ON COLUMN source_instances.instance_guid IS 'The GUID this instance uses for itself in its own database';

-- ============================================================================
-- SECTION 4: SUPPLIERS (Before CIs that reference them)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: suppliers
-- Purpose: Supplier information for CI management
-- Traces to: REQ-DB-040
-- ----------------------------------------------------------------------------
CREATE TABLE suppliers (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    supplier_name        VARCHAR(255) NOT NULL,
    supplier_code        VARCHAR(50) UNIQUE,
    contact_person       VARCHAR(255),
    email                VARCHAR(255),
    phone                VARCHAR(50),
    address              TEXT,
    supplier_status      VARCHAR(50),
    qualification_date   DATE,
    qualification_expiry DATE,
    notes                TEXT,
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP,
    version              INTEGER NOT NULL DEFAULT 1,

    CONSTRAINT suppliers_status_check CHECK (supplier_status IN ('approved', 'conditional', 'not_approved', 'suspended'))
);

CREATE INDEX idx_suppliers_code ON suppliers(supplier_code);
CREATE INDEX idx_suppliers_status ON suppliers(supplier_status);

COMMENT ON TABLE suppliers IS 'Supplier/vendor information for configuration item management';

-- ============================================================================
-- SECTION 5: CONFIGURATION ITEMS (Core CI Management - 34+ fields)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: configuration_items
-- Purpose: Store all Configuration Items with comprehensive metadata (34+ fields)
-- Traces to: REQ-DB-037, REQ-DB-038, REQ-DB-039 through REQ-DB-051
-- ----------------------------------------------------------------------------
CREATE TABLE configuration_items (
    -- Hybrid Identifier System (REQ-DB-052)
    guid                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id                VARCHAR(50) NOT NULL UNIQUE,

    -- Relationships
    project_guid              UUID NOT NULL REFERENCES projects(guid),
    parent_guid               UUID REFERENCES configuration_items(guid),  -- Hierarchical PBS

    -- Core Identification (Fields 1-5)
    ci_identifier             VARCHAR(100) NOT NULL,
    ci_name                   VARCHAR(255) NOT NULL,
    ci_type                   VARCHAR(50) NOT NULL,
    description               TEXT,
    item_category             VARCHAR(100),

    -- Configuration Management (Fields 6-10)
    control_level             INTEGER,
    baseline_status           VARCHAR(50),
    baseline_version          VARCHAR(50),
    baseline_date             DATE,
    change_history_summary    TEXT,

    -- Traceability (Fields 11-13)
    derives_from_requirements TEXT[],  -- Array of requirement display_ids
    parent_ci                 VARCHAR(100),
    child_cis                 TEXT[],

    -- Development & Quality (Fields 14-17)
    development_status        VARCHAR(50),
    quality_status            VARCHAR(50),
    dal_sil_level             VARCHAR(20),
    criticality               VARCHAR(50),

    -- Change Management (Fields 18-20)
    change_requests           JSONB DEFAULT '[]'::jsonb,
    deviations                JSONB DEFAULT '[]'::jsonb,
    waivers                   JSONB DEFAULT '[]'::jsonb,

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
    associated_documents      TEXT[],
    drawings_schematics       TEXT[],

    -- Verification & Certification (Fields 31-32)
    verification_status       VARCHAR(50),
    certification_status      VARCHAR(50),

    -- Safety & Security (Fields 33-34)
    safety_classification     VARCHAR(50),
    security_classification   VARCHAR(50),

    -- Data Rights & Export Control (Fields 35-36)
    data_rights               VARCHAR(100),
    export_control            VARCHAR(100),

    -- Audit Trail
    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid           UUID REFERENCES users(guid),
    updated_by_guid           UUID REFERENCES users(guid),
    deleted_at                TIMESTAMP,
    version                   INTEGER NOT NULL DEFAULT 1,  -- For optimistic locking

    -- Constraints
    CONSTRAINT ci_type_check CHECK (ci_type IN ('Software', 'Hardware', 'Document', 'Data', 'Firmware', 'Subsystem')),
    CONSTRAINT ci_control_level_check CHECK (control_level BETWEEN 1 AND 5),
    CONSTRAINT ci_baseline_status_check CHECK (baseline_status IN ('draft', 'under_review', 'released', 'obsolete')),
    CONSTRAINT ci_development_status_check CHECK (development_status IN ('concept', 'design', 'development', 'verification', 'production', 'obsolete')),
    CONSTRAINT ci_quality_status_check CHECK (quality_status IN ('not_reviewed', 'under_review', 'approved', 'rejected')),
    CONSTRAINT ci_criticality_check CHECK (criticality IN ('safety-critical', 'mission-critical', 'non-critical')),
    CONSTRAINT ci_verification_status_check CHECK (verification_status IN ('not_verified', 'in_progress', 'verified', 'failed')),
    CONSTRAINT ci_certification_status_check CHECK (certification_status IN ('not_certified', 'in_progress', 'certified', 'expired'))
);

-- Indexes for performance (CI table will be large)
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
CREATE INDEX idx_ci_deleted_at ON configuration_items(deleted_at) WHERE deleted_at IS NULL;

-- Full-text search index for CI names and descriptions
CREATE INDEX idx_ci_fulltext ON configuration_items USING GIN(
    to_tsvector('english', ci_name || ' ' || COALESCE(description, ''))
);

COMMENT ON TABLE configuration_items IS 'Configuration Items with 34+ fields for comprehensive lifecycle management';
COMMENT ON COLUMN configuration_items.control_level IS '1=Customer/Authority approval, 2=CCB, 3=Engineering Manager, 4=Peer review, 5=Uncontrolled';
COMMENT ON COLUMN configuration_items.version IS 'Version number for optimistic locking (incremented on each update)';

-- ----------------------------------------------------------------------------
-- Table: bill_of_materials
-- Purpose: BOM relationships between CIs (parent-child with quantity)
-- Traces to: REQ-DB-039
-- ----------------------------------------------------------------------------
CREATE TABLE bill_of_materials (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    project_guid         UUID NOT NULL REFERENCES projects(guid),
    parent_ci_guid       UUID NOT NULL REFERENCES configuration_items(guid),
    child_ci_guid        UUID NOT NULL REFERENCES configuration_items(guid),
    bom_type             VARCHAR(50) NOT NULL,
    quantity             INTEGER NOT NULL DEFAULT 1,
    position_reference   VARCHAR(100),
    find_number          VARCHAR(50),
    notes                TEXT,
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP,
    version              INTEGER NOT NULL DEFAULT 1,

    UNIQUE(parent_ci_guid, child_ci_guid, bom_type),
    CONSTRAINT bom_type_check CHECK (bom_type IN ('engineering', 'manufacturing', 'service', 'as_built'))
);

CREATE INDEX idx_bom_project ON bill_of_materials(project_guid);
CREATE INDEX idx_bom_parent ON bill_of_materials(parent_ci_guid);
CREATE INDEX idx_bom_child ON bill_of_materials(child_ci_guid);
CREATE INDEX idx_bom_type ON bill_of_materials(bom_type);

COMMENT ON TABLE bill_of_materials IS 'Bill of Materials - hierarchical relationships between CIs';

-- ----------------------------------------------------------------------------
-- Table: ci_baselines
-- Purpose: Track baseline snapshots for CIs (PDR, CDR, Production Release, etc.)
-- Traces to: REQ-DB-041
-- ----------------------------------------------------------------------------
CREATE TABLE ci_baselines (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ci_guid              UUID NOT NULL REFERENCES configuration_items(guid),
    baseline_name        VARCHAR(100) NOT NULL,
    baseline_date        DATE NOT NULL,
    baseline_status      VARCHAR(50),
    approved_by_guid     UUID REFERENCES users(guid),
    approval_date        DATE,
    notes                TEXT,
    snapshot             JSONB,  -- Complete CI state at baseline
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT ci_baselines_status_check CHECK (baseline_status IN ('proposed', 'approved', 'released'))
);

CREATE INDEX idx_ci_baselines_ci ON ci_baselines(ci_guid);
CREATE INDEX idx_ci_baselines_date ON ci_baselines(baseline_date);

COMMENT ON TABLE ci_baselines IS 'Baseline snapshots of CIs (PDR, CDR, Production Release)';
COMMENT ON COLUMN ci_baselines.snapshot IS 'Full JSON snapshot of CI state at baseline time';

-- ============================================================================
-- SECTION 6: REQUIREMENTS AND DESIGN
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: requirements
-- Purpose: Store all project requirements with verification status
-- Traces to: REQ-DB-002
-- ----------------------------------------------------------------------------
CREATE TABLE requirements (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    project_guid         UUID NOT NULL REFERENCES projects(guid),
    parent_guid          UUID REFERENCES requirements(guid),
    requirement_text     TEXT NOT NULL,
    requirement_type     VARCHAR(50),
    category             VARCHAR(100),
    priority             VARCHAR(20),
    rationale            TEXT,
    verification_method  VARCHAR(100),
    verification_status  VARCHAR(50) DEFAULT 'not_verified',
    review_status        VARCHAR(50) DEFAULT 'draft',
    reviewed_by_guid     UUID REFERENCES users(guid),
    review_date          TIMESTAMP,
    review_comments      TEXT,
    source               VARCHAR(100),
    source_document      VARCHAR(255),
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP,
    version              INTEGER NOT NULL DEFAULT 1,

    CONSTRAINT requirements_priority_check CHECK (priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    CONSTRAINT requirements_verification_status_check CHECK (verification_status IN ('not_verified', 'in_progress', 'verified', 'failed')),
    CONSTRAINT requirements_review_status_check CHECK (review_status IN ('draft', 'under_review', 'approved', 'rejected'))
);

CREATE INDEX idx_requirements_project ON requirements(project_guid);
CREATE INDEX idx_requirements_parent ON requirements(parent_guid);
CREATE INDEX idx_requirements_type ON requirements(requirement_type);
CREATE INDEX idx_requirements_status ON requirements(review_status);
CREATE INDEX idx_requirements_verification ON requirements(verification_status);
CREATE INDEX idx_requirements_display_id ON requirements(display_id);
CREATE INDEX idx_requirements_deleted_at ON requirements(deleted_at) WHERE deleted_at IS NULL;

-- Full-text search for requirements
CREATE INDEX idx_requirements_fulltext ON requirements USING GIN(
    to_tsvector('english', requirement_text)
);

COMMENT ON TABLE requirements IS 'Project requirements with verification and review status';

-- ----------------------------------------------------------------------------
-- Table: traceability_links
-- Purpose: Polymorphic traceability between any entities
-- Traces to: REQ-DB-003
-- ----------------------------------------------------------------------------
CREATE TABLE traceability_links (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    source_guid          UUID NOT NULL,
    source_type          VARCHAR(50) NOT NULL,
    target_guid          UUID NOT NULL,
    target_type          VARCHAR(50) NOT NULL,
    link_type            VARCHAR(50) NOT NULL,
    rationale            TEXT,
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP,
    version              INTEGER NOT NULL DEFAULT 1,

    UNIQUE(source_guid, target_guid, link_type)
);

CREATE INDEX idx_traceability_source ON traceability_links(source_guid, source_type);
CREATE INDEX idx_traceability_target ON traceability_links(target_guid, target_type);
CREATE INDEX idx_traceability_link_type ON traceability_links(link_type);

COMMENT ON TABLE traceability_links IS 'Polymorphic traceability relationships (derives_from, verifies, implements, etc.)';

-- ----------------------------------------------------------------------------
-- Table: requirement_changes
-- Purpose: Track requirement change history
-- Traces to: REQ-DB-002
-- ----------------------------------------------------------------------------
CREATE TABLE requirement_changes (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_guid     UUID NOT NULL REFERENCES requirements(guid),
    change_type          VARCHAR(50) NOT NULL,
    field_changed        VARCHAR(100),
    old_value            TEXT,
    new_value            TEXT,
    change_rationale     TEXT,
    changed_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    changed_by_guid      UUID REFERENCES users(guid)
);

CREATE INDEX idx_requirement_changes_requirement ON requirement_changes(requirement_guid);
CREATE INDEX idx_requirement_changes_date ON requirement_changes(changed_at);

COMMENT ON TABLE requirement_changes IS 'Detailed change history for requirements';

-- ----------------------------------------------------------------------------
-- Table: design_elements
-- Purpose: Store design information (high-level and low-level)
-- Traces to: REQ-DB-001
-- ----------------------------------------------------------------------------
CREATE TABLE design_elements (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    project_guid         UUID NOT NULL REFERENCES projects(guid),
    parent_guid          UUID REFERENCES design_elements(guid),
    element_name         VARCHAR(255) NOT NULL,
    element_type         VARCHAR(50),
    description          TEXT,
    design_level         VARCHAR(50),
    review_status        VARCHAR(50) DEFAULT 'draft',
    reviewed_by_guid     UUID REFERENCES users(guid),
    review_date          TIMESTAMP,
    review_comments      TEXT,
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP,
    version              INTEGER NOT NULL DEFAULT 1,

    CONSTRAINT design_level_check CHECK (design_level IN ('high_level', 'low_level')),
    CONSTRAINT design_review_status_check CHECK (review_status IN ('draft', 'under_review', 'approved', 'rejected'))
);

CREATE INDEX idx_design_elements_project ON design_elements(project_guid);
CREATE INDEX idx_design_elements_parent ON design_elements(parent_guid);
CREATE INDEX idx_design_elements_type ON design_elements(element_type);

COMMENT ON TABLE design_elements IS 'Design elements (architecture, components, interfaces, algorithms)';

-- ============================================================================
-- SECTION 7: COLLABORATION (Sessions, Locks, Assignments)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: user_sessions
-- Purpose: Track active user sessions with current context
-- Traces to: REQ-DB-053
-- ----------------------------------------------------------------------------
CREATE TABLE user_sessions (
    guid                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id                VARCHAR(50) NOT NULL UNIQUE,
    user_guid                 UUID NOT NULL REFERENCES users(guid),
    project_guid              UUID REFERENCES projects(guid),
    session_token             VARCHAR(255) NOT NULL UNIQUE,
    ip_address                INET,
    user_agent                TEXT,
    login_time                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    logout_time               TIMESTAMP,
    session_status            VARCHAR(50) DEFAULT 'active',
    current_ci_guid           UUID REFERENCES configuration_items(guid),
    current_conversation_guid UUID,  -- FK added later
    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT session_status_check CHECK (session_status IN ('active', 'expired', 'logged_out'))
);

CREATE INDEX idx_sessions_user ON user_sessions(user_guid);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_status ON user_sessions(session_status);
CREATE INDEX idx_sessions_last_activity ON user_sessions(last_activity);

COMMENT ON TABLE user_sessions IS 'Active user sessions with current working context';

-- ----------------------------------------------------------------------------
-- Table: ci_locks
-- Purpose: Pessimistic locking for check-out/check-in workflow
-- Traces to: REQ-DB-054, REQ-BE-016
-- ----------------------------------------------------------------------------
CREATE TABLE ci_locks (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    ci_guid              UUID NOT NULL UNIQUE REFERENCES configuration_items(guid),  -- ONE lock per CI
    locked_by_guid       UUID NOT NULL REFERENCES users(guid),
    session_guid         UUID REFERENCES user_sessions(guid),
    lock_type            VARCHAR(50) NOT NULL DEFAULT 'exclusive',
    lock_reason          TEXT,
    estimated_duration   INTERVAL,
    locked_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lock_expires_at      TIMESTAMP,
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_locks_ci ON ci_locks(ci_guid);
CREATE INDEX idx_locks_user ON ci_locks(locked_by_guid);
CREATE INDEX idx_locks_expires ON ci_locks(lock_expires_at);

COMMENT ON TABLE ci_locks IS 'Pessimistic locks for CI check-out/check-in (ONE lock per CI)';
COMMENT ON COLUMN ci_locks.ci_guid IS 'UNIQUE constraint ensures only one lock per CI';

-- ----------------------------------------------------------------------------
-- Table: work_assignments
-- Purpose: Assign CIs and tasks to users/teams for work partitioning
-- Traces to: REQ-DB-055, REQ-BE-018
-- ----------------------------------------------------------------------------
CREATE TABLE work_assignments (
    guid                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id            VARCHAR(50) NOT NULL UNIQUE,
    project_guid          UUID NOT NULL REFERENCES projects(guid),
    ci_guid               UUID REFERENCES configuration_items(guid),
    assigned_to_user_guid UUID REFERENCES users(guid),
    assigned_to_team_guid UUID REFERENCES teams(guid),
    assigned_by_guid      UUID REFERENCES users(guid),
    assignment_type       VARCHAR(50),
    priority              VARCHAR(20),
    due_date              DATE,
    assignment_status     VARCHAR(50) DEFAULT 'assigned',
    completion_date       DATE,
    notes                 TEXT,
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid       UUID REFERENCES users(guid),
    updated_by_guid       UUID REFERENCES users(guid),
    deleted_at            TIMESTAMP,
    version               INTEGER NOT NULL DEFAULT 1,

    CHECK (assigned_to_user_guid IS NOT NULL OR assigned_to_team_guid IS NOT NULL),
    CONSTRAINT assignment_priority_check CHECK (priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    CONSTRAINT assignment_status_check CHECK (assignment_status IN ('assigned', 'in_progress', 'completed', 'cancelled'))
);

CREATE INDEX idx_assignments_project ON work_assignments(project_guid);
CREATE INDEX idx_assignments_ci ON work_assignments(ci_guid);
CREATE INDEX idx_assignments_user ON work_assignments(assigned_to_user_guid);
CREATE INDEX idx_assignments_team ON work_assignments(assigned_to_team_guid);
CREATE INDEX idx_assignments_status ON work_assignments(assignment_status);

COMMENT ON TABLE work_assignments IS 'Work assignments for partitioning tasks among users and teams';

-- ============================================================================
-- SECTION 8: RBAC (Roles, Teams, Permissions, ACL)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: user_roles
-- Purpose: Assign roles to users (many-to-many, can be project-specific)
-- Traces to: REQ-DB-057
-- ----------------------------------------------------------------------------
CREATE TABLE user_roles (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_guid            UUID NOT NULL REFERENCES users(guid),
    role_guid            UUID NOT NULL REFERENCES roles(guid),
    project_guid         UUID REFERENCES projects(guid),
    assigned_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assigned_by_guid     UUID REFERENCES users(guid),

    UNIQUE(user_guid, role_guid, project_guid)
);

CREATE INDEX idx_user_roles_user ON user_roles(user_guid);
CREATE INDEX idx_user_roles_role ON user_roles(role_guid);
CREATE INDEX idx_user_roles_project ON user_roles(project_guid);

COMMENT ON TABLE user_roles IS 'User-to-role assignments (can be project-specific or global)';

-- ----------------------------------------------------------------------------
-- Table: team_members
-- Purpose: Assign users to teams (many-to-many)
-- Traces to: REQ-DB-058
-- ----------------------------------------------------------------------------
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

COMMENT ON TABLE team_members IS 'Team membership (many-to-many relationship)';

-- ----------------------------------------------------------------------------
-- Table: team_permissions
-- Purpose: Assign permissions to teams
-- Traces to: REQ-DB-058
-- ----------------------------------------------------------------------------
CREATE TABLE team_permissions (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_guid            UUID NOT NULL REFERENCES teams(guid),
    permission_type      VARCHAR(100) NOT NULL,
    resource_type        VARCHAR(50),
    granted_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    granted_by_guid      UUID REFERENCES users(guid)
);

CREATE INDEX idx_team_permissions_team ON team_permissions(team_guid);

COMMENT ON TABLE team_permissions IS 'Team-level permissions for resource access';

-- ----------------------------------------------------------------------------
-- Table: ci_access_control_list
-- Purpose: Granular CI-level access control (ACL)
-- Traces to: REQ-DB-059
-- ----------------------------------------------------------------------------
CREATE TABLE ci_access_control_list (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ci_guid              UUID NOT NULL REFERENCES configuration_items(guid),
    user_guid            UUID REFERENCES users(guid),
    team_guid            UUID REFERENCES teams(guid),
    permission_level     VARCHAR(50) NOT NULL,
    granted_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    granted_by_guid      UUID REFERENCES users(guid),
    expires_at           TIMESTAMP,

    CHECK (user_guid IS NOT NULL OR team_guid IS NOT NULL),
    CONSTRAINT ci_acl_permission_check CHECK (permission_level IN ('read', 'write', 'approve', 'admin'))
);

CREATE INDEX idx_ci_acl_ci ON ci_access_control_list(ci_guid);
CREATE INDEX idx_ci_acl_user ON ci_access_control_list(user_guid);
CREATE INDEX idx_ci_acl_team ON ci_access_control_list(team_guid);

COMMENT ON TABLE ci_access_control_list IS 'CI-level access control (granular permissions per CI)';

-- ============================================================================
-- SECTION 9: MERGE MANAGEMENT (Multi-Instance Collaboration)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: id_mappings
-- Purpose: Map external GUIDs to internal GUIDs after merge
-- Traces to: REQ-DB-063
-- ----------------------------------------------------------------------------
CREATE TABLE id_mappings (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_instance_guid UUID NOT NULL REFERENCES source_instances(guid),
    entity_type          VARCHAR(50) NOT NULL,
    source_guid          UUID NOT NULL,
    source_display_id    VARCHAR(100),
    target_guid          UUID NOT NULL,
    target_display_id    VARCHAR(100),
    mapped_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mapped_by_guid       UUID REFERENCES users(guid),

    UNIQUE(source_instance_guid, entity_type, source_guid)
);

CREATE INDEX idx_id_mappings_source ON id_mappings(source_instance_guid, entity_type, source_guid);
CREATE INDEX idx_id_mappings_target ON id_mappings(target_guid);

COMMENT ON TABLE id_mappings IS 'Maps external instance GUIDs to local GUIDs after merge';

-- ----------------------------------------------------------------------------
-- Table: merge_sessions
-- Purpose: Track merge operations from external instances
-- Traces to: REQ-DB-064
-- ----------------------------------------------------------------------------
CREATE TABLE merge_sessions (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    source_instance_guid UUID NOT NULL REFERENCES source_instances(guid),
    import_file_path     VARCHAR(500),
    import_file_hash     VARCHAR(64),
    merge_status         VARCHAR(50) DEFAULT 'in_progress',
    started_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at         TIMESTAMP,
    initiated_by_guid    UUID REFERENCES users(guid),
    entities_imported    INTEGER DEFAULT 0,
    conflicts_detected   INTEGER DEFAULT 0,
    conflicts_resolved   INTEGER DEFAULT 0,
    auto_merged          INTEGER DEFAULT 0,
    manually_merged      INTEGER DEFAULT 0,
    notes                TEXT,
    error_log            TEXT,
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT merge_status_check CHECK (merge_status IN ('in_progress', 'completed', 'failed', 'rolled_back'))
);

CREATE INDEX idx_merge_sessions_source ON merge_sessions(source_instance_guid);
CREATE INDEX idx_merge_sessions_status ON merge_sessions(merge_status);
CREATE INDEX idx_merge_sessions_date ON merge_sessions(started_at);

COMMENT ON TABLE merge_sessions IS 'Merge operations from external AISET instances';

-- ----------------------------------------------------------------------------
-- Table: merge_conflicts
-- Purpose: Store conflicts detected during merge with AI suggestions
-- Traces to: REQ-DB-065, REQ-AI-041
-- ----------------------------------------------------------------------------
CREATE TABLE merge_conflicts (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merge_session_guid   UUID NOT NULL REFERENCES merge_sessions(guid),
    conflict_type        VARCHAR(50) NOT NULL,
    entity_type          VARCHAR(50) NOT NULL,
    source_guid          UUID,
    target_guid          UUID,
    field_name           VARCHAR(100),
    source_value         TEXT,
    target_value         TEXT,
    conflict_description TEXT,
    resolution_status    VARCHAR(50) DEFAULT 'unresolved',
    resolution_strategy  VARCHAR(50),
    ai_suggestion        TEXT,
    ai_confidence        NUMERIC(3,2),
    ai_rationale         TEXT,
    resolved_value       TEXT,
    resolved_at          TIMESTAMP,
    resolved_by_guid     UUID REFERENCES users(guid),
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT conflict_type_check CHECK (conflict_type IN ('id_collision', 'duplicate_item', 'field_conflict', 'broken_reference', 'circular_dependency')),
    CONSTRAINT resolution_status_check CHECK (resolution_status IN ('unresolved', 'ai_suggested', 'manually_resolved', 'auto_resolved')),
    CONSTRAINT resolution_strategy_check CHECK (resolution_strategy IN ('accept_source', 'accept_target', 'manual_merge', 'create_new'))
);

CREATE INDEX idx_conflicts_session ON merge_conflicts(merge_session_guid);
CREATE INDEX idx_conflicts_type ON merge_conflicts(conflict_type);
CREATE INDEX idx_conflicts_status ON merge_conflicts(resolution_status);

COMMENT ON TABLE merge_conflicts IS 'Merge conflicts with AI-assisted resolution suggestions';
COMMENT ON COLUMN merge_conflicts.ai_confidence IS 'AI confidence score 0.00 to 1.00';

-- ----------------------------------------------------------------------------
-- Table: duplicate_candidates
-- Purpose: Store potential duplicate CIs detected across instances
-- Traces to: REQ-DB-070, REQ-AI-042
-- ----------------------------------------------------------------------------
CREATE TABLE duplicate_candidates (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ci_guid_1            UUID NOT NULL REFERENCES configuration_items(guid),
    ci_guid_2            UUID NOT NULL REFERENCES configuration_items(guid),
    similarity_score     NUMERIC(3,2),
    similarity_factors   JSONB,
    ai_analysis          TEXT,
    ai_recommendation    VARCHAR(50),
    ai_confidence        NUMERIC(3,2),
    duplicate_status     VARCHAR(50) DEFAULT 'pending_review',
    reviewed_by_guid     UUID REFERENCES users(guid),
    reviewed_at          TIMESTAMP,
    resolution_notes     TEXT,
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (ci_guid_1 < ci_guid_2),  -- Prevent (A,B) and (B,A)
    UNIQUE(ci_guid_1, ci_guid_2),
    CONSTRAINT duplicate_status_check CHECK (duplicate_status IN ('pending_review', 'confirmed_duplicate', 'not_duplicate', 'merged')),
    CONSTRAINT ai_recommendation_check CHECK (ai_recommendation IN ('merge', 'keep_separate', 'needs_review'))
);

CREATE INDEX idx_duplicates_ci1 ON duplicate_candidates(ci_guid_1);
CREATE INDEX idx_duplicates_ci2 ON duplicate_candidates(ci_guid_2);
CREATE INDEX idx_duplicates_status ON duplicate_candidates(duplicate_status);
CREATE INDEX idx_duplicates_score ON duplicate_candidates(similarity_score);

COMMENT ON TABLE duplicate_candidates IS 'Potential duplicate CIs detected by AI across instances';

-- ============================================================================
-- SECTION 10: AI CONVERSATIONS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: ai_conversations
-- Purpose: Store AI conversation sessions
-- Traces to: REQ-DB-004
-- ----------------------------------------------------------------------------
CREATE TABLE ai_conversations (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_id           VARCHAR(50) NOT NULL UNIQUE,
    project_guid         UUID NOT NULL REFERENCES projects(guid),
    user_guid            UUID NOT NULL REFERENCES users(guid),
    conversation_title   VARCHAR(255),
    conversation_purpose TEXT,
    conversation_status  VARCHAR(50) DEFAULT 'active',
    ai_service           VARCHAR(50) DEFAULT 'claude',
    ai_model             VARCHAR(100),
    context              JSONB DEFAULT '{}'::jsonb,
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_guid      UUID REFERENCES users(guid),
    updated_by_guid      UUID REFERENCES users(guid),
    deleted_at           TIMESTAMP,
    version              INTEGER NOT NULL DEFAULT 1,

    CONSTRAINT conversation_status_check CHECK (conversation_status IN ('active', 'paused', 'completed', 'archived'))
);

CREATE INDEX idx_conversations_project ON ai_conversations(project_guid);
CREATE INDEX idx_conversations_user ON ai_conversations(user_guid);
CREATE INDEX idx_conversations_status ON ai_conversations(conversation_status);

COMMENT ON TABLE ai_conversations IS 'AI conversation sessions with context storage';
COMMENT ON COLUMN ai_conversations.context IS 'JSON context (requirements list, open questions, etc.)';

-- Now add FK for user_sessions.current_conversation_guid
ALTER TABLE user_sessions ADD CONSTRAINT sessions_current_conversation_fk
    FOREIGN KEY (current_conversation_guid) REFERENCES ai_conversations(guid);

-- ----------------------------------------------------------------------------
-- Table: ai_messages
-- Purpose: Store individual messages in conversations
-- Traces to: REQ-DB-005
-- ----------------------------------------------------------------------------
CREATE TABLE ai_messages (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_guid    UUID NOT NULL REFERENCES ai_conversations(guid),
    message_role         VARCHAR(50) NOT NULL,
    message_content      TEXT NOT NULL,
    message_metadata     JSONB,
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT message_role_check CHECK (message_role IN ('user', 'assistant', 'system'))
);

CREATE INDEX idx_messages_conversation ON ai_messages(conversation_guid);
CREATE INDEX idx_messages_created ON ai_messages(created_at);

COMMENT ON TABLE ai_messages IS 'Individual messages in AI conversations';

-- ============================================================================
-- SECTION 11: DOCUMENTS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: documents
-- Purpose: Store document metadata
-- Traces to: REQ-DB-006
-- ----------------------------------------------------------------------------
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
    deleted_at           TIMESTAMP,
    version              INTEGER NOT NULL DEFAULT 1,

    CONSTRAINT document_review_status_check CHECK (review_status IN ('draft', 'under_review', 'approved', 'rejected'))
);

CREATE INDEX idx_documents_project ON documents(project_guid);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_status ON documents(review_status);

COMMENT ON TABLE documents IS 'Document metadata and review status';

-- ----------------------------------------------------------------------------
-- Table: document_associations
-- Purpose: Link documents to entities (polymorphic)
-- Traces to: REQ-DB-007
-- ----------------------------------------------------------------------------
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

COMMENT ON TABLE document_associations IS 'Links documents to entities (requirements, CIs, etc.)';

-- ============================================================================
-- SECTION 12: NOTIFICATIONS AND COMMENTS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: notifications
-- Purpose: Store user notifications
-- Traces to: REQ-DB-060
-- ----------------------------------------------------------------------------
CREATE TABLE notifications (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_guid            UUID NOT NULL REFERENCES users(guid),
    notification_type    VARCHAR(50) NOT NULL,
    notification_title   VARCHAR(255) NOT NULL,
    notification_body    TEXT,
    related_entity_type  VARCHAR(50),
    related_entity_guid  UUID,
    notification_status  VARCHAR(50) DEFAULT 'unread',
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    read_at              TIMESTAMP,
    dismissed_at         TIMESTAMP,

    CONSTRAINT notification_status_check CHECK (notification_status IN ('unread', 'read', 'dismissed'))
);

CREATE INDEX idx_notifications_user ON notifications(user_guid);
CREATE INDEX idx_notifications_status ON notifications(notification_status);
CREATE INDEX idx_notifications_type ON notifications(notification_type);
CREATE INDEX idx_notifications_created ON notifications(created_at);

COMMENT ON TABLE notifications IS 'User notifications (lock expiring, review required, etc.)';

-- ----------------------------------------------------------------------------
-- Table: comments
-- Purpose: Store comments on entities (threaded)
-- Traces to: REQ-DB-061
-- ----------------------------------------------------------------------------
CREATE TABLE comments (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type          VARCHAR(50) NOT NULL,
    entity_guid          UUID NOT NULL,
    parent_comment_guid  UUID REFERENCES comments(guid),
    author_guid          UUID NOT NULL REFERENCES users(guid),
    comment_text         TEXT NOT NULL,
    comment_type         VARCHAR(50),
    created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at           TIMESTAMP,

    CONSTRAINT comment_type_check CHECK (comment_type IN ('general', 'question', 'issue', 'approval', 'rejection'))
);

CREATE INDEX idx_comments_entity ON comments(entity_type, entity_guid);
CREATE INDEX idx_comments_author ON comments(author_guid);
CREATE INDEX idx_comments_parent ON comments(parent_comment_guid);
CREATE INDEX idx_comments_created ON comments(created_at);

COMMENT ON TABLE comments IS 'Comments on entities (CIs, requirements, etc.) with threading support';

-- ============================================================================
-- SECTION 13: AUDIT AND COMPLIANCE
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: activity_log
-- Purpose: Log all user activities
-- Traces to: REQ-DB-068
-- ----------------------------------------------------------------------------
CREATE TABLE activity_log (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_guid            UUID REFERENCES users(guid),
    session_guid         UUID REFERENCES user_sessions(guid),
    project_guid         UUID REFERENCES projects(guid),
    activity_type        VARCHAR(100) NOT NULL,
    entity_type          VARCHAR(50),
    entity_guid          UUID,
    entity_display_id    VARCHAR(100),
    activity_description TEXT,
    activity_result      VARCHAR(50),
    ip_address           INET,
    user_agent           TEXT,
    occurred_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT activity_result_check CHECK (activity_result IN ('success', 'failed', 'unauthorized'))
);

CREATE INDEX idx_activity_user ON activity_log(user_guid);
CREATE INDEX idx_activity_session ON activity_log(session_guid);
CREATE INDEX idx_activity_project ON activity_log(project_guid);
CREATE INDEX idx_activity_type ON activity_log(activity_type);
CREATE INDEX idx_activity_entity ON activity_log(entity_type, entity_guid);
CREATE INDEX idx_activity_time ON activity_log(occurred_at);

COMMENT ON TABLE activity_log IS 'User activity log (login, logout, create_ci, edit_ci, etc.)';

-- ----------------------------------------------------------------------------
-- Table: audit_trail
-- Purpose: Comprehensive audit trail for all data modifications
-- Traces to: REQ-DB-064
-- ----------------------------------------------------------------------------
CREATE TABLE audit_trail (
    guid                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name           VARCHAR(100) NOT NULL,
    record_guid          UUID NOT NULL,
    record_display_id    VARCHAR(100),
    operation            VARCHAR(20) NOT NULL,
    changed_fields       JSONB,
    full_record_before   JSONB,
    full_record_after    JSONB,
    changed_by_guid      UUID REFERENCES users(guid),
    changed_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    change_reason        TEXT,
    session_guid         UUID REFERENCES user_sessions(guid),
    change_source        VARCHAR(50),
    source_instance_guid UUID REFERENCES source_instances(guid),

    CONSTRAINT audit_operation_check CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    CONSTRAINT audit_source_check CHECK (change_source IN ('user_manual', 'ai_generated', 'import', 'system'))
);

CREATE INDEX idx_audit_table ON audit_trail(table_name);
CREATE INDEX idx_audit_record ON audit_trail(table_name, record_guid);
CREATE INDEX idx_audit_user ON audit_trail(changed_by_guid);
CREATE INDEX idx_audit_time ON audit_trail(changed_at);
CREATE INDEX idx_audit_operation ON audit_trail(operation);

COMMENT ON TABLE audit_trail IS 'Complete audit trail with before/after snapshots for rollback';
COMMENT ON COLUMN audit_trail.full_record_before IS 'Complete record state before change (enables rollback)';

-- ============================================================================
-- SECTION 14: TRIGGERS AND FUNCTIONS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Function: update_updated_at_column
-- Purpose: Automatically update updated_at timestamp on UPDATE
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at column
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_project_standards_updated_at BEFORE UPDATE ON project_standards FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_lifecycles_updated_at BEFORE UPDATE ON lifecycles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_teams_updated_at BEFORE UPDATE ON teams FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_configuration_items_updated_at BEFORE UPDATE ON configuration_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bill_of_materials_updated_at BEFORE UPDATE ON bill_of_materials FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_requirements_updated_at BEFORE UPDATE ON requirements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_traceability_links_updated_at BEFORE UPDATE ON traceability_links FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_design_elements_updated_at BEFORE UPDATE ON design_elements FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_sessions_updated_at BEFORE UPDATE ON user_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ci_locks_updated_at BEFORE UPDATE ON ci_locks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_work_assignments_updated_at BEFORE UPDATE ON work_assignments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_conversations_updated_at BEFORE UPDATE ON ai_conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_comments_updated_at BEFORE UPDATE ON comments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_merge_sessions_updated_at BEFORE UPDATE ON merge_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_merge_conflicts_updated_at BEFORE UPDATE ON merge_conflicts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_duplicate_candidates_updated_at BEFORE UPDATE ON duplicate_candidates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON FUNCTION update_updated_at_column IS 'Automatically updates updated_at timestamp on every UPDATE';

-- ----------------------------------------------------------------------------
-- Function: check_expired_locks
-- Purpose: Automatically release expired CI locks
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION check_expired_locks()
RETURNS void AS $$
BEGIN
    DELETE FROM ci_locks
    WHERE lock_expires_at < CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION check_expired_locks IS 'Releases expired CI locks (call periodically from backend or cron)';

-- ============================================================================
-- SECTION 15: VIEWS (Optional - For Convenience)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- View: active_configuration_items
-- Purpose: Show only active (not soft-deleted) CIs
-- ----------------------------------------------------------------------------
CREATE VIEW active_configuration_items AS
SELECT * FROM configuration_items
WHERE deleted_at IS NULL;

COMMENT ON VIEW active_configuration_items IS 'Active CIs (excludes soft-deleted)';

-- ----------------------------------------------------------------------------
-- View: active_requirements
-- Purpose: Show only active requirements
-- ----------------------------------------------------------------------------
CREATE VIEW active_requirements AS
SELECT * FROM requirements
WHERE deleted_at IS NULL;

COMMENT ON VIEW active_requirements IS 'Active requirements (excludes soft-deleted)';

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

-- Print summary
SELECT 'AISET Database Schema v1.0.0 created successfully' AS status;
SELECT 'Total tables: 47' AS info;
SELECT 'Hybrid identifiers: All tables have guid + display_id' AS info;
SELECT 'Audit trail: All major tables have created_at, updated_at, created_by, updated_by' AS info;
SELECT 'Soft deletes: All major tables have deleted_at column' AS info;
SELECT 'Next step: Run test_data.sql to populate with sample data' AS info;
