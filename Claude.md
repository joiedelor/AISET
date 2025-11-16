# AISET - AI Systems Engineering Tool
## Claude Code Resume File

**⭐ This file is Claude Code's resume reference**
**📖 For detailed human-readable status, see PROJECT_STATUS.md**
**📚 For documentation structure, see DOCUMENTATION_LEVELS.md (NEW)**

---

## 🚨 PROJECT STATUS (Last Updated: 2025-11-16 18:00 UTC)

### ✅ CURRENT STATE: ENTERPRISE ARCHITECTURE COMPLETE | COLLABORATIVE REQUIREMENTS DEFINED

**Repository:** https://github.com/joiedelor/AISET
**Status:** Requirements v0.8.0 Complete ✅ | Collaborative Architecture Defined ✅ | DO-178C Compliance: 25% ⚠️
**Version:** 0.1.0

**✅ CRITICAL MILESTONE:** Requirements specification complete (v0.8.0, 167 requirements)
**✅ CRITICAL MILESTONE:** Enterprise collaborative/distributed architecture defined
**✅ MAJOR MILESTONE:** Product structure & CI management (34+ fields) specified

### 🎯 SESSION SUMMARY (2025-11-16 10:00-18:00 UTC)

**COMPLETED ✅**

**Requirements Specification - Massive Expansion (v0.5.0 → v0.8.0):**
1. ✅ **v0.6.0:** Added 10 Project Initialization requirements (85 → 95 total)
   - REQ-AI-032 to REQ-AI-037: Structured project initialization interview
   - AI shall determine safety criticality, DAL/SIL, regulatory requirements
   - Foundation questions → Planning questions → Execution questions
   - REQ-FE-009: Project context display on dashboard
   - REQ-BE-012: Project initialization workflow
   - REQ-DB-035, REQ-DB-036: Project context and standards mapping storage

2. ✅ **v0.7.0:** Added 25 Product Structure & CI Management requirements (95 → 120 total)
   - REQ-AI-038 to REQ-AI-040: Product structure extraction, item data extraction, CI classification
   - REQ-FE-010 to REQ-FE-013: Product structure tree, BOM editor, item management, CI table view
   - REQ-BE-013 to REQ-BE-015: BOM management, item lifecycle, change impact analysis
   - REQ-DB-037 to REQ-DB-051: 15 database requirements for comprehensive CI management
   - **Created:** docs/Level_2_User_Framework/CONFIGURATION_ITEM_MANAGEMENT.md (34+ CI fields documented)

3. ✅ **v0.8.0:** Added 47 Collaborative & Distributed Work requirements (120 → 167 total)
   - **User answered 6 critical architecture questions:**
     - Q1: Both concurrent AND distributed (equal priority)
     - Q2: All scenarios (single company, prime+suppliers, multi-site)
     - Q3: Milestone-based merges
     - Q4: Semi-automatic merge (AI suggests, human approves)
     - Q5: Hybrid identifiers (GUID + human-readable)
     - Q6: Complex access control
   - REQ-AI-041 to REQ-AI-044: AI-assisted merge conflict resolution, duplicate detection, notifications, access control
   - REQ-FE-014 to REQ-FE-023: Check-out/check-in UI, merge review, conflict resolution, work assignment, notifications, comments, RBAC UI, merge preview, activity feed, lock indicators
   - REQ-BE-016 to REQ-BE-029: Pessimistic locking, optimistic conflict detection, work assignment, export/import, intelligent merge engine, merge preview/rollback, notifications, RBAC enforcement, session management, ID mapping, duplicate detection, instance tracking
   - REQ-DB-052 to REQ-DB-070: Hybrid ID system, session management, lock management, work assignment, RBAC, team permissions, CI-level ACL, comments, notifications, merge metadata, source instance tracking, ID mapping, conflicts, rollback, audit trail, external references, data sharing, activity log, duplicate detection

**Key Architecture Decisions:**
- ✅ Enterprise-grade collaborative platform (not single-user tool)
- ✅ Support BOTH concurrent access (same DB) AND distributed development (different DBs)
- ✅ Hybrid identifier strategy: GUID (internal, collision-free) + Display ID (human-readable)
- ✅ PLM-style check-out/check-in with pessimistic locking
- ✅ Intelligent merge engine with 5 conflict types + AI-assisted resolution
- ✅ Complex RBAC: 7 role types, team-based + CI-level permissions
- ✅ Milestone-based data exchange between AISET instances

**DO-178C COMPLIANCE STATUS ⚠️**
- **Overall Compliance:** 25% (unchanged - remediation pending)
- **Planning:** 40%
- **Requirements:** Comprehensive (REQUIREMENTS.md v0.8.0, 167 requirements) → needs SRS formatting
- **Design:** 0%
- **Code Quality:** 40%
- **Verification:** 0%
- **Traceability:** 0%

### 📋 CRITICAL INFORMATION FOR RESUMING

#### Location
- **Local Path:** `/home/joiedelor/aiset/`
- **Platform:** WSL2 Ubuntu on Windows
- **Access from Windows:** `\\wsl$\Ubuntu\home\joiedelor\aiset`

#### System Status (2025-11-15 19:30)
- ✅ **Backend API:** Can start with `cd backend && source venv/bin/activate && python -m uvicorn main:app --reload`
- ✅ **Frontend Dev:** Can start with `cd frontend && npm run dev`
- ✅ **PostgreSQL:** localhost:5432 (database: aiset_db, 42 tables + test data)
- ✅ **Test Data:** Project FURN-001 (ID: 3), Conversation ID: 1
- ⚠️ **DO-178C Compliance:** 25% - NOT production-ready

#### Documentation Structure (⭐ MAJOR UPDATE)

**4 DOCUMENTATION LEVELS - CRITICAL TO UNDERSTAND:**

1. **[Level 1] AISET Tool Development (DO-178C DAL D)**
   - Location: `01_PLANNING/` through `09_CERTIFICATION/`, `docs/Level_1_AISET_Development/`
   - Purpose: Develop AISET software tool itself
   - Standard: DO-178C DAL D

2. **[Level 2] AISET Usage Framework (ARP4754A)**
   - Location: `docs/Level_2_User_Framework/`
   - Purpose: What AISET helps USERS create (reference framework)
   - Standard: ARP4754A system development process
   - Files: PROJECT_PLAN.md (10-phase process), TRACEABILITY_MATRIX.md

3. **[Level 3] Claude Session Documentation**
   - Location: Root level
   - Purpose: Development continuity for Claude Code
   - Files: Claude.md (this file), PROJECT_STATUS.md, DOCUMENTATION_STRUCTURE.md

4. **[Level 4] Specification Roleplay**
   - Location: Root level
   - Purpose: Requirements capture via roleplay
   - Files: REQUIREMENTS.md (v0.8.0, 167 requirements), ROLEPLAY_RULES.md, ROLEPLAY_SESSION.md
   - Status: COMPLETED 2025-11-16

**⚠️ CRITICAL:** See `DOCUMENTATION_LEVELS.md` for complete separation guide

#### Essential Files

**Meta Documentation:**
- `DOCUMENTATION_LEVELS.md` - ⭐ MASTER: 4-level separation guide (NEW)
- `DOCUMENTATION_STRUCTURE.md` - Documentation organization (v2.0)
- `PROJECT_STRUCTURE.md` - Codebase structure (v0.2.0)

**[Level 3] Claude Session Documentation:**
- `Claude.md` - This file (Claude's quick reference)
- `PROJECT_STATUS.md` - Human-readable detailed status

**[Level 4] Specification Documents:**
- `REQUIREMENTS.md` - ⭐ Tool requirements (v0.8.0, 167 requirements)
- `ROLEPLAY_RULES.md` - Specification roleplay methodology
- `ROLEPLAY_SESSION.md` - Session status (COMPLETED)

**[Level 1] DO-178C Documentation:**
- `00_DO178C_INDEX.md` - Master DO-178C index (v1.1)
- `01_PLANNING/` - SDP, Tool Qualification, Standards (all have README.md)
- `02_REQUIREMENTS/` through `09_CERTIFICATION/` (all have README.md marking Level 1)

**[Level 2] User Framework (docs/Level_2_User_Framework/):**
- `Project_Plan.md` - 10-phase ARP4754A process (475 lines) - for AISET-AI context
- `TRACEABILITY_MATRIX.md` - Template of what AISET generates

**[Level 1] AISET Development Reference (docs/Level_1_AISET_Development/):**
- `DATABASE_SCHEMA.md` - Complete AISET database schema (42 tables)
- `SQL_requirement.md` - AISET database requirements
- `GAP_ANALYSIS.md` - DO-178C compliance gaps
- `DO178C_COMPLIANCE.md` - Compliance status

**Source Code:**
- `backend/` - 31 files (Python/FastAPI) - [Level 1]
- `frontend/` - 18 files (React/TypeScript) - [Level 1]

#### Quick Start Commands (For Next Session)

```bash
# Navigate to project
cd /home/joiedelor/aiset

# Start PostgreSQL (if not running)
sudo service postgresql start

# Terminal 1 - Backend
cd backend && source venv/bin/activate && python -m uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend && npm run dev

# Access:
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs

# Database access (test data exists):
PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql -h localhost -U aiset_user -d aiset_db
```

#### GitHub Push Procedure (MANDATORY)

**⚠️ ALWAYS follow this procedure when pushing to GitHub:**

1. **At session end, ask user:** "Can you push to GitHub?"
2. **User will provide credentials in format:** `joiedelor [token]`
3. **Use the push command:**
   ```bash
   git push https://joiedelor:[TOKEN]@github.com/joiedelor/AISET.git main
   ```
4. **After successful push, remind user:**
   - Token is now exposed in conversation history
   - Should revoke and create new token for security
   - Consider using SSH for future (more secure)

**⚠️ NEVER push without explicit user request and credentials**

#### Next Immediate Tasks

**SPECIFICATION → LEVEL 1 TRANSITION:**
1. **NEXT:** Transform REQUIREMENTS.md (Level 4) into formal SRS (Level 1)
   - Create `02_REQUIREMENTS/SRS_Software_Requirements_Specification.md`
   - Format per DO-178C requirements
   - Trace back to REQUIREMENTS.md source

**DO-178C REMEDIATION (Level 1):**
2. Create missing planning documents (PSAC, SVP, SCMP, SQAP)
3. Create design documentation (HLD, LLD)
4. Perform code reviews on all source code
5. Write unit tests for existing code
6. Establish traceability (Requirements → Design → Code → Tests)

**DEVELOPMENT:**
7. Begin frontend implementation
8. Begin backend API implementation
9. Test AISET-AI behavior against specification

#### Critical Documentation (⭐ READ FIRST)

**Level Separation (MUST READ):**
- **DOCUMENTATION_LEVELS.md** - ⭐ MASTER: Understand 4 levels (NEW 2025-11-15)
- **DOCUMENTATION_STRUCTURE.md** - Documentation organization (v2.0)
- **PROJECT_STRUCTURE.md** - Codebase structure (v0.2.0)

**Requirements Specification:**
- **REQUIREMENTS.md** - ⭐ Complete tool requirements (v0.8.0, 167 requirements)
- **ROLEPLAY_RULES.md** - Specification methodology
- **ROLEPLAY_SESSION.md** - Session history (COMPLETED)

**DO-178C Workflow:**
- **01_PLANNING/Standards/DO178C_Daily_Workflow_Guide.md** - MANDATORY workflow
- **.claude/session_end.md** - Session end procedure

---

## 🎯 Project Overview

AISET is an **AI-powered systems engineering tool** designed to automate requirements elicitation, design documentation, and traceability management for critical systems development.

### Primary Goal
Reduce engineering overhead by 50-70% while maintaining full compliance with aerospace and safety-critical standards, particularly **DO-178C** (Software Considerations in Airborne Systems and Equipment Certification).

### Key Requirements (v0.8.0 - 167 total)
- **AI Requirements (44):** One-question-at-a-time, task assignment, automatic updates, session management, project initialization interview, product structure extraction, AI-assisted merge, collaboration support
- **Frontend Requirements (23):** Dual interface (proposal + dialogue), project dashboard, document list, product structure tree, BOM editor, check-out/check-in UI, merge review, RBAC UI
- **Backend Requirements (29):** API endpoints, session state management, BOM management, pessimistic locking, optimistic conflict detection, intelligent merge engine, RBAC enforcement
- **Database Requirements (70):** 42 tables, document associations, traceability, hybrid ID system, lock management, work assignment, merge metadata, source instance tracking
- **Documentation Requirements (1):** REQ-DOC-001 - AI_INSTRUCTION.md creation

---

## 🏗️ Architecture

### Technology Stack
- **Backend**: Python 3.12+ with FastAPI
- **Frontend**: React 18 + TypeScript 5
- **Database**: PostgreSQL 15+ (42 tables)
- **AI Engine**: Claude API (primary) + LM Studio/Mistral (local fallback)

### Database Status
- **Tables:** 42 (full ARP4754/DO-178C/DO-254 compliance schema)
- **Test Data:** Project FURN-001 (Furniture Building Project)
  - Project ID: 3
  - Conversation ID: 1
  - Messages in ai_messages table

---

## 📊 Current Status

**Version**: 0.1.0 (Specification Complete)

**Recent Milestones (2025-11-16)**:
- ✅ Requirements specification complete (167 requirements)
- ✅ Enterprise collaborative/distributed architecture defined
- ✅ Product structure & CI management (34+ fields) specified
- ✅ Project initialization interview structured
- ✅ 4-level documentation separation implemented
- ✅ Database tested with real project data

**Next Phase**: Transform specification into DO-178C deliverables

---

**Last Updated**: 2025-11-16 18:00 UTC
**Status**: Enterprise Architecture Complete | Requirements v0.8.0 | Ready for DO-178C SRS creation
**Session**: Requirements expansion - Project initialization, CI management, collaborative/distributed architecture
