-- =============================================
-- PostgreSQL Migration Script
-- ARP4754 / DO-178C / DO-254 Compliance Schema
-- Date: 2025-11-14
-- Author: AISET Development Team
-- =============================================

-- This migration adds tables required for full ARP4754/DO-178C/DO-254 compliance
-- while preserving existing tables from the MVP

BEGIN;

-- =============================================
-- 1. Rename 'users' to 'user' (SQL requirement compliance)
-- =============================================
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'users') THEN
        ALTER TABLE users RENAME TO "user";
    END IF;
END $$;

-- =============================================
-- 2. Modify existing 'project' table if needed
-- =============================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'project') THEN
        ALTER TABLE projects RENAME TO project;
    END IF;

    -- Add 'code' column if it doesn't exist
    IF NOT EXISTS (SELECT FROM information_schema.columns
                   WHERE table_name='project' AND column_name='code') THEN
        ALTER TABLE project ADD COLUMN code TEXT;
        -- Generate codes for existing projects
        UPDATE project SET code = 'PROJ-' || SUBSTRING(CAST(id AS TEXT), 1, 8) WHERE code IS NULL;
        ALTER TABLE project ALTER COLUMN code SET NOT NULL;
        CREATE UNIQUE INDEX idx_project_code ON project(code);
    END IF;
END $$;

-- =============================================
-- 3. Modify existing 'requirement' table
-- =============================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'requirement') THEN
        ALTER TABLE requirements RENAME TO requirement;
    END IF;

    -- Add new columns if they don't exist
    IF NOT EXISTS (SELECT FROM information_schema.columns
                   WHERE table_name='requirement' AND column_name='level') THEN
        ALTER TABLE requirement ADD COLUMN level TEXT DEFAULT 'system';
    END IF;

    IF NOT EXISTS (SELECT FROM information_schema.columns
                   WHERE table_name='requirement' AND column_name='discipline') THEN
        ALTER TABLE requirement ADD COLUMN discipline TEXT;
    END IF;

    IF NOT EXISTS (SELECT FROM information_schema.columns
                   WHERE table_name='requirement' AND column_name='origin') THEN
        ALTER TABLE requirement ADD COLUMN origin TEXT;
    END IF;

    IF NOT EXISTS (SELECT FROM information_schema.columns
                   WHERE table_name='requirement' AND column_name='dal') THEN
        ALTER TABLE requirement ADD COLUMN dal TEXT;
    END IF;

    IF NOT EXISTS (SELECT FROM information_schema.columns
                   WHERE table_name='requirement' AND column_name='version') THEN
        ALTER TABLE requirement ADD COLUMN version INT DEFAULT 1;
    END IF;

    IF NOT EXISTS (SELECT FROM information_schema.columns
                   WHERE table_name='requirement' AND column_name='metadata') THEN
        ALTER TABLE requirement ADD COLUMN metadata JSONB;
    END IF;

    IF NOT EXISTS (SELECT FROM information_schema.columns
                   WHERE table_name='requirement' AND column_name='approval_required') THEN
        ALTER TABLE requirement ADD COLUMN approval_required BOOLEAN DEFAULT TRUE;
    END IF;

    -- Rename 'requirement_id' to 'req_id' if exists
    IF EXISTS (SELECT FROM information_schema.columns
               WHERE table_name='requirement' AND column_name='requirement_id')
       AND NOT EXISTS (SELECT FROM information_schema.columns
                       WHERE table_name='requirement' AND column_name='req_id') THEN
        ALTER TABLE requirement RENAME COLUMN requirement_id TO req_id;
    END IF;
END $$;

-- =============================================
-- 4. Create NEW TABLES (only if they don't exist)
-- =============================================

-- Requirement Types
CREATE TABLE IF NOT EXISTS requirement_type (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT
);

-- Insert default requirement types
INSERT INTO requirement_type (code, name)
VALUES
    ('FUNC', 'Functional Requirement'),
    ('PERF', 'Performance Requirement'),
    ('SAFE', 'Safety Requirement'),
    ('SEC', 'Security Requirement'),
    ('INTF', 'Interface Requirement')
ON CONFLICT (code) DO NOTHING;

-- Requirement Derivation
CREATE TABLE IF NOT EXISTS requirement_derivation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_req_id UUID REFERENCES requirement(id) ON DELETE CASCADE,
    child_req_id UUID REFERENCES requirement(id) ON DELETE CASCADE,
    rationale TEXT,
    UNIQUE (parent_req_id, child_req_id)
);

-- WBS Nodes (Work Breakdown Structure - MIL-STD-881)
CREATE TABLE IF NOT EXISTS wbs_node (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT NOT NULL,
    title TEXT,
    parent_id UUID REFERENCES wbs_node(id) ON DELETE CASCADE,
    metadata JSONB,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_wbs_code_project ON wbs_node(code, project_id);

-- S1000D Responsibility
CREATE TABLE IF NOT EXISTS s1000d_resp (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dm_id TEXT,
    role TEXT,
    role_code TEXT,
    organization TEXT,
    contact_user_id UUID REFERENCES "user"(id) ON DELETE SET NULL,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE
);

-- Artifacts (documents, models, code, etc.)
CREATE TABLE IF NOT EXISTS artifact (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    kind TEXT,
    storage_type TEXT,
    external_uri TEXT,
    version INT DEFAULT 1,
    metadata JSONB,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_artifact_title ON artifact(title);
CREATE INDEX IF NOT EXISTS idx_artifact_project ON artifact(project_id);

-- Design Items
CREATE TABLE IF NOT EXISTS design_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT,
    discipline TEXT,
    artifact_id UUID REFERENCES artifact(id) ON DELETE CASCADE,
    version INT DEFAULT 1,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_design_item_code ON design_item(code);

-- Software Items (DO-178C)
CREATE TABLE IF NOT EXISTS software_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identifier TEXT NOT NULL,
    dal TEXT,
    type TEXT,
    version INT DEFAULT 1,
    metadata JSONB,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE,
    UNIQUE(identifier, project_id)
);

CREATE INDEX IF NOT EXISTS idx_software_identifier ON software_item(identifier);

CREATE TABLE IF NOT EXISTS software_design (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    software_item_id UUID REFERENCES software_item(id) ON DELETE CASCADE,
    design_level TEXT,   -- HLR (High-Level Requirements), LLR (Low-Level Requirements)
    description TEXT,
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS software_code (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    software_item_id UUID REFERENCES software_item(id) ON DELETE CASCADE,
    language TEXT,
    repo_uri TEXT,
    version TEXT,
    metadata JSONB
);

-- Hardware Items (DO-254)
CREATE TABLE IF NOT EXISTS hardware_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identifier TEXT NOT NULL,
    dal TEXT,
    type TEXT,
    version INT DEFAULT 1,
    metadata JSONB,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE,
    UNIQUE(identifier, project_id)
);

CREATE INDEX IF NOT EXISTS idx_hardware_identifier ON hardware_item(identifier);

CREATE TABLE IF NOT EXISTS hardware_design (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hardware_item_id UUID REFERENCES hardware_item(id) ON DELETE CASCADE,
    design_level TEXT,
    description TEXT,
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS hardware_implementation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hardware_item_id UUID REFERENCES hardware_item(id) ON DELETE CASCADE,
    type TEXT,
    version TEXT,
    repo_uri TEXT,
    metadata JSONB
);

-- Baselines
CREATE TABLE IF NOT EXISTS baseline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    project_id UUID REFERENCES project(id) ON DELETE CASCADE,
    UNIQUE(name, project_id)
);

CREATE INDEX IF NOT EXISTS idx_baseline_name_project ON baseline(name, project_id);

-- Entity Versions (for version control)
CREATE TABLE IF NOT EXISTS entity_version (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    version_number INT DEFAULT 1,
    snapshot JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES "user"(id)
);

CREATE INDEX IF NOT EXISTS idx_entity_version_lookup ON entity_version(entity_type, entity_id);

-- Allocations (Requirement → WBS → Responsibility)
CREATE TABLE IF NOT EXISTS allocation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID REFERENCES requirement(id) ON DELETE CASCADE,
    wbs_node_id UUID REFERENCES wbs_node(id) ON DELETE CASCADE,
    s1000d_resp_id UUID REFERENCES s1000d_resp(id) ON DELETE SET NULL,
    allocation_type TEXT
);

-- Verification (Test methods and procedures)
CREATE TABLE IF NOT EXISTS verification (
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
    project_id UUID REFERENCES project(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_verification_code_project ON verification(code, project_id);

-- Validation (Requirement validation against verification)
CREATE TABLE IF NOT EXISTS validation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID REFERENCES requirement(id) ON DELETE CASCADE,
    verification_id UUID REFERENCES verification(id) ON DELETE CASCADE,
    verdict TEXT,
    context TEXT,
    acceptance_criteria TEXT,
    verifier_user_id UUID REFERENCES "user"(id) ON DELETE SET NULL,
    verdict_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trace Links (Generic traceability)
CREATE TABLE IF NOT EXISTS tracelink (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    src_type TEXT,
    src_id UUID,
    dst_type TEXT,
    dst_id UUID,
    link_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tracelink_src ON tracelink(src_type, src_id);
CREATE INDEX IF NOT EXISTS idx_tracelink_dst ON tracelink(dst_type, dst_id);

-- Baseline Items
CREATE TABLE IF NOT EXISTS baseline_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    baseline_id UUID REFERENCES baseline(id) ON DELETE CASCADE,
    item_type TEXT,
    item_id UUID,
    entity_version_id UUID REFERENCES entity_version(id),
    metadata JSONB
);

-- Change Requests
CREATE TABLE IF NOT EXISTS change_request (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cr_id TEXT NOT NULL,
    title TEXT,
    description TEXT,
    status TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    project_id UUID REFERENCES project(id) ON DELETE CASCADE,
    UNIQUE(cr_id, project_id)
);

-- Approvals
CREATE TABLE IF NOT EXISTS approval (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT,
    entity_id UUID,
    approved_by UUID REFERENCES "user"(id) ON DELETE SET NULL,
    verdict TEXT,
    comments TEXT,
    approved_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Logs
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    actor_id UUID REFERENCES "user"(id) ON DELETE SET NULL,
    actor_type TEXT, -- 'human' or 'ai_agent'
    action TEXT,
    target_type TEXT,
    target_id UUID,
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_actor ON audit_log(actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_target ON audit_log(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created ON audit_log(created_at);

-- Reviews
CREATE TABLE IF NOT EXISTS review (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT,
    type TEXT,
    date DATE,
    conducted_by UUID REFERENCES "user"(id) ON DELETE SET NULL,
    notes TEXT,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS review_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID REFERENCES review(id) ON DELETE CASCADE,
    entity_type TEXT,
    entity_id UUID,
    findings TEXT,
    status TEXT
);

-- Coverage (Test coverage for software items)
CREATE TABLE IF NOT EXISTS coverage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    verification_id UUID REFERENCES verification(id) ON DELETE CASCADE,
    software_item_id UUID REFERENCES software_item(id) ON DELETE CASCADE,
    type TEXT,
    percentage FLOAT,
    details JSONB
);

-- Lifecycle Deliverables
CREATE TABLE IF NOT EXISTS lifecycle_deliverable (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT,
    title TEXT,
    version TEXT,
    status TEXT,
    project_id UUID REFERENCES project(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI Job Queue
CREATE TABLE IF NOT EXISTS ai_job (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type TEXT,
    payload JSONB,
    status TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    executed_by UUID REFERENCES "user"(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_ai_job_status ON ai_job(status);
CREATE INDEX IF NOT EXISTS idx_ai_job_created ON ai_job(created_at);

-- =============================================
-- 5. Add missing indexes on existing tables
-- =============================================

CREATE INDEX IF NOT EXISTS idx_requirement_req_id ON requirement(req_id);
CREATE INDEX IF NOT EXISTS idx_requirement_project_id ON requirement(project_id);
CREATE INDEX IF NOT EXISTS idx_requirement_status ON requirement(status);
CREATE INDEX IF NOT EXISTS idx_requirement_level ON requirement(level);

COMMIT;

-- =============================================
-- Migration Complete
-- =============================================
-- New tables added: 27
-- Modified tables: 3 (user, project, requirement)
-- Total tables: ~43
-- =============================================
