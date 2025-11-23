-- =============================================================================
-- AISET Process Engine Database Schema
-- Version: 1.0.0
-- Date: 2025-11-23
--
-- This schema supports the "Codification of the Systems Engineer" -
-- deterministic state machines for development process execution.
-- =============================================================================

-- =============================================================================
-- PROCESS TEMPLATES
-- =============================================================================

-- Process templates table (stores template metadata, JSON content stored separately)
CREATE TABLE process_templates (
    id SERIAL PRIMARY KEY,
    guid UUID NOT NULL DEFAULT gen_random_uuid(),

    -- Template identification
    template_id VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    standard VARCHAR(50) NOT NULL,  -- ARP4754A, DO-178C, DO-254, GENERIC, etc.
    version VARCHAR(20) NOT NULL,

    -- Template content (full JSON)
    template_json JSONB NOT NULL,

    -- Applicable CI types (denormalized for quick lookup)
    applicable_ci_types VARCHAR(50)[] NOT NULL,

    -- DAL levels this template supports
    dal_levels VARCHAR(20)[] NOT NULL,

    -- Metadata
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by INT REFERENCES users(id),

    -- Unique constraint
    CONSTRAINT uq_process_template UNIQUE (template_id, version)
);

CREATE INDEX idx_process_templates_standard ON process_templates(standard);
CREATE INDEX idx_process_templates_ci_types ON process_templates USING GIN(applicable_ci_types);

-- =============================================================================
-- STATE MACHINE INSTANCES
-- =============================================================================

-- State machine instances for Configuration Items
CREATE TABLE ci_state_machines (
    id SERIAL PRIMARY KEY,
    guid UUID NOT NULL DEFAULT gen_random_uuid(),

    -- Link to CI
    ci_id INT NOT NULL REFERENCES configuration_items(id) ON DELETE CASCADE,
    project_id INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- Template reference
    template_id VARCHAR(100) NOT NULL,
    template_version VARCHAR(20) NOT NULL,

    -- Current state
    current_phase_index INT NOT NULL DEFAULT 0,
    current_sub_phase_index INT NOT NULL DEFAULT 0,
    current_activity_index INT NOT NULL DEFAULT 0,

    -- DAL level for this instance (affects which activities are required)
    dal_level VARCHAR(20),

    -- Full state machine state (JSON)
    state_json JSONB NOT NULL,

    -- Progress metrics (denormalized for quick queries)
    total_phases INT NOT NULL DEFAULT 0,
    completed_phases INT NOT NULL DEFAULT 0,
    total_activities INT NOT NULL DEFAULT 0,
    completed_activities INT NOT NULL DEFAULT 0,
    progress_percent NUMERIC(5,2) NOT NULL DEFAULT 0.00,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'not_started',
    -- Values: not_started, in_progress, completed, blocked, on_hold

    -- Context for conditional logic
    context_json JSONB NOT NULL DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Unique constraint: one state machine per CI
    CONSTRAINT uq_ci_state_machine UNIQUE (ci_id)
);

CREATE INDEX idx_ci_state_machines_project ON ci_state_machines(project_id);
CREATE INDEX idx_ci_state_machines_status ON ci_state_machines(status);
CREATE INDEX idx_ci_state_machines_progress ON ci_state_machines(progress_percent);

-- =============================================================================
-- PHASE INSTANCES
-- =============================================================================

-- Individual phase instances (for detailed tracking and queries)
CREATE TABLE ci_phase_instances (
    id SERIAL PRIMARY KEY,
    guid UUID NOT NULL DEFAULT gen_random_uuid(),

    -- Parent references
    state_machine_id INT NOT NULL REFERENCES ci_state_machines(id) ON DELETE CASCADE,
    ci_id INT NOT NULL REFERENCES configuration_items(id) ON DELETE CASCADE,

    -- Phase identification
    phase_id VARCHAR(100) NOT NULL,
    phase_name VARCHAR(255) NOT NULL,
    phase_order INT NOT NULL,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'not_started',
    -- Values: not_started, in_progress, completed, blocked, skipped

    -- Criteria tracking
    entry_criteria_met BOOLEAN NOT NULL DEFAULT FALSE,
    exit_criteria_met BOOLEAN NOT NULL DEFAULT FALSE,
    entry_criteria_data JSONB,
    exit_criteria_data JSONB,

    -- Progress
    total_sub_phases INT NOT NULL DEFAULT 0,
    completed_sub_phases INT NOT NULL DEFAULT 0,
    total_activities INT NOT NULL DEFAULT 0,
    completed_activities INT NOT NULL DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Unique constraint
    CONSTRAINT uq_ci_phase UNIQUE (state_machine_id, phase_id)
);

CREATE INDEX idx_ci_phase_instances_ci ON ci_phase_instances(ci_id);
CREATE INDEX idx_ci_phase_instances_status ON ci_phase_instances(status);

-- =============================================================================
-- ACTIVITY INSTANCES
-- =============================================================================

-- Individual activity instances (the most granular tracking level)
CREATE TABLE ci_activity_instances (
    id SERIAL PRIMARY KEY,
    guid UUID NOT NULL DEFAULT gen_random_uuid(),

    -- Parent references
    state_machine_id INT NOT NULL REFERENCES ci_state_machines(id) ON DELETE CASCADE,
    phase_instance_id INT NOT NULL REFERENCES ci_phase_instances(id) ON DELETE CASCADE,
    ci_id INT NOT NULL REFERENCES configuration_items(id) ON DELETE CASCADE,

    -- Activity identification
    activity_id VARCHAR(100) NOT NULL,
    activity_name VARCHAR(255) NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    -- Types: INTERVIEW, DOCUMENT_CREATION, DOCUMENT_REVIEW, ANALYSIS, DESIGN,
    --        IMPLEMENTATION, TEST, VERIFICATION, VALIDATION, APPROVAL, BASELINE, AUDIT

    -- Sub-phase info
    sub_phase_id VARCHAR(100) NOT NULL,
    sub_phase_order INT NOT NULL,
    activity_order INT NOT NULL,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'not_started',
    -- Values: not_started, in_progress, completed, skipped, blocked

    -- Required flag
    is_required BOOLEAN NOT NULL DEFAULT TRUE,

    -- Output artifacts (references to documents, etc.)
    output_artifact_types VARCHAR(100)[] DEFAULT '{}',
    output_artifact_ids INT[] DEFAULT '{}',  -- References to actual artifacts

    -- Completion data (captured data, interview answers, etc.)
    completion_data JSONB,

    -- Skip reason (if skipped)
    skip_reason TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- User who completed
    completed_by INT REFERENCES users(id),

    -- Unique constraint
    CONSTRAINT uq_ci_activity UNIQUE (state_machine_id, activity_id)
);

CREATE INDEX idx_ci_activity_instances_ci ON ci_activity_instances(ci_id);
CREATE INDEX idx_ci_activity_instances_phase ON ci_activity_instances(phase_instance_id);
CREATE INDEX idx_ci_activity_instances_status ON ci_activity_instances(status);
CREATE INDEX idx_ci_activity_instances_type ON ci_activity_instances(activity_type);

-- =============================================================================
-- INTERVIEW ANSWERS
-- =============================================================================

-- Captured interview answers (from activities of type INTERVIEW)
CREATE TABLE interview_answers (
    id SERIAL PRIMARY KEY,
    guid UUID NOT NULL DEFAULT gen_random_uuid(),

    -- Context
    project_id INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    ci_id INT REFERENCES configuration_items(id) ON DELETE CASCADE,
    activity_instance_id INT REFERENCES ci_activity_instances(id) ON DELETE SET NULL,

    -- Question info
    question_id VARCHAR(100) NOT NULL,
    question_text TEXT NOT NULL,
    question_variant_used TEXT,  -- Which variant of the question was displayed

    -- Phase/sub-phase context
    phase_id VARCHAR(100),
    sub_phase_id VARCHAR(100),

    -- Answer info
    answer_raw TEXT NOT NULL,
    answer_transformed JSONB,  -- Transformed/structured data

    -- Storage mapping
    target_table VARCHAR(100),
    target_column VARCHAR(100),
    target_record_id INT,
    storage_successful BOOLEAN NOT NULL DEFAULT FALSE,

    -- Validation
    validation_passed BOOLEAN NOT NULL DEFAULT TRUE,
    validation_errors JSONB,

    -- NLP interpretation (if AI was used)
    nlp_used BOOLEAN NOT NULL DEFAULT FALSE,
    nlp_interpretation JSONB,
    user_confirmed BOOLEAN NOT NULL DEFAULT TRUE,

    -- Audit
    answered_by INT REFERENCES users(id),
    answered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_interview_answers_project ON interview_answers(project_id);
CREATE INDEX idx_interview_answers_ci ON interview_answers(ci_id);
CREATE INDEX idx_interview_answers_question ON interview_answers(question_id);
CREATE INDEX idx_interview_answers_phase ON interview_answers(phase_id);

-- =============================================================================
-- GENERATED DOCUMENTS
-- =============================================================================

-- Documents generated from templates
CREATE TABLE generated_documents (
    id SERIAL PRIMARY KEY,
    guid UUID NOT NULL DEFAULT gen_random_uuid(),

    -- Context
    project_id INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    ci_id INT REFERENCES configuration_items(id) ON DELETE SET NULL,

    -- Document info
    document_type VARCHAR(50) NOT NULL,
    -- Types: SRS, HLD, LLD, RTM, TEST_PLAN, TEST_REPORT, SAFETY_ASSESSMENT, etc.

    title VARCHAR(500) NOT NULL,
    version INT NOT NULL DEFAULT 1,

    -- Content
    content TEXT NOT NULL,
    content_format VARCHAR(20) NOT NULL DEFAULT 'markdown',
    -- Formats: markdown, html, json

    -- Generation info
    template_id VARCHAR(100),
    template_version VARCHAR(20),
    source_data_hash VARCHAR(64),  -- To detect if regeneration needed

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    -- Values: draft, needs_review, reviewed, approved, obsolete

    -- Timestamps
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    approved_at TIMESTAMP WITH TIME ZONE,

    -- Users
    generated_by INT REFERENCES users(id),
    reviewed_by INT REFERENCES users(id),
    approved_by INT REFERENCES users(id),

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_generated_documents_project ON generated_documents(project_id);
CREATE INDEX idx_generated_documents_type ON generated_documents(document_type);
CREATE INDEX idx_generated_documents_status ON generated_documents(status);

-- Document versions history
CREATE TABLE generated_document_history (
    id SERIAL PRIMARY KEY,
    document_id INT NOT NULL REFERENCES generated_documents(id) ON DELETE CASCADE,
    version INT NOT NULL,
    content TEXT NOT NULL,
    change_summary TEXT,
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    changed_by INT REFERENCES users(id)
);

CREATE INDEX idx_gen_doc_history_doc ON generated_document_history(document_id);

-- =============================================================================
-- DELIVERABLES TRACKING
-- =============================================================================

-- Track deliverables required by phases
CREATE TABLE phase_deliverables (
    id SERIAL PRIMARY KEY,
    guid UUID NOT NULL DEFAULT gen_random_uuid(),

    -- Context
    phase_instance_id INT NOT NULL REFERENCES ci_phase_instances(id) ON DELETE CASCADE,
    ci_id INT NOT NULL REFERENCES configuration_items(id) ON DELETE CASCADE,

    -- Deliverable info from template
    deliverable_id VARCHAR(100) NOT NULL,
    deliverable_name VARCHAR(255) NOT NULL,
    artifact_type VARCHAR(50) NOT NULL,
    is_required BOOLEAN NOT NULL DEFAULT TRUE,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- Values: pending, in_progress, completed, waived

    -- Link to actual artifact
    artifact_id INT,  -- Generic reference to various artifact tables
    artifact_table VARCHAR(100),  -- Which table the artifact is in

    -- Link to generated document (if applicable)
    generated_document_id INT REFERENCES generated_documents(id),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT uq_phase_deliverable UNIQUE (phase_instance_id, deliverable_id)
);

CREATE INDEX idx_phase_deliverables_ci ON phase_deliverables(ci_id);
CREATE INDEX idx_phase_deliverables_status ON phase_deliverables(status);

-- =============================================================================
-- REVIEW TRACKING
-- =============================================================================

-- Track reviews required by phases
CREATE TABLE phase_reviews (
    id SERIAL PRIMARY KEY,
    guid UUID NOT NULL DEFAULT gen_random_uuid(),

    -- Context
    phase_instance_id INT NOT NULL REFERENCES ci_phase_instances(id) ON DELETE CASCADE,
    ci_id INT NOT NULL REFERENCES configuration_items(id) ON DELETE CASCADE,

    -- Review info from template
    review_id VARCHAR(100) NOT NULL,
    review_name VARCHAR(255) NOT NULL,
    review_type VARCHAR(50) NOT NULL,
    -- Types: SRR, SDR, PDR, CDR, TRR, PRR, FCA, PCA, GATE_REVIEW, PEER_REVIEW, MANAGEMENT_REVIEW

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    -- Values: pending, scheduled, in_progress, passed, failed, waived

    -- Schedule
    scheduled_date DATE,
    actual_date DATE,

    -- Result
    result VARCHAR(20),  -- passed, passed_with_comments, failed
    comments TEXT,

    -- Attendees
    required_attendees VARCHAR(100)[],
    actual_attendees INT[],  -- User IDs

    -- Review record
    review_record_id INT,  -- Link to review record document

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT uq_phase_review UNIQUE (phase_instance_id, review_id)
);

CREATE INDEX idx_phase_reviews_ci ON phase_reviews(ci_id);
CREATE INDEX idx_phase_reviews_status ON phase_reviews(status);
CREATE INDEX idx_phase_reviews_type ON phase_reviews(review_type);

-- =============================================================================
-- STATE MACHINE HISTORY (AUDIT TRAIL)
-- =============================================================================

-- History of state changes for audit trail
CREATE TABLE state_machine_history (
    id SERIAL PRIMARY KEY,
    guid UUID NOT NULL DEFAULT gen_random_uuid(),

    -- Context
    state_machine_id INT NOT NULL REFERENCES ci_state_machines(id) ON DELETE CASCADE,
    ci_id INT NOT NULL REFERENCES configuration_items(id) ON DELETE CASCADE,

    -- Change info
    change_type VARCHAR(50) NOT NULL,
    -- Types: PHASE_STARTED, PHASE_COMPLETED, ACTIVITY_STARTED, ACTIVITY_COMPLETED,
    --        ACTIVITY_SKIPPED, ROLLBACK, STATUS_CHANGE

    -- What changed
    from_phase VARCHAR(100),
    to_phase VARCHAR(100),
    from_status VARCHAR(50),
    to_status VARCHAR(50),
    activity_id VARCHAR(100),

    -- Snapshot of state at time of change
    state_snapshot JSONB,

    -- User and timestamp
    changed_by INT REFERENCES users(id),
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Reason (especially for rollbacks)
    change_reason TEXT
);

CREATE INDEX idx_sm_history_state_machine ON state_machine_history(state_machine_id);
CREATE INDEX idx_sm_history_ci ON state_machine_history(ci_id);
CREATE INDEX idx_sm_history_type ON state_machine_history(change_type);
CREATE INDEX idx_sm_history_date ON state_machine_history(changed_at);

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- View: Current phase status for all CIs in a project
CREATE OR REPLACE VIEW v_project_ci_phases AS
SELECT
    p.id AS project_id,
    p.name AS project_name,
    ci.id AS ci_id,
    ci.display_id AS ci_display_id,
    ci.name AS ci_name,
    ci.ci_type,
    sm.status AS state_machine_status,
    sm.progress_percent,
    ph.phase_id,
    ph.phase_name,
    ph.phase_order,
    ph.status AS phase_status,
    ph.started_at AS phase_started_at,
    ph.completed_at AS phase_completed_at
FROM
    projects p
    JOIN configuration_items ci ON ci.project_id = p.id
    LEFT JOIN ci_state_machines sm ON sm.ci_id = ci.id
    LEFT JOIN ci_phase_instances ph ON ph.state_machine_id = sm.id
ORDER BY
    p.id, ci.id, ph.phase_order;

-- View: Activity completion summary by project
CREATE OR REPLACE VIEW v_project_activity_summary AS
SELECT
    p.id AS project_id,
    p.name AS project_name,
    COUNT(DISTINCT ci.id) AS total_cis,
    COUNT(DISTINCT sm.id) AS cis_with_state_machines,
    COUNT(act.id) AS total_activities,
    SUM(CASE WHEN act.status = 'completed' THEN 1 ELSE 0 END) AS completed_activities,
    SUM(CASE WHEN act.status = 'in_progress' THEN 1 ELSE 0 END) AS in_progress_activities,
    SUM(CASE WHEN act.status = 'not_started' THEN 1 ELSE 0 END) AS not_started_activities,
    ROUND(
        SUM(CASE WHEN act.status = 'completed' THEN 1 ELSE 0 END)::NUMERIC /
        NULLIF(COUNT(act.id), 0) * 100, 2
    ) AS completion_percent
FROM
    projects p
    LEFT JOIN configuration_items ci ON ci.project_id = p.id
    LEFT JOIN ci_state_machines sm ON sm.ci_id = ci.id
    LEFT JOIN ci_activity_instances act ON act.state_machine_id = sm.id
GROUP BY
    p.id, p.name;

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to relevant tables
CREATE TRIGGER trg_ci_state_machines_updated
    BEFORE UPDATE ON ci_state_machines
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_ci_phase_instances_updated
    BEFORE UPDATE ON ci_phase_instances
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_ci_activity_instances_updated
    BEFORE UPDATE ON ci_activity_instances
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_generated_documents_updated
    BEFORE UPDATE ON generated_documents
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_phase_deliverables_updated
    BEFORE UPDATE ON phase_deliverables
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_phase_reviews_updated
    BEFORE UPDATE ON phase_reviews
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- =============================================================================
-- COMMENTS
-- =============================================================================

COMMENT ON TABLE process_templates IS 'Stores process templates (ARP4754A, DO-178C, etc.) as JSON';
COMMENT ON TABLE ci_state_machines IS 'State machine instances for each Configuration Item';
COMMENT ON TABLE ci_phase_instances IS 'Individual phase tracking within a state machine';
COMMENT ON TABLE ci_activity_instances IS 'Granular activity tracking (the work items)';
COMMENT ON TABLE interview_answers IS 'Captured data from interview activities';
COMMENT ON TABLE generated_documents IS 'Documents generated from templates';
COMMENT ON TABLE phase_deliverables IS 'Tracks required deliverables for each phase';
COMMENT ON TABLE phase_reviews IS 'Tracks required reviews/gates for each phase';
COMMENT ON TABLE state_machine_history IS 'Audit trail of all state changes';

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
