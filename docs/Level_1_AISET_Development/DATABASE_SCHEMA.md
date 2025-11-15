# AISET Database Schema
## Complete ARP4754 / DO-178C / DO-254 Compliance

**Version:** 2.0
**Date:** 2025-11-14
**Total Tables:** 42
**Migration:** 002_add_compliance_schema_v2.sql

---

## 📊 Overview

This database schema supports full compliance with:
- **ARP4754A** - Development of Civil Aircraft and Systems
- **DO-178C** - Software Considerations in Airborne Systems
- **DO-254** - Design Assurance Guidance for Airborne Electronic Hardware
- **MIL-STD-881** - Work Breakdown Structures
- **S1000D** - International Specification for Technical Publications

---

## 📋 Table Categories

### Core Project Management (3 tables)
1. **projects** - Project definitions
2. **users** - Human and AI users
3. **ai_job** - AI task queue

### Requirements Management (6 tables)
4. **requirements** - All project requirements (system/software/hardware)
5. **requirement_type** - Requirement classification
6. **requirement_derivation** - Parent-child requirement relationships
7. **ai_extracted_entities** - AI-proposed requirements pending validation
8. **validation_decisions** - Human approval/rejection of AI proposals
9. **ai_conversations** - Conversational AI sessions
10. **ai_messages** - Individual messages in AI conversations

### Work Breakdown & Responsibility (2 tables)
11. **wbs_node** - Work Breakdown Structure (MIL-STD-881)
12. **s1000d_resp** - S1000D responsibility allocation

### Allocation (1 table)
13. **allocation** - Links requirements → WBS → responsibilities

### Artifacts & Design (4 tables)
14. **artifact** - All artifacts (documents, models, 3D files, code)
15. **design_item** - Design elements
16. **design_components** - Legacy design components
17. **document_exports** - Generated documents

### Software Items (DO-178C) (3 tables)
18. **software_item** - Software items with DAL levels
19. **software_design** - HLR/LLR design data
20. **software_code** - Source code references

### Hardware Items (DO-254) (3 tables)
21. **hardware_item** - Hardware items with DAL levels
22. **hardware_design** - Hardware design data
23. **hardware_implementation** - HDL/schematics

### Verification & Validation (4 tables)
24. **verification** - Test methods and procedures
25. **validation** - Requirement validation against tests
26. **test_cases** - Test case definitions
27. **coverage** - Test coverage metrics (DO-178C requirement)

### Traceability (5 tables)
28. **tracelink** - Generic bidirectional traceability
29. **requirements_design_trace** - Requirements ↔ Design
30. **requirements_test_trace** - Requirements ↔ Tests
31. **design_test_trace** - Design ↔ Tests
32. **traceability_gaps** - Missing traceability detection

### Configuration Management (5 tables)
33. **baseline** - Version baselines
34. **baseline_item** - Items included in baselines
35. **entity_version** - Complete version history
36. **version_history** - Legacy version tracking
37. **change_requests** - Change request management

### Quality Assurance (4 tables)
38. **approval** - Human approval workflow
39. **audit_log** - Complete audit trail (human + AI actions)
40. **review** - Formal reviews (SRR, PDR, CDR, etc.)
41. **review_item** - Items under review

### Lifecycle Deliverables (1 table)
42. **lifecycle_deliverable** - SRS, SDD, SVP, STP, SAS, etc.

---

## 🔗 Key Relationships

### End-to-End Traceability Chain
```
REQUIREMENT → ALLOCATION → WBS_NODE → S1000D_RESP
            ↓
            TRACELINK → DESIGN_ITEM → ARTIFACT
            ↓
            TRACELINK → VERIFICATION → VALIDATION
            ↓
            COVERAGE (for software)
            ↓
            BASELINE → BASELINE_ITEM → ENTITY_VERSION
```

### Software Development Flow (DO-178C)
```
REQUIREMENT (software, dal=A-E)
    ↓
SOFTWARE_ITEM
    ↓
SOFTWARE_DESIGN (HLR/LLR)
    ↓
SOFTWARE_CODE
    ↓
VERIFICATION (unit/integration/system tests)
    ↓
COVERAGE (statement/branch/MC/DC)
    ↓
VALIDATION (requirement verification)
```

### Hardware Development Flow (DO-254)
```
REQUIREMENT (hardware, dal=A-E)
    ↓
HARDWARE_ITEM
    ↓
HARDWARE_DESIGN
    ↓
HARDWARE_IMPLEMENTATION (HDL/schematic)
    ↓
VERIFICATION
    ↓
VALIDATION
```

---

## 📚 Table Details

### 1. projects
```sql
id              SERIAL PRIMARY KEY
code            TEXT NOT NULL UNIQUE
name            TEXT
description     TEXT
created_at      TIMESTAMPTZ
```

### 2. users
```sql
id              SERIAL PRIMARY KEY
username        TEXT UNIQUE
full_name       TEXT
email           TEXT UNIQUE
role            TEXT  -- 'human' or 'ai_agent'
hashed_password TEXT
```

### 3. requirements
```sql
id                  SERIAL PRIMARY KEY
project_id          INTEGER FK → projects
requirement_id      TEXT UNIQUE
title               TEXT
description         TEXT
type                ENUM (functional, non_functional, constraint, interface)
priority            ENUM (critical, high, medium, low)
status              ENUM (draft, review, approved, implemented, verified)
level               TEXT  -- 'system', 'software', 'hardware'
discipline          TEXT  -- 'aerodynamic', 'structure', 'eme', etc.
origin              TEXT
dal                 TEXT  -- 'A', 'B', 'C', 'D', 'E' (for SW/HW)
version_number      INTEGER
metadata            JSONB
approval_required   BOOLEAN
parent_id           INTEGER FK → requirements
created_at          TIMESTAMPTZ
```

### 4. requirement_type
```sql
id          SERIAL PRIMARY KEY
code        TEXT UNIQUE  -- 'FUNC', 'PERF', 'SAFE', etc.
name        TEXT
description TEXT
```

**Default Types:**
- FUNC - Functional Requirement
- PERF - Performance Requirement
- SAFE - Safety Requirement
- SEC - Security Requirement
- INTF - Interface Requirement
- ENV - Environmental Requirement
- REL - Reliability Requirement

### 5. requirement_derivation
```sql
id              SERIAL PRIMARY KEY
parent_req_id   INTEGER FK → requirements
child_req_id    INTEGER FK → requirements
rationale       TEXT
created_at      TIMESTAMPTZ
```

### 6. wbs_node (MIL-STD-881)
```sql
id          SERIAL PRIMARY KEY
code        TEXT  -- e.g., '1.2.3.4'
title       TEXT
parent_id   INTEGER FK → wbs_node (self-reference)
metadata    JSONB
project_id  INTEGER FK → projects
created_at  TIMESTAMPTZ
```

### 7. s1000d_resp (S1000D Responsibility)
```sql
id                  SERIAL PRIMARY KEY
dm_id               TEXT  -- Data Module ID
role                TEXT
role_code           TEXT
organization        TEXT
contact_user_id     INTEGER FK → users
project_id          INTEGER FK → projects
created_at          TIMESTAMPTZ
```

### 8. allocation
```sql
id                  SERIAL PRIMARY KEY
requirement_id      INTEGER FK → requirements
wbs_node_id         INTEGER FK → wbs_node
s1000d_resp_id      INTEGER FK → s1000d_resp
allocation_type     TEXT
created_at          TIMESTAMPTZ
```

### 9. artifact
```sql
id              SERIAL PRIMARY KEY
title           TEXT
kind            TEXT  -- 'document', 'model_3d', 'code', 'schema', 'drawing'
storage_type    TEXT  -- 'local', 'external', 'database'
external_uri    TEXT
content         TEXT  -- for text-based artifacts
version         INTEGER
metadata        JSONB
project_id      INTEGER FK → projects
created_at      TIMESTAMPTZ
updated_at      TIMESTAMPTZ
```

### 10. design_item
```sql
id              SERIAL PRIMARY KEY
code            TEXT
discipline      TEXT  -- 'system', 'software', 'hardware', 'structure', etc.
artifact_id     INTEGER FK → artifact
version         INTEGER
metadata        JSONB
created_at      TIMESTAMPTZ
```

### 11. software_item (DO-178C)
```sql
id              SERIAL PRIMARY KEY
identifier      TEXT UNIQUE (per project)
dal             TEXT  -- 'A', 'B', 'C', 'D', 'E'
type            TEXT  -- 'executable', 'library', 'module'
version         INTEGER
metadata        JSONB
project_id      INTEGER FK → projects
created_at      TIMESTAMPTZ
```

### 12. software_design
```sql
id                  SERIAL PRIMARY KEY
software_item_id    INTEGER FK → software_item
design_level        TEXT  -- 'HLR' (High-Level), 'LLR' (Low-Level)
description         TEXT
metadata            JSONB
created_at          TIMESTAMPTZ
```

### 13. software_code
```sql
id                  SERIAL PRIMARY KEY
software_item_id    INTEGER FK → software_item
language            TEXT
repo_uri            TEXT
version             TEXT
metadata            JSONB
created_at          TIMESTAMPTZ
```

### 14. hardware_item (DO-254)
```sql
id              SERIAL PRIMARY KEY
identifier      TEXT UNIQUE (per project)
dal             TEXT  -- 'A', 'B', 'C', 'D', 'E'
type            TEXT  -- 'fpga', 'asic', 'circuit'
version         INTEGER
metadata        JSONB
project_id      INTEGER FK → projects
created_at      TIMESTAMPTZ
```

### 15. hardware_design
```sql
id                  SERIAL PRIMARY KEY
hardware_item_id    INTEGER FK → hardware_item
design_level        TEXT
description         TEXT
metadata            JSONB
created_at          TIMESTAMPTZ
```

### 16. hardware_implementation
```sql
id                  SERIAL PRIMARY KEY
hardware_item_id    INTEGER FK → hardware_item
type                TEXT  -- 'vhdl', 'verilog', 'schematic'
version             TEXT
repo_uri            TEXT
metadata            JSONB
created_at          TIMESTAMPTZ
```

### 17. baseline
```sql
id              SERIAL PRIMARY KEY
name            TEXT UNIQUE (per project)
description     TEXT
baseline_date   DATE
project_id      INTEGER FK → projects
created_at      TIMESTAMPTZ
```

### 18. entity_version
```sql
id              SERIAL PRIMARY KEY
entity_type     TEXT  -- 'requirement', 'design_item', etc.
entity_id       INTEGER
version_number  INTEGER
snapshot        JSONB  -- Full snapshot of entity at this version
created_at      TIMESTAMPTZ
created_by      INTEGER FK → users
```

### 19. baseline_item
```sql
id                  SERIAL PRIMARY KEY
baseline_id         INTEGER FK → baseline
item_type           TEXT
item_id             INTEGER
entity_version_id   INTEGER FK → entity_version
metadata            JSONB
created_at          TIMESTAMPTZ
```

### 20. verification
```sql
id                      SERIAL PRIMARY KEY
code                    TEXT
method                  TEXT  -- 'test', 'analysis', 'inspection', 'demonstration'
method_details          TEXT
environment             TEXT
config_baseline_id      INTEGER FK → baseline
testbench_artifact_id   INTEGER FK → artifact
version                 INTEGER
result                  JSONB
approval_required       BOOLEAN
project_id              INTEGER FK → projects
created_at              TIMESTAMPTZ
```

### 21. validation
```sql
id                      SERIAL PRIMARY KEY
requirement_id          INTEGER FK → requirements
verification_id         INTEGER FK → verification
verdict                 TEXT  -- 'passed', 'failed', 'conditional', 'not_tested'
context                 TEXT
acceptance_criteria     TEXT
verifier_user_id        INTEGER FK → users
verdict_date            DATE
created_at              TIMESTAMPTZ
```

### 22. tracelink (Generic Traceability)
```sql
id          SERIAL PRIMARY KEY
src_type    TEXT  -- 'requirement', 'design_item', 'artifact', etc.
src_id      INTEGER
dst_type    TEXT
dst_id      INTEGER
link_type   TEXT  -- 'derives_from', 'implements', 'verifies', 'validates'
created_at  TIMESTAMPTZ
```

**Common link_type values:**
- `derives_from` - Child requirement derived from parent
- `implements` - Design implements requirement
- `verifies` - Test verifies requirement
- `validates` - Validation confirms requirement
- `refines` - Lower-level refines higher-level
- `depends_on` - Dependency relationship

### 23. coverage (DO-178C Test Coverage)
```sql
id                  SERIAL PRIMARY KEY
verification_id     INTEGER FK → verification
software_item_id    INTEGER FK → software_item
type                TEXT  -- 'statement', 'branch', 'mcdc', 'function'
percentage          FLOAT
details             JSONB
created_at          TIMESTAMPTZ
```

**Coverage Types (DO-178C):**
- **statement** - Statement coverage (all DALs)
- **branch** - Decision coverage (DAL A-C)
- **mcdc** - Modified Condition/Decision Coverage (DAL A)
- **function** - Function coverage

### 24. approval
```sql
id          SERIAL PRIMARY KEY
entity_type TEXT
entity_id   INTEGER
approved_by INTEGER FK → users
verdict     TEXT  -- 'approved', 'rejected', 'conditional', 'pending'
comments    TEXT
approved_at TIMESTAMPTZ
```

### 25. audit_log
```sql
id          BIGSERIAL PRIMARY KEY
actor_id    INTEGER FK → users
actor_type  TEXT  -- 'human' or 'ai_agent'
action      TEXT  -- 'create', 'update', 'delete', 'approve', etc.
target_type TEXT
target_id   INTEGER
payload     JSONB
created_at  TIMESTAMPTZ
```

### 26. review
```sql
id              SERIAL PRIMARY KEY
name            TEXT
type            TEXT  -- 'SRR', 'PDR', 'CDR', 'TRR', 'code_review'
date            DATE
conducted_by    INTEGER FK → users
notes           TEXT
status          TEXT  -- 'planned', 'in_progress', 'completed', 'cancelled'
project_id      INTEGER FK → projects
created_at      TIMESTAMPTZ
```

**Review Types:**
- **SRR** - System Requirements Review
- **PDR** - Preliminary Design Review
- **CDR** - Critical Design Review
- **TRR** - Test Readiness Review
- **code_review** - Code Review

### 27. review_item
```sql
id          SERIAL PRIMARY KEY
review_id   INTEGER FK → review
entity_type TEXT
entity_id   INTEGER
findings    TEXT
status      TEXT  -- 'open', 'closed', 'deferred'
created_at  TIMESTAMPTZ
```

### 28. lifecycle_deliverable
```sql
id          SERIAL PRIMARY KEY
type        TEXT  -- 'SRS', 'SDD', 'SVP', 'STP', 'SAS'
title       TEXT
version     TEXT
status      TEXT  -- 'draft', 'review', 'approved', 'baseline'
artifact_id INTEGER FK → artifact
project_id  INTEGER FK → projects
created_at  TIMESTAMPTZ
```

**Deliverable Types (DO-178C):**
- **SRS** - Software Requirements Specification
- **SDD** - Software Design Description
- **SVP** - Software Verification Plan
- **STP** - Software Test Plan
- **SAS** - Software Accomplishment Summary
- **PSAC** - Plan for Software Aspects of Certification
- **SCMP** - Software Configuration Management Plan
- **SQAP** - Software Quality Assurance Plan

### 29. ai_job
```sql
id              SERIAL PRIMARY KEY
job_type        TEXT  -- 'create_requirement', 'generate_test', etc.
payload         JSONB
status          TEXT  -- 'pending', 'processing', 'completed', 'failed'
result          JSONB
error_message   TEXT
created_at      TIMESTAMPTZ
started_at      TIMESTAMPTZ
completed_at    TIMESTAMPTZ
executed_by     INTEGER FK → users
```

---

## 📈 Useful Views

### v_requirement_traceability
Complete view of requirement traceability with counts:
```sql
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
...
```

### v_software_coverage
Software items with average coverage:
```sql
SELECT
    si.id,
    si.identifier,
    si.dal,
    si.version,
    p.name as project_name,
    AVG(c.percentage) as avg_coverage,
    COUNT(DISTINCT c.id) as coverage_records
FROM software_item si
...
```

---

## 🔍 Common Queries

### 1. Find all requirements not yet verified
```sql
SELECT r.*
FROM requirements r
LEFT JOIN validation val ON val.requirement_id = r.id
WHERE val.id IS NULL AND r.status = 'approved';
```

### 2. Get software items with coverage < 90%
```sql
SELECT si.identifier, AVG(c.percentage) as avg_cov
FROM software_item si
JOIN coverage c ON c.software_item_id = si.id
GROUP BY si.id, si.identifier
HAVING AVG(c.percentage) < 90;
```

### 3. Complete traceability for a requirement
```sql
WITH RECURSIVE trace AS (
    SELECT * FROM tracelink WHERE src_type = 'requirement' AND src_id = 123
    UNION
    SELECT tl.* FROM tracelink tl
    JOIN trace t ON t.dst_id = tl.src_id AND t.dst_type = tl.src_type
)
SELECT * FROM trace;
```

### 4. All pending AI jobs
```sql
SELECT * FROM ai_job
WHERE status = 'pending'
ORDER BY created_at ASC;
```

### 5. Audit trail for a specific requirement
```sql
SELECT * FROM audit_log
WHERE target_type = 'requirement' AND target_id = 123
ORDER BY created_at DESC;
```

---

## 🎯 DO-178C Compliance Mapping

| DO-178C Objective | Tables Involved |
|-------------------|-----------------|
| Requirements Data | requirements, requirement_type, requirement_derivation |
| Design Data | design_item, software_design, hardware_design, artifact |
| Source Code | software_code, hardware_implementation |
| Verification Data | verification, validation, coverage |
| Traceability | tracelink, requirements_design_trace, requirements_test_trace |
| Configuration Management | baseline, baseline_item, entity_version |
| Quality Assurance | review, review_item, approval, audit_log |
| Lifecycle Data | lifecycle_deliverable |

---

## 🚀 Migration History

| Version | Date | Migration File | Changes |
|---------|------|----------------|---------|
| 1.0 | 2025-11-13 | Initial Schema | 16 tables (MVP) |
| 2.0 | 2025-11-14 | 002_add_compliance_schema_v2.sql | +26 tables, +views, full compliance |

---

**Last Updated:** 2025-11-14
**Maintained by:** AISET Development Team
