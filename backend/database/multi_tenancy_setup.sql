-- Multi-Tenancy and Row-Level Security Setup
-- DO-178C Traceability: REQ-DB-067, REQ-DB-068
--
-- This script implements multi-tenancy with row-level security (RLS)
-- for AISET, allowing multiple organizations to use the same database
-- instance with complete data isolation.
--
-- Features:
-- - Organization/tenant management
-- - Row-level security policies
-- - Tenant-scoped queries
-- - Data isolation guarantees

-- Create organizations/tenants table
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    guid UUID DEFAULT gen_random_uuid() NOT NULL UNIQUE,
    org_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    tier VARCHAR(50) DEFAULT 'standard', -- standard, premium, enterprise
    max_users INTEGER DEFAULT 10,
    max_projects INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_organizations_org_code ON organizations(org_code);
CREATE INDEX idx_organizations_status ON organizations(status);

-- Add organization_id to users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id);

CREATE INDEX IF NOT EXISTS idx_users_organization ON users(organization_id);

-- Add organization_id to projects table
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS organization_id INTEGER REFERENCES organizations(id);

CREATE INDEX IF NOT EXISTS idx_projects_organization ON projects(organization_id);

-- Enable Row Level Security on all major tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE requirements ENABLE ROW LEVEL SECURITY;
ALTER TABLE design_components ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE configuration_items ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for users table
-- Users can only see users in their own organization
CREATE POLICY users_org_isolation ON users
    USING (organization_id = current_setting('app.current_org_id')::integer);

-- Create RLS policies for projects table
CREATE POLICY projects_org_isolation ON projects
    USING (organization_id = current_setting('app.current_org_id')::integer);

-- Create RLS policies for requirements table
-- Requirements belong to projects, which belong to organizations
CREATE POLICY requirements_org_isolation ON requirements
    USING (
        project_id IN (
            SELECT id FROM projects
            WHERE organization_id = current_setting('app.current_org_id')::integer
        )
    );

-- Create RLS policies for design_components table
CREATE POLICY design_components_org_isolation ON design_components
    USING (
        project_id IN (
            SELECT id FROM projects
            WHERE organization_id = current_setting('app.current_org_id')::integer
        )
    );

-- Create RLS policies for test_cases table
CREATE POLICY test_cases_org_isolation ON test_cases
    USING (
        project_id IN (
            SELECT id FROM projects
            WHERE organization_id = current_setting('app.current_org_id')::integer
        )
    );

-- Create RLS policies for configuration_items table
CREATE POLICY configuration_items_org_isolation ON configuration_items
    USING (
        project_id IN (
            SELECT id FROM projects
            WHERE organization_id = current_setting('app.current_org_id')::integer
        )
    );

-- Function to set current organization context
CREATE OR REPLACE FUNCTION set_current_organization(org_id integer)
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.current_org_id', org_id::text, false);
END;
$$ LANGUAGE plpgsql;

-- Function to get current organization
CREATE OR REPLACE FUNCTION get_current_organization()
RETURNS integer AS $$
BEGIN
    RETURN current_setting('app.current_org_id', true)::integer;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create organization usage tracking
CREATE TABLE IF NOT EXISTS organization_usage (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    metric_type VARCHAR(100) NOT NULL, -- users, projects, storage_mb, api_calls
    metric_value BIGINT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL
);

CREATE INDEX idx_org_usage_org ON organization_usage(organization_id);
CREATE INDEX idx_org_usage_period ON organization_usage(period_start, period_end);

-- View for current organization usage
CREATE OR REPLACE VIEW organization_usage_summary AS
SELECT
    o.id,
    o.name,
    o.org_code,
    (SELECT COUNT(*) FROM users WHERE organization_id = o.id) as user_count,
    o.max_users,
    (SELECT COUNT(*) FROM projects WHERE organization_id = o.id) as project_count,
    o.max_projects,
    CASE
        WHEN (SELECT COUNT(*) FROM users WHERE organization_id = o.id) >= o.max_users THEN true
        ELSE false
    END as users_at_limit,
    CASE
        WHEN (SELECT COUNT(*) FROM projects WHERE organization_id = o.id) >= o.max_projects THEN true
        ELSE false
    END as projects_at_limit
FROM organizations o
WHERE o.status = 'active';

-- Function to check organization limits
CREATE OR REPLACE FUNCTION check_organization_limit(
    org_id integer,
    limit_type varchar
)
RETURNS boolean AS $$
DECLARE
    current_count integer;
    max_count integer;
BEGIN
    IF limit_type = 'users' THEN
        SELECT COUNT(*) INTO current_count FROM users WHERE organization_id = org_id;
        SELECT max_users INTO max_count FROM organizations WHERE id = org_id;
    ELSIF limit_type = 'projects' THEN
        SELECT COUNT(*) INTO current_count FROM projects WHERE organization_id = org_id;
        SELECT max_projects INTO max_count FROM organizations WHERE id = org_id;
    ELSE
        RETURN false;
    END IF;

    RETURN current_count < max_count;
END;
$$ LANGUAGE plpgsql;

-- Create tenant isolation audit log
CREATE TABLE IF NOT EXISTS tenant_audit_log (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id),
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tenant_audit_org ON tenant_audit_log(organization_id);
CREATE INDEX idx_tenant_audit_action ON tenant_audit_log(action);
CREATE INDEX idx_tenant_audit_timestamp ON tenant_audit_log(created_at);

-- Trigger function for tenant audit logging
CREATE OR REPLACE FUNCTION log_tenant_change()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO tenant_audit_log (
        organization_id,
        action,
        table_name,
        record_id,
        old_values,
        new_values
    ) VALUES (
        COALESCE(get_current_organization(), NEW.organization_id),
        TG_OP,
        TG_TABLE_NAME,
        NEW.id,
        CASE WHEN TG_OP = 'UPDATE' THEN row_to_json(OLD) ELSE NULL END,
        row_to_json(NEW)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Example: Create demo organizations
INSERT INTO organizations (org_code, name, tier, max_users, max_projects)
VALUES
    ('DEMO-001', 'Demo Organization 1', 'standard', 10, 5),
    ('DEMO-002', 'Demo Organization 2', 'premium', 50, 20),
    ('DEMO-003', 'Demo Organization 3', 'enterprise', 200, 100)
ON CONFLICT (org_code) DO NOTHING;

-- Helper function to create organization
CREATE OR REPLACE FUNCTION create_organization(
    p_org_code VARCHAR(50),
    p_name VARCHAR(255),
    p_tier VARCHAR(50) DEFAULT 'standard'
)
RETURNS integer AS $$
DECLARE
    v_org_id integer;
    v_max_users integer;
    v_max_projects integer;
BEGIN
    -- Set limits based on tier
    CASE p_tier
        WHEN 'standard' THEN
            v_max_users := 10;
            v_max_projects := 5;
        WHEN 'premium' THEN
            v_max_users := 50;
            v_max_projects := 20;
        WHEN 'enterprise' THEN
            v_max_users := 200;
            v_max_projects := 100;
        ELSE
            v_max_users := 10;
            v_max_projects := 5;
    END CASE;

    INSERT INTO organizations (org_code, name, tier, max_users, max_projects)
    VALUES (p_org_code, p_name, p_tier, v_max_users, v_max_projects)
    RETURNING id INTO v_org_id;

    RETURN v_org_id;
END;
$$ LANGUAGE plpgsql;

-- Usage examples:
-- Set organization context: SELECT set_current_organization(1);
-- Create organization: SELECT create_organization('ACME-001', 'Acme Corporation', 'enterprise');
-- Check limit: SELECT check_organization_limit(1, 'users');
