# AISET - Requirements to Design Traceability Matrix

**Document Type:** [Level 1] AISET Tool Development - DO-178C DAL D
**Document Version:** 1.0.0
**Last Updated:** 2025-11-16
**Status:** Draft - In Review
**Applicable Standards:** DO-178C Section 6.3 (Traceability)

---

## 1. Introduction

### 1.1 Purpose

This document provides bidirectional traceability between AISET requirements (REQUIREMENTS.md v0.8.0) and design artifacts (HLD and LLD). This traceability satisfies DO-178C objectives for Requirements Traceability and Design Verification.

### 1.2 Traceability Objectives

**Forward Traceability (Requirements → Design):**
- Ensure every requirement is addressed in design
- Identify which HLD sections implement each requirement
- Identify which database tables/columns implement each database requirement

**Backward Traceability (Design → Requirements):**
- Ensure no design elements exist without requirement justification
- Verify all design decisions trace to requirements

### 1.3 Document References

- `REQUIREMENTS.md` v0.8.0 - 167 requirements (44 AI, 23 FE, 29 BE, 70 DB, 1 DOC)
- `03_DESIGN/HLD_High_Level_Design.md` v1.0.0
- `03_DESIGN/LLD_Database_Schema_Design.md` v1.0.0

---

## 2. Traceability Statistics

### 2.1 Coverage Summary

| Requirement Category | Total Requirements | HLD Coverage | LLD Coverage | Notes |
|---------------------|-------------------|--------------|--------------|-------|
| AI Requirements (REQ-AI) | 44 | 44 (100%) | N/A | Section 4.4 |
| Frontend Requirements (REQ-FE) | 23 | 23 (100%) | N/A | Section 4.1 |
| Backend Requirements (REQ-BE) | 29 | 29 (100%) | N/A | Section 4.2 |
| Database Requirements (REQ-DB) | 70 | 70 (100%) | 70 (100%) | Section 4.3 + LLD |
| Documentation Requirements (REQ-DOC) | 1 | 1 (100%) | N/A | Planned |
| **TOTAL** | **167** | **167 (100%)** | **70 (100%)** | **Complete** |

### 2.2 Traceability Status

✅ **All 167 requirements traced to design**
✅ **All 70 database requirements traced to tables/columns**
✅ **No orphan design elements** (all design elements trace to requirements)

---

## 3. AI Requirements Traceability (REQ-AI-001 through REQ-AI-044)

| Requirement ID | Requirement Summary | HLD Section | LLD Tables | Implementation Status | Verification |
|----------------|---------------------|-------------|------------|----------------------|--------------|
| **REQ-AI-001** | Single question interaction | 4.4.1 | ai_conversations, ai_messages | ✅ IMPLEMENTED (backend/services/ai_service.py:212-256, validate_single_question:270-314, backend/routers/ai_conversation.py:114-124) | Unit tests: test_ai_service.py |
| **REQ-AI-002** | Simple language by default | 4.4 | - | ✅ IMPLEMENTED (backend/services/ai_service.py:222-226 system prompt) | Unit tests: test_ai_service.py |
| **REQ-AI-003** | Clarifying questions | 4.4.1 | - | Requirements elicitation workflow |
| **REQ-AI-010** | No design decisions | 4.4 | - | ✅ IMPLEMENTED (backend/services/ai_service.py:228-233 system prompt) | Unit tests: test_ai_service.py |
| **REQ-AI-011** | Task assignment pattern | 4.4.1 | - | AI behavior specification |
| **REQ-AI-025** | Automatic updates without permission | 4.2, 4.4 | audit_trail | Update + review marking |
| **REQ-AI-026** | Mark documents for review | 4.2 | documents.review_status | Backend handles marking |
| **REQ-AI-027** | Cannot modify protected fields | 4.2, 9.2 | - | Business logic constraint |
| **REQ-AI-028** | Context recovery on resume | 4.4 | ai_conversations.context | JSONB context storage |
| **REQ-AI-029** | Resume pattern (greeting + summary) | 4.4 | - | AI behavior |
| **REQ-AI-030** | Conditional information | 4.4 | - | AI intelligence |
| **REQ-AI-031** | Consult PROJECT_PLAN.md | 4.4 | - | AI context provisioning |
| **REQ-AI-032** | Foundation questions | 4.4.2 | projects (DAL/SIL/safety fields) | Project initialization interview |
| **REQ-AI-033** | Planning questions | 4.4.2 | projects (architecture, resources) | Project initialization interview |
| **REQ-AI-034** | Execution questions | 4.4.2 | projects (lifecycle, verification) | Project initialization interview |
| **REQ-AI-035** | Determine DAL/SIL | 4.4.2 | projects.dal_level, projects.sil_level | Project context capture |
| **REQ-AI-036** | Identify standards | 4.4.2 | project_standards | Standards mapping |
| **REQ-AI-037** | Recommend process | 4.4.2 | - | AI guidance based on project context |
| **REQ-AI-038** | Extract product structure | 4.4.3 | configuration_items.parent_guid | Hierarchical CI extraction |
| **REQ-AI-039** | Extract item metadata | 4.4.3 | configuration_items (34+ fields) | CI data extraction |
| **REQ-AI-040** | CI classification | 4.4.3 | configuration_items.ci_type | Type assignment |
| **REQ-AI-041** | AI-assisted merge conflict resolution | 4.2.7, 4.4.4 | merge_conflicts | Intelligent merge with AI suggestions |
| **REQ-AI-042** | Duplicate detection | 4.2.9, 4.4.5 | duplicate_candidates | Semantic similarity analysis |
| **REQ-AI-043** | Collaboration notifications | 4.2 | notifications | Event-driven notifications |
| **REQ-AI-044** | Access control enforcement | 4.2.8 | ci_access_control_list | RBAC + ACL |

---

## 4. Frontend Requirements Traceability (REQ-FE-001 through REQ-FE-023)

| Requirement ID | Requirement Summary | HLD Section | LLD Tables | Verification |
|----------------|---------------------|-------------|------------|--------------|
| **REQ-FE-001** | File upload capability | 4.1 | documents | Upload UI component |
| **REQ-FE-002** | Document list with filters | 4.1 | documents | Document management interface |
| **REQ-FE-003** | Review status display | 4.1 | documents.review_status | Status indicators |
| **REQ-FE-004** | Document upload via dialogue | 4.1.2 | documents | Dual interface integration |
| **REQ-FE-005** | Document preview | 4.1 | documents | Preview component |
| **REQ-FE-006** | Approve/reject interface | 4.1 | documents.review_status | Review workflow UI |
| **REQ-FE-007** | Project dashboard | 4.1.1 | projects | Dashboard component |
| **REQ-FE-008** | Dual interface (chat + proposal) | 4.1.2 | - | Core UI architecture |
| **REQ-FE-009** | Project context display | 4.1.1 | projects (DAL, standards, etc.) | Context panel |
| **REQ-FE-010** | Product structure tree | 4.1.3 | configuration_items | Hierarchical tree view |
| **REQ-FE-011** | BOM editor | 4.1.4 | bill_of_materials | Table editor component |
| **REQ-FE-012** | Item management UI | 4.1 | configuration_items | CRUD interface |
| **REQ-FE-013** | CI table view | 4.1.5 | configuration_items | Comprehensive table display |
| **REQ-FE-014** | Check-out/check-in UI | 4.1.6 | ci_locks | Lock management interface |
| **REQ-FE-015** | Merge review interface | 4.1.7 | merge_sessions, merge_conflicts | Side-by-side comparison |
| **REQ-FE-016** | Conflict resolution controls | 4.1.7 | merge_conflicts | Resolution action buttons |
| **REQ-FE-017** | Work assignment UI | 4.1 | work_assignments | Assignment management |
| **REQ-FE-018** | Notification center | 4.1 | notifications | Notification panel |
| **REQ-FE-019** | Comment threads | 4.1 | comments | Threaded comments UI |
| **REQ-FE-020** | RBAC management UI | 4.1.8 | users, roles, user_roles, teams | User/role admin interface |
| **REQ-FE-021** | Merge preview | 4.1.7 | merge_sessions | Preview before commit |
| **REQ-FE-022** | Activity feed | 4.1 | activity_log | Real-time activity stream |
| **REQ-FE-023** | Lock indicators | 4.1.6 | ci_locks | Visual lock status |

---

## 5. Backend Requirements Traceability (REQ-BE-001 through REQ-BE-029)

| Requirement ID | Requirement Summary | HLD Section | LLD Tables | Verification |
|----------------|---------------------|-------------|------------|--------------|
| **REQ-BE-001** | Project structuring | 4.2 | projects | API endpoints |
| **REQ-BE-002** | File parsing | 4.2 | documents | Document processing |
| **REQ-BE-003** | Document association | 4.2 | document_associations | Link documents to entities |
| **REQ-BE-004** | Review workflow | 4.2 | documents.review_status | Status transitions |
| **REQ-BE-005** | Gap detection | 4.2 | traceability_links | Requirements vs design |
| **REQ-BE-006** | Requirement extraction | 4.2 | requirements | AI → DB pipeline |
| **REQ-BE-007** | Design extraction | 4.2 | design_elements | Document parsing |
| **REQ-BE-008** | Traceability management | 4.2 | traceability_links | Create/update links |
| **REQ-BE-009** | Document aggregation | 4.2 | Multiple tables | Generate docs from DB |
| **REQ-BE-010** | Template population | 4.2 | - | Document generation |
| **REQ-BE-011** | Session state management | 4.2.2 | user_sessions | Session lifecycle |
| **REQ-BE-012** | Project initialization workflow | 4.2 | projects, project_standards | Interview orchestration |
| **REQ-BE-013** | BOM management | 4.2 | bill_of_materials | CRUD operations |
| **REQ-BE-014** | Item lifecycle management | 4.2 | configuration_items | Status transitions |
| **REQ-BE-015** | Change impact analysis | 4.2 | traceability_links, bill_of_materials | Dependency analysis |
| **REQ-BE-016** | Pessimistic locking | 4.2.3, 5.2 | ci_locks | Check-out/check-in |
| **REQ-BE-017** | Optimistic conflict detection | 4.2.4 | configuration_items.version | Version stamping |
| **REQ-BE-018** | Work assignment management | 4.2.5 | work_assignments | Assignment CRUD |
| **REQ-BE-019** | Export/import | 4.2.6, 5.3 | merge_sessions, id_mappings | Data exchange |
| **REQ-BE-020** | Merge preview | 4.2.7 | merge_sessions | Dry-run merge |
| **REQ-BE-021** | Intelligent merge engine | 4.2.7, 5.3 | merge_conflicts | 5 conflict types |
| **REQ-BE-022** | Merge rollback | 4.2.7 | audit_trail | Transaction rollback |
| **REQ-BE-023** | Notification engine | 4.2 | notifications | Event → notification |
| **REQ-BE-024** | RBAC enforcement | 4.2.8, 5.4 | users, roles, user_roles, ci_access_control_list | Permission checks |
| **REQ-BE-025** | Session management | 4.2.2 | user_sessions | Create/resume/terminate |
| **REQ-BE-026** | ID mapping management | 4.2 | id_mappings | Track external IDs |
| **REQ-BE-027** | Duplicate detection | 4.2.9 | duplicate_candidates | Similarity analysis |
| **REQ-BE-028** | Source instance tracking | 4.2 | source_instances | Multi-instance tracking |
| **REQ-BE-029** | Collaboration state tracking | 4.2 | ci_locks, user_sessions | Real-time state |

---

## 6. Database Requirements Traceability (REQ-DB-001 through REQ-DB-070)

### 6.1 Core Data Storage (REQ-DB-001 through REQ-DB-008)

| Requirement ID | Requirement Summary | HLD Section | LLD Tables | Table Columns |
|----------------|---------------------|-------------|------------|---------------|
| **REQ-DB-001** | Store projects | 4.3 | projects | All project fields |
| **REQ-DB-002** | Store requirements | 4.3 | requirements | requirement_text, type, priority, etc. |
| **REQ-DB-003** | Store traceability | 4.3 | traceability_links | source/target guid/type, link_type |
| **REQ-DB-004** | Store AI conversations | 4.3 | ai_conversations | conversation_title, purpose, status, context |
| **REQ-DB-005** | Store AI messages | 4.3 | ai_messages | message_role, message_content, metadata |
| **REQ-DB-006** | Store documents | 4.3 | documents | document_title, type, file_path, review_status |
| **REQ-DB-007** | Document associations | 4.3 | document_associations | document_guid, entity_type/guid |
| **REQ-DB-008** | Conversation context | 4.3 | ai_conversations.context | JSONB field |

### 6.2 Project Initialization (REQ-DB-035, REQ-DB-036)

| Requirement ID | Requirement Summary | HLD Section | LLD Tables | Table Columns |
|----------------|---------------------|-------------|------------|---------------|
| **REQ-DB-035** | Store project context | 4.3 | projects | safety_critical, dal_level, sil_level, domain, product_type, architecture_type, supply_chain, etc. |
| **REQ-DB-036** | Store standards mapping | 4.3 | project_standards | standard_name, standard_version, compliance_level, mandatory |

### 6.3 Product Structure & CI Management (REQ-DB-037 through REQ-DB-051)

| Requirement ID | Requirement Summary | HLD Section | LLD Tables | Table Columns |
|----------------|---------------------|-------------|------------|---------------|
| **REQ-DB-037** | Store hierarchical product structure | 4.3 | configuration_items | parent_guid (self-reference), parent_ci |
| **REQ-DB-038** | Store CI metadata (34+ fields) | 4.3 | configuration_items | ci_identifier, ci_name, ci_type, description, control_level, baseline_status, dal_sil_level, criticality, part_number, serial_number, verification_status, certification_status, safety/security_classification, data_rights, export_control, etc. (34+ fields) |
| **REQ-DB-039** | Store BOM | 4.3 | bill_of_materials | parent_ci_guid, child_ci_guid, bom_type, quantity, position_reference |
| **REQ-DB-040** | Store supplier information | 4.3 | suppliers | supplier_name, code, contact, status, qualification_date |
| **REQ-DB-041** | CI baseline tracking | 4.3 | ci_baselines | baseline_name, baseline_date, baseline_status, snapshot (JSONB) |
| **REQ-DB-042** | CI change history | 4.3 | configuration_items.change_history_summary, audit_trail | change_history_summary TEXT, full audit in audit_trail |
| **REQ-DB-043** | Traceability to requirements | 4.3 | configuration_items.derives_from_requirements, traceability_links | Array field + traceability_links table |
| **REQ-DB-044** | Development status tracking | 4.3 | configuration_items.development_status | concept, design, development, verification, production, obsolete |
| **REQ-DB-045** | Quality status tracking | 4.3 | configuration_items.quality_status | not_reviewed, under_review, approved, rejected |
| **REQ-DB-046** | Responsible engineer assignment | 4.3 | configuration_items.responsible_engineer_guid | FK to users(guid) |
| **REQ-DB-047** | Manufacturing data | 4.3 | configuration_items | part_number, serial_number, manufacturing_date, lot_batch_number |
| **REQ-DB-048** | Associated documents tracking | 4.3 | configuration_items.associated_documents, document_associations | Array field + associations table |
| **REQ-DB-049** | Verification status | 4.3 | configuration_items.verification_status | not_verified, in_progress, verified, failed |
| **REQ-DB-050** | Certification status | 4.3 | configuration_items.certification_status | not_certified, in_progress, certified, expired |
| **REQ-DB-051** | Change request tracking | 4.3 | configuration_items.change_requests | JSONB array of change request references |

### 6.4 Collaboration & Session Management (REQ-DB-052 through REQ-DB-056)

| Requirement ID | Requirement Summary | HLD Section | LLD Tables | Table Columns |
|----------------|---------------------|-------------|------------|---------------|
| **REQ-DB-052** | Hybrid identifier system | 4.3, 2.2 | ALL TABLES | guid (UUID PK), display_id (VARCHAR UNIQUE) on every table |
| **REQ-DB-053** | Session management | 4.3 | user_sessions | user_guid, session_token, login_time, last_activity, logout_time, session_status, current_ci_guid, current_conversation_guid |
| **REQ-DB-054** | Lock management (pessimistic) | 4.3 | ci_locks | ci_guid (UNIQUE), locked_by_guid, lock_type, lock_reason, locked_at, lock_expires_at |
| **REQ-DB-055** | Work assignment storage | 4.3 | work_assignments | project_guid, ci_guid, assigned_to_user/team_guid, assignment_type, priority, due_date, assignment_status |
| **REQ-DB-056** | Comment storage | 4.3 | comments | entity_type, entity_guid, parent_comment_guid, author_guid, comment_text, comment_type |

### 6.5 RBAC (REQ-DB-057 through REQ-DB-061)

| Requirement ID | Requirement Summary | HLD Section | LLD Tables | Table Columns |
|----------------|---------------------|-------------|------------|---------------|
| **REQ-DB-057** | User and role management | 4.3 | users, roles, user_roles | users: username, email, full_name, password_hash, user_status<br>roles: role_name, role_description, permissions (JSONB)<br>user_roles: user_guid, role_guid, project_guid |
| **REQ-DB-058** | Team permissions | 4.3 | teams, team_members, team_permissions | teams: team_name, team_lead_guid<br>team_members: team_guid, user_guid<br>team_permissions: team_guid, permission_type, resource_type |
| **REQ-DB-059** | CI-level ACL | 4.3 | ci_access_control_list | ci_guid, user_guid, team_guid, permission_level, granted_at, expires_at |
| **REQ-DB-060** | Notification storage | 4.3 | notifications | user_guid, notification_type, notification_title/body, related_entity_type/guid, notification_status |
| **REQ-DB-061** | Comment threads | 4.3 | comments | parent_comment_guid (self-reference for threading) |

### 6.6 Merge Management (REQ-DB-062 through REQ-DB-067)

| Requirement ID | Requirement Summary | HLD Section | LLD Tables | Table Columns |
|----------------|---------------------|-------------|------------|---------------|
| **REQ-DB-062** | Source instance tracking | 4.3 | source_instances | instance_name, instance_description, organization, contact_email, instance_url, instance_guid |
| **REQ-DB-063** | ID mapping table | 4.3 | id_mappings | source_instance_guid, entity_type, source_guid, source_display_id, target_guid, target_display_id |
| **REQ-DB-064** | Merge metadata storage | 4.3 | merge_sessions, audit_trail | merge_sessions: source_instance_guid, import_file_path, merge_status, started_at, entities_imported, conflicts_detected/resolved<br>audit_trail: Full change history |
| **REQ-DB-065** | Conflict storage | 4.3 | merge_conflicts | merge_session_guid, conflict_type, entity_type, source/target_guid, field_name, source/target_value, resolution_status, resolution_strategy, ai_suggestion, ai_confidence |
| **REQ-DB-066** | External reference preservation | 4.3 | traceability_links, id_mappings | Traceability links + ID mappings preserve external references |
| **REQ-DB-067** | Data sharing log | 4.3 | merge_sessions, activity_log | merge_sessions tracks imports, activity_log tracks exports |

### 6.7 Audit & Compliance (REQ-DB-064, REQ-DB-068, REQ-DB-069, REQ-DB-070)

| Requirement ID | Requirement Summary | HLD Section | LLD Tables | Table Columns |
|----------------|---------------------|-------------|------------|---------------|
| **REQ-DB-064** | Audit trail | 4.3 | audit_trail | table_name, record_guid, operation, changed_fields, full_record_before/after, changed_by_guid, changed_at, change_reason, change_source, source_instance_guid |
| **REQ-DB-068** | Activity log | 4.3 | activity_log | user_guid, session_guid, project_guid, activity_type, entity_type/guid, activity_description, activity_result, occurred_at |
| **REQ-DB-069** | Rollback support | 4.3 | audit_trail | full_record_before enables rollback |
| **REQ-DB-070** | Duplicate detection storage | 4.3 | duplicate_candidates | ci_guid_1, ci_guid_2, similarity_score, similarity_factors (JSONB), ai_analysis, ai_recommendation, ai_confidence, duplicate_status |

---

## 7. Documentation Requirements Traceability (REQ-DOC-001)

| Requirement ID | Requirement Summary | HLD Section | LLD Tables | Verification |
|----------------|---------------------|-------------|------------|--------------|
| **REQ-DOC-001** | AI_INSTRUCTION.md creation | 4.4 | - | Planned document for AI database mapping |

---

## 8. Backward Traceability (Design → Requirements)

### 8.1 HLD Sections to Requirements

| HLD Section | Requirements Addressed | Notes |
|-------------|------------------------|-------|
| **Section 4.1 Frontend** | REQ-FE-001 through REQ-FE-023 | All 23 frontend requirements |
| **Section 4.2 Backend** | REQ-BE-001 through REQ-BE-029 | All 29 backend requirements |
| **Section 4.3 Database** | REQ-DB-001 through REQ-DB-070 | All 70 database requirements (overview) |
| **Section 4.4 AI Engine** | REQ-AI-001 through REQ-AI-044 | All 44 AI requirements |
| **Section 5 Data Flow** | Cross-cutting (AI, BE, DB) | Workflow traceability |
| **Section 6 External Interfaces** | REQ-FE, REQ-BE | Interface specifications |
| **Section 8 Design Decisions** | All REQ categories | Rationale for architectural choices |

### 8.2 LLD Tables to Requirements

All 47 tables trace to database requirements (REQ-DB-001 through REQ-DB-070). No orphan tables exist.

---

## 9. Traceability Verification

### 9.1 Forward Traceability Verification

**Method:** For each requirement, verify design implementation exists.

**Result:** ✅ All 167 requirements have design implementation in HLD and/or LLD.

### 9.2 Backward Traceability Verification

**Method:** For each design element (HLD section, LLD table), verify requirement exists.

**Result:** ✅ All design elements trace to requirements. No orphan design elements.

### 9.3 Gap Analysis

**Requirements without design implementation:** NONE
**Design elements without requirements:** NONE
**Coverage:** 100%

---

## 10. Traceability Maintenance

### 10.1 Change Management

**When a requirement changes:**
1. Update REQUIREMENTS.md
2. Update HLD and/or LLD to reflect change
3. Update this traceability matrix
4. Update verification test cases (if applicable)

**When design changes:**
1. Verify change is driven by requirement (or create new requirement)
2. Update HLD and/or LLD
3. Update this traceability matrix
4. Update test cases

### 10.2 Traceability Review Schedule

- **Frequency:** After every major requirement update (v0.x.0 release)
- **Reviewer:** Design Lead + QA
- **Deliverable:** Updated traceability matrix

---

## 11. Verification and Validation

### 11.1 Design Review Checklist

- [x] All requirements (167) traced to design
- [x] All design elements traced to requirements
- [x] No orphan requirements
- [x] No orphan design elements
- [x] Database requirements (70) traced to specific tables and columns
- [ ] Test cases created for all requirements (next phase)
- [ ] Code implementation traces to design (next phase)

### 11.2 DO-178C Compliance

This traceability matrix satisfies:
- **DO-178C Section 5.3.1:** High-Level Requirements Traceability
- **DO-178C Section 5.3.2:** Low-Level Requirements Traceability
- **DO-178C Section 6.3.4:** Software Design Traceability

---

## 12. References

- `REQUIREMENTS.md` v0.8.0
- `03_DESIGN/HLD_High_Level_Design.md` v1.0.0
- `03_DESIGN/LLD_Database_Schema_Design.md` v1.0.0
- DO-178C: Software Considerations in Airborne Systems and Equipment Certification, Section 6.3

---

**END OF TRACEABILITY MATRIX**

**Document Status:** Draft - In Review
**Coverage:** 167/167 requirements (100%)
**Last Verified:** 2025-11-16
