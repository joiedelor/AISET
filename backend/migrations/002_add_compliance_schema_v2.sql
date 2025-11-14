-- =============================================
-- PostgreSQL Migration Script V2
-- ARP4754 / DO-178C / DO-254 Compliance Schema
-- Date: 2025-11-14
-- Author: AISET Development Team
-- =============================================

-- This migration adds tables required for full ARP4754/DO-178C/DO-254 compliance
-- Compatible with existing INTEGER-based schema

BEGIN;

-- =============================================
-- 1. Add missing columns to existing 'requirements' table
-- =============================================
ALTER TABLE requirements ADD COLUMN IF NOT EXISTS level TEXT DEFAULT 'system';
ALTER TABLE requirements ADD COLUMN IF NOT EXISTS discipline TEXT;
ALTER TABLE requirements ADD COLUMN IF NOT EXISTS origin TEXT;
ALTER TABLE requirements ADD COLUMN IF NOT EXISTS dal TEXT;
ALTER TABLE requirements ADD COLUMN IF NOT EXISTS version_number INT DEFAULT 1;
ALTER TABLE requirements ADD COLUMN IF NOT EXISTS metadata JSONB;
ALTER TABLE requirements ADD COLUMN IF NOT EXISTS approval_required BOOLEAN DEFAULT TRUE;

-- =============================================
-- 2. Add missing columns to existing 'projects' table
-- =============================================
ALTER TABLE projects ADD COLUMN IF NOT EXISTS code TEXT;

-- Generate codes for existing projects
UPDATE projects SET code = 'PROJ-' || LPAD(id::TEXT, 4, '0') WHERE code IS NULL;
ALTER TABLE projects ALTER COLUMN code SET NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_project_code ON projects(code);

-- =============================================
-- 3. Add missing columns to 'users' table
-- =============================================
ALTER TABLE users ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'human';
ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name TEXT;

COMMENT ON COLUMN users.role IS 'Values: human, ai_agent';

-- =============================================
-- 4. CREATE NEW TABLES
-- =============================================

-- Requirement Types
CREATE TABLE IF NOT EXISTS requirement_type (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT,
    description TEXT
);

-- Insert default requirement types
INSERT INTO requirement_type (code, name, description)
VALUES
    ('FUNC', 'Functional Requirement', 'Describes what the system shall do'),
    ('PERF', 'Performance Requirement', 'Describes performance criteria'),
    ('SAFE', 'Safety Requirement', 'Safety-critical requirements'),
    ('SEC', 'Security Requirement', 'Security and protection requirements'),
    ('INTF', 'Interface Requirement', 'Interface specifications'),
    ('ENV', 'Environmental Requirement', 'Environmental conditions'),
    ('REL', 'Reliability Requirement', 'Reliability criteria')
ON CONFLICT (code) DO NOTHING;

-- Requirement Derivation (tracks parent-child relationships)
CREATE TABLE IF NOT EXISTS requirement_derivation (
    id SERIAL PRIMARY KEY,
    parent_req_id INTEGER REFERENCES requirements(id) ON DELETE CASCADE,
    child_req_id INTEGER REFERENCES requirements(id) ON DELETE CASCADE,
    rationale TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (parent_req_id, child_req_id)
);

-- WBS Nodes (Work Breakdown Structure - MIL-STD-881)
CREATE TABLE IF NOT EXISTS wbs_node (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL,
    title TEXT,
    parent_id INTEGER REFERENCES wbs_node(id) ON DELETE CASCADE,
    metadata JSONB,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wbs_code_project ON wbs_node(code, project_id);

-- S1000D Responsibility
CREATE TABLE IF NOT EXISTS s1000d_resp (
    id SERIAL PRIMARY KEY,
    dm_id TEXT,
    role TEXT,
    role_code TEXT,
    organization TEXT,
    contact_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Artifacts (documents, models, 3D files, code, etc.)
CREATE TABLE IF NOT EXISTS artifact (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    kind TEXT,  -- 'document', 'model_3d', 'code', 'schema', 'drawing', etc.
    storage_type TEXT,  -- 'local', 'external', 'database'
    external_uri TEXT,
    content TEXT,  -- For text-based artifacts
    version INTEGER DEFAULT 1,
    metadata JSONB,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_artifact_title ON artifact(title);
CREATE INDEX IF NOT EXISTS idx_artifact_project ON artifact(project_id);

-- Design Items
CREATE TABLE IF NOT EXISTS design_item (
    id SERIAL PRIMARY KEY,
    code TEXT,
    discipline TEXT,  -- 'system', 'software', 'hardware', 'structure', 'aerodynamic', etc.
    artifact_id INTEGER REFERENCES artifact(id) ON DELETE CASCADE,
    version INTEGER DEFAULT 1,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_design_item_code ON design_item(code);

-- Software Items (DO-178C)
CREATE TABLE IF NOT EXISTS software_item (
    id SERIAL PRIMARY KEY,
    identifier TEXT NOT NULL,
    dal TEXT,  -- A, B, C, D, E
    type TEXT,  -- 'executable', 'library', 'module', etc.
    version INTEGER DEFAULT 1,
    metadata JSONB,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(identifier, project_id)
);

CREATE INDEX IF NOT EXISTS idx_software_identifier ON software_item(identifier);

CREATE TABLE IF NOT EXISTS software_design (
    id SERIAL PRIMARY KEY,
    software_item_id INTEGER REFERENCES software_item(id) ON DELETE CASCADE,
    design_level TEXT,   -- 'HLR' (High-Level Requirements), 'LLR' (Low-Level Requirements)
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS software_code (
    id SERIAL PRIMARY KEY,
    software_item_id INTEGER REFERENCES software_item(id) ON DELETE CASCADE,
    language TEXT,
    repo_uri TEXT,
    version TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Hardware Items (DO-254)
CREATE TABLE IF NOT EXISTS hardware_item (
    id SERIAL PRIMARY KEY,
    identifier TEXT NOT NULL,
    dal TEXT,  -- A, B, C, D, E
    type TEXT,  -- 'fpga', 'asic', 'circuit', etc.
    version INTEGER DEFAULT 1,
    metadata JSONB,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(identifier, project_id)
);

CREATE INDEX IF NOT EXISTS idx_hardware_identifier ON hardware_item(identifier);

CREATE TABLE IF NOT EXISTS hardware_design (
    id SERIAL PRIMARY KEY,
    hardware_item_id INTEGER REFERENCES hardware_item(id) ON DELETE CASCADE,
    design_level TEXT,
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hardware_implementation (
    id SERIAL PRIMARY KEY,
    hardware_item_id INTEGER REFERENCES hardware_item(id) ON DELETE CASCADE,
    type TEXT,
    version TEXT,
    repo_uri TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Baselines (version snapshots)
CREATE TABLE IF NOT EXISTS baseline (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    baseline_date DATE DEFAULT CURRENT_DATE,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(name, project_id)
);

CREATE INDEX IF NOT EXISTS idx_baseline_name_project ON baseline(name, project_id);

-- Entity Versions (for complete version history)
CREATE TABLE IF NOT EXISTS entity_version (
    id SERIAL PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    version_number INTEGER DEFAULT 1,
    snapshot JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_entity_version_lookup ON entity_version(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_entity_version_created ON entity_version(created_at);

-- Allocations (Requirement → WBS → Responsibility)
CREATE TABLE IF NOT EXISTS allocation (
    id SERIAL PRIMARY KEY,
    requirement_id INTEGER REFERENCES requirements(id) ON DELETE CASCADE,
    wbs_node_id INTEGER REFERENCES wbs_node(id) ON DELETE CASCADE,
    s1000d_resp_id INTEGER REFERENCES s1000d_resp(id) ON DELETE SET NULL,
    allocation_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_allocation_requirement ON allocation(requirement_id);
CREATE INDEX IF NOT EXISTS idx_allocation_wbs ON allocation(wbs_node_id);

-- Verification (Test methods and procedures)
CREATE TABLE IF NOT EXISTS verification (
    id SERIAL PRIMARY KEY,
    code TEXT,
    method TEXT,  -- 'test', 'analysis', 'inspection', 'demonstration'
    method_details TEXT,
    environment TEXT,
    config_baseline_id INTEGER REFERENCES baseline(id) ON DELETE SET NULL,
    testbench_artifact_id INTEGER REFERENCES artifact(id) ON DELETE SET NULL,
    version INTEGER DEFAULT 1,
    result JSONB,
    approval_required BOOLEAN DEFAULT TRUE,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_verification_code_project ON verification(code, project_id);

-- Validation (Requirement validation against verification)
CREATE TABLE IF NOT EXISTS validation (
    id SERIAL PRIMARY KEY,
    requirement_id INTEGER REFERENCES requirements(id) ON DELETE CASCADE,
    verification_id INTEGER REFERENCES verification(id) ON DELETE CASCADE,
    verdict TEXT,  -- 'passed', 'failed', 'conditional', 'not_tested'
    context TEXT,
    acceptance_criteria TEXT,
    verifier_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    verdict_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_validation_requirement ON validation(requirement_id);
CREATE INDEX IF NOT EXISTS idx_validation_verification ON validation(verification_id);

-- Trace Links (Generic traceability between any entities)
CREATE TABLE IF NOT EXISTS tracelink (
    id SERIAL PRIMARY KEY,
    src_type TEXT,  -- 'requirement', 'design_item', 'artifact', etc.
    src_id INTEGER,
    dst_type TEXT,
    dst_id INTEGER,
    link_type TEXT,  -- 'derives_from', 'implements', 'verifies', 'validates', etc.
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tracelink_src ON tracelink(src_type, src_id);
CREATE INDEX IF NOT EXISTS idx_tracelink_dst ON tracelink(dst_type, dst_id);
CREATE INDEX IF NOT EXISTS idx_tracelink_type ON tracelink(link_type);

-- Baseline Items (what's included in each baseline)
CREATE TABLE IF NOT EXISTS baseline_item (
    id SERIAL PRIMARY KEY,
    baseline_id INTEGER REFERENCES baseline(id) ON DELETE CASCADE,
    item_type TEXT,
    item_id INTEGER,
    entity_version_id INTEGER REFERENCES entity_version(id),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_baseline_item_baseline ON baseline_item(baseline_id);

-- Approvals (human approval workflow)
CREATE TABLE IF NOT EXISTS approval (
    id SERIAL PRIMARY KEY,
    entity_type TEXT,
    entity_id INTEGER,
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    verdict TEXT,  -- 'approved', 'rejected', 'conditional', 'pending'
    comments TEXT,
    approved_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_approval_entity ON approval(entity_type, entity_id);

-- Audit Logs (complete audit trail)
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    actor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    actor_type TEXT,  -- 'human' or 'ai_agent'
    action TEXT,  -- 'create', 'update', 'delete', 'approve', etc.
    target_type TEXT,
    target_id INTEGER,
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_actor ON audit_log(actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_target ON audit_log(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created ON audit_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action);

-- Reviews (formal design/code reviews)
CREATE TABLE IF NOT EXISTS review (
    id SERIAL PRIMARY KEY,
    name TEXT,
    type TEXT,  -- 'SRR', 'PDR', 'CDR', 'TRR', 'code_review', etc.
    date DATE,
    conducted_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    notes TEXT,
    status TEXT,  -- 'planned', 'in_progress', 'completed', 'cancelled'
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS review_item (
    id SERIAL PRIMARY KEY,
    review_id INTEGER REFERENCES review(id) ON DELETE CASCADE,
    entity_type TEXT,
    entity_id INTEGER,
    findings TEXT,
    status TEXT,  -- 'open', 'closed', 'deferred'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Coverage (Test coverage for software items - DO-178C requirement)
CREATE TABLE IF NOT EXISTS coverage (
    id SERIAL PRIMARY KEY,
    verification_id INTEGER REFERENCES verification(id) ON DELETE CASCADE,
    software_item_id INTEGER REFERENCES software_item(id) ON DELETE CASCADE,
    type TEXT,  -- 'statement', 'branch', 'mcdc', 'function'
    percentage FLOAT,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_coverage_verification ON coverage(verification_id);
CREATE INDEX IF NOT EXISTS idx_coverage_software ON coverage(software_item_id);

-- Lifecycle Deliverables (SRS, SDD, Test Plans, etc.)
CREATE TABLE IF NOT EXISTS lifecycle_deliverable (
    id SERIAL PRIMARY KEY,
    type TEXT,  -- 'SRS', 'SDD', 'SVP', 'STP', 'SAS', etc.
    title TEXT,
    version TEXT,
    status TEXT,  -- 'draft', 'review', 'approved', 'baseline'
    artifact_id INTEGER REFERENCES artifact(id) ON DELETE SET NULL,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_deliverable_project ON lifecycle_deliverable(project_id);
CREATE INDEX IF NOT EXISTS idx_deliverable_type ON lifecycle_deliverable(type);

-- AI Job Queue (for asynchronous AI processing)
CREATE TABLE IF NOT EXISTS ai_job (
    id SERIAL PRIMARY KEY,
    job_type TEXT,  -- 'create_requirement', 'generate_test', 'update_design', etc.
    payload JSONB,
    status TEXT,  -- 'pending', 'processing', 'completed', 'failed'
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    executed_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_ai_job_status ON ai_job(status);
CREATE INDEX IF NOT EXISTS idx_ai_job_created ON ai_job(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_job_type ON ai_job(job_type);

-- =============================================
-- 5. Add additional indexes on existing tables
-- =============================================

CREATE INDEX IF NOT EXISTS idx_requirements_status ON requirements(status);
CREATE INDEX IF NOT EXISTS idx_requirements_type ON requirements(type);
CREATE INDEX IF NOT EXISTS idx_requirements_level ON requirements(level);
CREATE INDEX IF NOT EXISTS idx_requirements_dal ON requirements(dal);

CREATE INDEX IF NOT EXISTS idx_projects_code ON projects(code);

-- =============================================
-- 6. Add helpful views
-- =============================================

-- View: Complete Requirement Traceability
CREATE OR REPLACE VIEW v_requirement_traceability AS
SELECT
    r.id,
    r.requirement_id,
    r.title,
    r.level,
    r.discipline,
    r.dal,
    r.status,
    p.name as project_name,
    COUNT(DISTINCT tl.id) as trace_count,
    COUNT(DISTINCT v.id) as verification_count,
    COUNT(DISTINCT val.id) as validation_count
FROM requirements r
LEFT JOIN projects p ON r.project_id = p.id
LEFT JOIN tracelink tl ON tl.src_type = 'requirement' AND tl.src_id = r.id
LEFT JOIN verification v ON v.project_id = r.project_id
LEFT JOIN validation val ON val.requirement_id = r.id
GROUP BY r.id, r.requirement_id, r.title, r.level, r.discipline, r.dal, r.status, p.name;

-- View: Software Items with Coverage
CREATE OR REPLACE VIEW v_software_coverage AS
SELECT
    si.id,
    si.identifier,
    si.dal,
    si.version,
    p.name as project_name,
    AVG(c.percentage) as avg_coverage,
    COUNT(DISTINCT c.id) as coverage_records
FROM software_item si
LEFT JOIN projects p ON si.project_id = p.id
LEFT JOIN coverage c ON c.software_item_id = si.id
GROUP BY si.id, si.identifier, si.dal, si.version, p.name;

COMMIT;

-- =============================================
-- Migration Complete
-- =============================================
-- New tables added: 27
-- Modified tables: 3 (users, projects, requirements)
-- Total tables: ~43
-- New views: 2
-- =============================================
