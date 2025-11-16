# AISET - AI Systems Engineering Tool
## Claude Code Resume File

**⭐ This file is Claude Code's resume reference**
**📖 For detailed human-readable status, see PROJECT_STATUS.md**
**📚 For documentation structure, see DOCUMENTATION_LEVELS.md (NEW)**

---

## 🚨 PROJECT STATUS (Last Updated: 2025-11-15 19:30 UTC)

### ✅ CURRENT STATE: SPECIFICATION COMPLETE | LEVEL SEPARATION APPLIED

**Repository:** https://github.com/joiedelor/AISET
**Status:** Specification Complete ✅ | Documentation Organized ✅ | DO-178C Compliance: 25% ⚠️
**Version:** 0.1.0

**✅ MAJOR MILESTONE:** Requirements specification complete (v0.5.0, 85 requirements)
**✅ MAJOR MILESTONE:** 4-level documentation separation implemented

### 🎯 SESSION SUMMARY (2025-11-15 09:00-19:30 UTC)

**COMPLETED ✅**

**Specification & Requirements:**
1. ✅ Specification roleplay completed (FURN-001 furniture project)
2. ✅ Database tested with real data (Project ID: 3, Conversation ID: 1)
3. ✅ REQUIREMENTS.md updated to v0.5.0 (85 requirements: 31 AI, 8 FE, 11 BE, 34 DB, 1 DOC)
4. ✅ Added REQ-AI-031: Product Development Context Awareness (AI consults PROJECT_PLAN.md)
5. ✅ Added REQ-AI-028-030: Session management requirements
6. ✅ Added REQ-FE-008: Dual Interface Layout (proposal + dialogue fields)
7. ✅ Roleplay session documented in ROLEPLAY_SESSION.md (COMPLETED status)

**Documentation Level Separation (CRITICAL):**
8. ✅ Created DOCUMENTATION_LEVELS.md - Master guide for 4-level separation
9. ✅ Updated DOCUMENTATION_STRUCTURE.md to v2.0 with level tags
10. ✅ Updated PROJECT_STRUCTURE.md to v0.2.0 with complete level tags
11. ✅ Updated root README.md with 4-level structure table
12. ✅ Updated 00_DO178C_INDEX.md to v1.1 with Level 1 warning

**Physical Project Organization:**
13. ✅ Created README.md in all 9 DO-178C folders (01-09) - all marked [Level 1]
14. ✅ Physically separated docs/ folder:
    - Created Level_1_AISET_Development/ folder
    - Created Level_2_User_Framework/ folder
    - Moved files to appropriate level folders
15. ✅ Created docs/README.md explaining physical separation
16. ✅ Removed Zone.Identifier Windows artifacts
17. ✅ Removed empty subdirectories (api/, guides/, images/)

**Key Insights & Clarifications:**
- ⭐ PROJECT_PLAN.md is Level 2 (what AISET USERS follow - ARP4754A)
- ⭐ AISET development follows DO-178C DAL D (Level 1), NOT ARP4754A
- ⭐ Critical separation: AISET tool development ≠ User system development
- ⭐ One-question-at-a-time is CRITICAL constraint for AISET-AI (REQ-AI-001)

**DO-178C COMPLIANCE STATUS ⚠️**
- **Overall Compliance:** 25% (unchanged - remediation pending)
- **Planning:** 40%
- **Requirements:** Source ready (REQUIREMENTS.md v0.5.0) → needs SRS formatting
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
   - Files: REQUIREMENTS.md (v0.5.0, 85 requirements), ROLEPLAY_RULES.md, ROLEPLAY_SESSION.md
   - Status: COMPLETED 2025-11-15

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
- `REQUIREMENTS.md` - ⭐ Tool requirements (v0.5.0, 85 requirements)
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
- **REQUIREMENTS.md** - ⭐ Complete tool requirements (v0.5.0, 85 requirements)
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

### Key Requirements (v0.5.0 - 85 total)
- **AI Requirements (31):** One-question-at-a-time, task assignment, automatic updates, session management
- **Frontend Requirements (8):** Dual interface (proposal + dialogue), project dashboard, document list
- **Backend Requirements (11):** API endpoints, session state management
- **Database Requirements (34):** 42 tables, document associations, traceability
- **Documentation Requirements (1):** REQ-AI-031 - AI consults PROJECT_PLAN.md for context

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

**Recent Milestones (2025-11-15)**:
- ✅ Requirements specification complete (85 requirements)
- ✅ 4-level documentation separation implemented
- ✅ Physical folder organization by level
- ✅ Specification roleplay methodology documented
- ✅ Database tested with real project data

**Next Phase**: Transform specification into DO-178C deliverables

---

**Last Updated**: 2025-11-15 19:30 UTC
**Status**: Specification Complete | Documentation Organized | Ready for DO-178C SRS creation
**Session**: Specification roleplay and documentation organization
