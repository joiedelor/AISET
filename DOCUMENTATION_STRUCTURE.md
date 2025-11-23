# AISET Documentation Structure
## Master Documentation Guide

**Version:** 2.0
**Date:** 2025-11-15
**Status:** AUTHORITATIVE

---

## 🎯 Purpose

This document defines the **single source of truth** for all project documentation to:
- Eliminate redundancy
- Prevent inconsistencies
- Clarify which files to use
- Define update procedures
- **Separate 4 distinct documentation levels**

---

## ⚠️ CRITICAL: Four Documentation Levels

**READ FIRST:** `DOCUMENTATION_LEVELS.md` - Master guide for level separation

### **Level 1: AISET Tool Development (DO-178C DAL D)**
Developing AISET software tool itself → `01-09_CERTIFICATION/` folders

### **Level 2: AISET Usage Framework (ARP4754A)**
What AISET helps users create → `docs/PROJECT_PLAN.md` (reference only)

### **Level 3: Claude Session Documentation**
Development continuity → Root level (Claude.md, PROJECT_STATUS.md, etc.)

### **Level 4: Specification Roleplay**
Requirements capture → Root level (REQUIREMENTS.md, ROLEPLAY_*.md)

**📖 See DOCUMENTATION_LEVELS.md for complete details and anti-mixing guidelines**

---

## 📁 File Structure & Responsibilities

### **ROOT LEVEL** (Quick Reference)

#### 1. `README.md` **[Level 1 + Level 3]**
**Purpose:** GitHub repository landing page
**Audience:** External users, contributors, developers
**Content:**
- Project overview
- Quick start guide
- Installation instructions
- Usage examples
- Contribution guidelines
**Update Frequency:** When features change
**Owner:** Project Lead

#### 2. `Claude.md` ⭐ **[Level 3]** CLAUDE'S RESUME FILE
**Purpose:** Session resume for Claude Code AI
**Audience:** Claude Code (AI assistant)
**Level:** 3 - Internal development continuity (NOT a DO-178C deliverable)
**Content:**
- Current project status (high-level)
- System status (backend, frontend, database running)
- Critical information for resuming work
- Quick reference for locations
- Session summary
**Update Frequency:** END OF EVERY SESSION
**Owner:** Claude Code (auto-updated)
**Format:** Concise, structured, actionable

#### 3. `PROJECT_STATUS.md` ⭐ **[Level 3]** HUMAN REFERENCE
**Purpose:** Comprehensive project status for humans
**Audience:** Developers, managers, auditors
**Level:** 3 - Internal development tracking (NOT a DO-178C deliverable)
**Content:**
- Detailed project status
- DO-178C compliance metrics (for Level 1)
- Remediation plans
- Known issues
- NCRs (Non-Conformance Reports)
- Required reading list
**Update Frequency:** Daily during active development
**Owner:** Project Manager
**Format:** Detailed, explanatory

#### 4. `DOCUMENTATION_LEVELS.md` ⭐ **[Meta]** LEVEL SEPARATION GUIDE
**Purpose:** Master guide for separating 4 documentation levels
**Audience:** All team members, Claude Code
**Level:** Meta - Defines organization of all levels
**Content:**
- Definition of 4 levels
- Current status and issues
- Anti-mixing guidelines
- Action items for proper separation
**Update Frequency:** When level structure changes
**Owner:** Documentation Lead
**Status:** ✅ CREATED 2025-11-15

#### 5. ~~`SESSION_RESUME.md`~~ **DEPRECATED - TO DELETE**
**Reason:** Redundant with Claude.md
**Action:** Content merged into Claude.md, file to be deleted

---

### **ROOT LEVEL** (Specification Documents) **[Level 4]**

#### 6. `REQUIREMENTS.md` ⭐ **[Level 4 → Level 1 source]** TOOL REQUIREMENTS
**Purpose:** Complete requirements specification for AISET tool
**Audience:** Development team, Claude Code
**Level:** 4 (Specification output) → Feeds Level 1 (becomes SRS source)
**Content:**
- All requirements (AI, Frontend, Backend, Database, Documentation)
- Requirements traceability
- Requirement sources and versions
**Update Frequency:** During specification phase, then change-controlled
**Owner:** Requirements Engineer
**Status:** v0.5.0 (85 requirements) - ✅ SPECIFICATION COMPLETE
**Breakdown:** 31 AI, 8 FE, 11 BE, 34 DB, 1 DOC
**Transition:** Will be formatted into Level 1 SRS (DO-178C format)

#### 7. `ROLEPLAY_RULES.md` **[Level 4]** SPECIFICATION ROLEPLAY GUIDE
**Purpose:** Rules and principles for specification roleplay sessions
**Audience:** Claude Code, Specification Team
**Level:** 4 - Specification methodology (NOT a DO-178C deliverable)
**Content:**
- Roleplay structure and triggers
- AISET-AI behavior principles
- Claude's dual responsibility (assess + respond)
- Session continuity guidelines
**Update Frequency:** When roleplay methodology changes
**Owner:** System Architect

#### 8. `ROLEPLAY_SESSION.md` **[Level 4]**
**Purpose:** Current/last roleplay session status
**Audience:** Claude Code, Specification Team
**Level:** 4 - Specification session tracking (NOT a DO-178C deliverable)
**Content:**
- Session state and history
- Requirements gathered
- Database test data created
- Resume instructions
**Update Frequency:** During active roleplay sessions
**Owner:** Claude Code (auto-updated)
**Status:** COMPLETED (2025-11-15)

---

### **docs/** (Reference Documentation) **[Physically Separated by Level]**

#### Purpose
Store **reference guides** - PHYSICALLY SEPARATED into level-specific subdirectories

**Structure:**
```
docs/
├── Level_1_AISET_Development/  [Level 1 folder]
└── Level_2_User_Framework/     [Level 2 folder]
```

---

#### **Level 2 Reference: AISET Usage Framework**

##### `docs/Level_2_User_Framework/PROJECT_PLAN.md` ⭐ **[Level 2]** PRODUCT DEVELOPMENT ROADMAP
**Purpose:** Framework for what AISET helps USERS create (NOT AISET development itself)
**Audience:** AISET-AI (for context), future AISET users
**Level:** 2 - AISET tool USAGE framework (ARP4754A process)
**Content:** 10-phase ARP4754A-aligned system development process (475 lines)
  - Phase 1: Requirements Capture & Definition
  - Phase 2: System Architecture Definition & Allocation
  - Phase 3-10: Design, Integration, Verification, Validation, Certification, Production, Support, End-of-Life
**AI Usage:** AISET-AI consults this (REQ-AI-031) to understand what USERS will do
**Status:** ✅ COMPLETE - Full 10-phase process documented
**⚠️ CRITICAL:** This describes what AISET USERS follow, NOT what AISET developers follow
**AISET Development:** Follows DO-178C DAL D (Level 1), NOT this ARP4754A process

##### `docs/Level_2_User_Framework/TRACEABILITY_MATRIX.md` **[Level 2]**
**Purpose:** Example/template of traceability matrix that AISET generates
**Content:** Traceability approach, matrix examples
**Level:** 2 - Example of AISET output for users
**Update:** When traceability structure changes
**Owner:** Requirements Engineer

---

#### **Level 1 Reference: AISET Tool Development**

##### `docs/Level_1_AISET_Development/DATABASE_SCHEMA.md` ⭐ **[Level 1]** SINGLE SOURCE OF TRUTH
**Purpose:** Complete database schema documentation FOR AISET TOOL
**Content:** All 47 tables, relationships, queries, DDL implementation
**Level:** 1 - AISET tool technical design
**Update:** When AISET schema changes
**Owner:** Database Engineer

##### `docs/Level_1_AISET_Development/SQL_requirement.md` **[Level 1]**
**Purpose:** Original database requirements specification FOR AISET TOOL
**Content:** Requirements for AISET database design, ERD
**Level:** 1 - AISET tool requirements
**Update:** Rarely (original spec)
**Owner:** System Architect

##### `docs/Level_1_AISET_Development/GAP_ANALYSIS.md` **[Level 1]**
**Purpose:** Gap analysis for AISET DO-178C compliance
**Content:** All identified gaps in AISET development, remediation roadmap
**Level:** 1 - AISET development status
**Update:** Monthly during remediation
**Owner:** Compliance Officer

##### `docs/Level_1_AISET_Development/DO178C_COMPLIANCE.md` **[Level 1]**
**Purpose:** DO-178C compliance status FOR AISET TOOL
**Content:** How AISET meets DO-178C objectives
**Level:** 1 - AISET development compliance
**Update:** When AISET compliance level changes
**Owner:** Compliance Officer

##### ~~`docs/DO178C_Project_Structure.md`~~ **DUPLICATE - TO DELETE**
**Reason:** Duplicate of 01_PLANNING/DO178C_Project_Structure.md
**Action:** Delete, keep version in 01_PLANNING/

##### ~~`docs/SDP_Software_Development_Plan.md`~~ **DUPLICATE - TO DELETE**
**Reason:** Duplicate of 01_PLANNING/SDP_Software_Development_Plan.md
**Action:** Delete, keep version in 01_PLANNING/

##### ~~`docs/DO178C_Daily_Workflow_Guide.md`~~ **DUPLICATE - TO DELETE**
**Reason:** Duplicate of 01_PLANNING/Standards/DO178C_Daily_Workflow_Guide.md
**Action:** Delete, keep version in 01_PLANNING/Standards/

##### ~~`docs/Tool_Qualification_Plan_DO330.md`~~ **DUPLICATE - TO DELETE**
**Reason:** Duplicate of 01_PLANNING/Tool_Qualification/Tool_Qualification_Plan_DO330.md
**Action:** Delete, keep version in 01_PLANNING/Tool_Qualification/

---

### **01_PLANNING/** through **09_CERTIFICATION/** (DO-178C Deliverables)

#### Purpose
Official DO-178C lifecycle data. These are **certification deliverables**.

#### Structure

```
01_PLANNING/
├── PSAC_Plan_Software_Aspects_Certification.md    [TODO]
├── SDP_Software_Development_Plan.md               [✅ COMPLETE]
├── SVP_Software_Verification_Plan.md              [TODO]
├── SCMP_Software_Configuration_Management_Plan.md [TODO]
├── SQAP_Software_Quality_Assurance_Plan.md        [TODO]
├── Standards/
│   └── DO178C_Daily_Workflow_Guide.md             [✅ COMPLETE]
└── Tool_Qualification/
    └── Tool_Qualification_Plan_DO330.md           [✅ COMPLETE]

02_REQUIREMENTS/
└── SRS_Software_Requirements_Specification.md     [TODO]

03_DESIGN/
├── HLD_High_Level_Design.md                       [TODO]
└── LLD_Low_Level_Design.md                        [TODO]

04_SOURCE_CODE/
├── Code_Reviews/                                  [Empty]
└── AI_Tool_Usage/
    └── TU-2025-11-14-001_Session_Setup.md         [✅ COMPLETE]

05_VERIFICATION/
├── Test_Plans/                                    [Empty]
├── Test_Cases/                                    [Empty]
├── Test_Results/                                  [Empty]
└── Tool_Qualification/                            [Empty]

06_CONFIGURATION_MANAGEMENT/
└── [To be populated]

07_QUALITY_ASSURANCE/
└── [To be populated]

08_TRACEABILITY/
└── [To be populated]

09_CERTIFICATION/
└── SAS_Software_Accomplishment_Summary.md         [TODO]
```

#### Key Files

##### `01_PLANNING/SDP_Software_Development_Plan.md` ⭐ **OFFICIAL SDP**
**Purpose:** Official DO-178C Software Development Plan
**Update:** Only through formal change control
**Owner:** Development Lead

##### `01_PLANNING/Standards/DO178C_Daily_Workflow_Guide.md` ⭐ **DAILY GUIDE**
**Purpose:** Mandatory daily workflow for developers
**Update:** When process changes
**Owner:** Process Manager

##### `01_PLANNING/Tool_Qualification/Tool_Qualification_Plan_DO330.md` ⭐ **TOOL QUAL**
**Purpose:** Tool qualification plan for Claude Code & LM Studio
**Update:** When tools change
**Owner:** Tool Qualification Engineer

---

## 🔄 Update Responsibilities

### End of Every Session (MANDATORY)

**Claude Code MUST update:**
1. ✅ `Claude.md` - Session summary, current status
2. ✅ `PROJECT_STATUS.md` - Compliance metrics, next steps
3. ✅ Create git commit with all changes
4. ✅ Prepare push command (user executes)

**Template for session end:**
```markdown
## Session End Checklist
- [ ] Claude.md updated
- [ ] PROJECT_STATUS.md updated
- [ ] All new files added to git
- [ ] Commit created with descriptive message
- [ ] Push command provided to user
```

### Daily (During Active Development)

**Developer updates:**
- `PROJECT_STATUS.md` - After significant changes
- Relevant DO-178C documents - When deliverables change

### Weekly

**Project Manager reviews:**
- `PROJECT_STATUS.md` - Accuracy
- `docs/GAP_ANALYSIS.md` - Progress on gaps

### Monthly

**Compliance Officer reviews:**
- All DO-178C deliverables
- `docs/DO178C_COMPLIANCE.md`
- `docs/GAP_ANALYSIS.md`

---

## 🗑️ Files to Delete (Duplicates)

Execute these deletions:

```bash
# Delete duplicate files from docs/
rm /home/joiedelor/aiset/docs/DO178C_Project_Structure.md
rm /home/joiedelor/aiset/docs/SDP_Software_Development_Plan.md
rm /home/joiedelor/aiset/docs/DO178C_Daily_Workflow_Guide.md
rm /home/joiedelor/aiset/docs/Tool_Qualification_Plan_DO330.md

# Delete deprecated session resume
rm /home/joiedelor/aiset/SESSION_RESUME.md

# Delete Zone.Identifier files (Windows artifacts)
find /home/joiedelor/aiset -name "*.Zone.Identifier" -delete
```

---

## 📝 File Content Guidelines

### Claude.md Format
```markdown
# AISET - Project Resume for Claude Code

**Last Updated:** YYYY-MM-DD HH:MM UTC
**Status:** [One-line status]

## Quick Status
- Backend: [status]
- Frontend: [status]
- Database: [X tables]
- Compliance: [X%]

## Current Session Summary
[Bulleted list of what was done]

## System Status
[How to start everything]

## Critical Locations
[Key file paths]

## Next Priorities
[Top 3-5 items]
```

### PROJECT_STATUS.md Format
```markdown
# AISET - Project Status & Resume Guide

**Last Updated:** YYYY-MM-DD
**Version:** X.Y.Z
**Status:** [Detailed status]

## Critical Status Update
[Current state, warnings]

## Project Quick Summary
[Overview with metrics]

## Current Status
[Detailed breakdown by area]

## Remediation Plan
[Phases with tasks]

## Documentation Created
[List of all docs]

## Known Issues
[NCRs and limitations]
```

---

## 🎯 Single Source of Truth (SSOT) - By Level

| Topic | Authoritative File | Level |
|-------|-------------------|-------|
| **Level 1: AISET Development** |
| AISET Requirements (source) | `REQUIREMENTS.md` | 4→1 |
| AISET Database Schema | `docs/Level_1_AISET_Development/DATABASE_SCHEMA.md` | 1 |
| AISET Development Plan | `01_PLANNING/SDP_Software_Development_Plan.md` | 1 |
| AISET Daily Workflow | `01_PLANNING/Standards/DO178C_Daily_Workflow_Guide.md` | 1 |
| AISET Tool Qualification | `01_PLANNING/Tool_Qualification/Tool_Qualification_Plan_DO330.md` | 1 |
| AISET Gap Analysis | `docs/Level_1_AISET_Development/GAP_ANALYSIS.md` | 1 |
| AISET Compliance Status | `docs/Level_1_AISET_Development/DO178C_COMPLIANCE.md` | 1 |
| **Level 2: User Framework** |
| User Development Process | `docs/Level_2_User_Framework/Project_Plan.md` | 2 |
| Traceability Template | `docs/Level_2_User_Framework/TRACEABILITY_MATRIX.md` | 2 |
| **Level 3: Claude Sessions** |
| Claude Resume | `Claude.md` | 3 |
| Project Status Tracking | `PROJECT_STATUS.md` | 3 |
| Documentation Organization | `DOCUMENTATION_STRUCTURE.md` | 3 |
| **Level 4: Specification** |
| Specification Output | `REQUIREMENTS.md` | 4 |
| Roleplay Methodology | `ROLEPLAY_RULES.md` | 4 |
| Roleplay Session | `ROLEPLAY_SESSION.md` | 4 |
| **Meta** |
| Level Separation Guide | `DOCUMENTATION_LEVELS.md` | Meta |

---

## ⚠️ Anti-Patterns to Avoid

### ❌ DON'T
- Create duplicate files in multiple locations
- Update one copy but not others
- Store DO-178C deliverables in docs/
- Put temporary files in git
- Forget to update Claude.md at session end

### ✅ DO
- Have ONE authoritative version
- Reference (link to) instead of duplicate
- Store DO-178C deliverables in 01-09 folders
- Use .gitignore for temporary files
- ALWAYS update Claude.md before ending session

---

## 🔧 Maintenance

### When Adding New Documentation
1. Determine if it's a DO-178C deliverable
   - YES → Put in appropriate 01-09 folder
   - NO → Put in docs/
2. Update this file (DOCUMENTATION_STRUCTURE.md)
3. Update README.md if user-facing
4. Never duplicate across folders

### When Updating Existing Documentation
1. Find the SSOT from table above
2. Update ONLY that file
3. If referenced elsewhere, verify links still work

---

## 📚 Quick Reference for Claude Code

**Before ending ANY session:**

```python
# Pseudo-code for session end
1. Update Claude.md with session summary
2. Update PROJECT_STATUS.md if compliance changed
3. Check for duplicates (shouldn't exist)
4. Git add all changes
5. Git commit with detailed message
6. Provide push command to user
7. Verify todolist is empty or updated
```

**Files Claude MUST always update:**
- `Claude.md` (every session)
- `PROJECT_STATUS.md` (when status changes)

**Files Claude should NEVER modify without explicit request:**
- Official DO-178C plans in 01_PLANNING/
- README.md (user-facing)

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.3 | 2025-11-23 | Added Product Structure/BOM Management (REQ-AI-038-040): configuration_item.py model, configuration_item_service.py, configuration_items.py router, ProductStructure.tsx page |
| 2.2 | 2025-11-23 | Enhanced Traceability.tsx with interactive matrix visualization (REQ-FE-012) |
| 2.1 | 2025-11-23 | Added JWT authentication files: auth_service.py, auth_dependencies.py, auth.py router, AuthContext.tsx, Login.tsx, Register.tsx |
| 2.0 | 2025-11-15 | **MAJOR:** Separated 4 documentation levels. Added level tags to all documents. Created DOCUMENTATION_LEVELS.md. Reorganized SSOT table by level. Critical clarification: PROJECT_PLAN.md is Level 2 (user framework), NOT Level 1 (AISET development). |
| 1.1 | 2025-11-15 | Added PROJECT_PLAN.md (product development roadmap for AISET-AI context), REQUIREMENTS.md, ROLEPLAY_RULES.md, ROLEPLAY_SESSION.md to SSOT table |
| 1.0 | 2025-11-14 | Initial structure definition, identified duplicates |

---

**This document is the authoritative guide for all AISET documentation.**
**When in doubt, refer to this file.**
