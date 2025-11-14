# AISET Documentation Structure
## Master Documentation Guide

**Version:** 1.0
**Date:** 2025-11-14
**Status:** AUTHORITATIVE

---

## 🎯 Purpose

This document defines the **single source of truth** for all project documentation to:
- Eliminate redundancy
- Prevent inconsistencies
- Clarify which files to use
- Define update procedures

---

## 📁 File Structure & Responsibilities

### **ROOT LEVEL** (Quick Reference)

#### 1. `README.md`
**Purpose:** GitHub repository landing page
**Audience:** External users, contributors
**Content:**
- Project overview
- Quick start guide
- Installation instructions
- Usage examples
- Contribution guidelines
**Update Frequency:** When features change
**Owner:** Project Lead

#### 2. `Claude.md` ⭐ **CLAUDE'S RESUME FILE**
**Purpose:** Session resume for Claude Code AI
**Audience:** Claude Code (AI assistant)
**Content:**
- Current project status (high-level)
- System status (backend, frontend, database running)
- Critical information for resuming work
- Quick reference for locations
- Session summary
**Update Frequency:** END OF EVERY SESSION
**Owner:** Claude Code (auto-updated)
**Format:** Concise, structured, actionable

#### 3. `PROJECT_STATUS.md` ⭐ **HUMAN REFERENCE**
**Purpose:** Comprehensive project status for humans
**Audience:** Developers, managers, auditors
**Content:**
- Detailed project status
- DO-178C compliance metrics
- Remediation plans
- Known issues
- NCRs (Non-Conformance Reports)
- Required reading list
**Update Frequency:** Daily during active development
**Owner:** Project Manager
**Format:** Detailed, explanatory

#### 4. ~~`SESSION_RESUME.md`~~ **DEPRECATED - TO DELETE**
**Reason:** Redundant with Claude.md
**Action:** Content merged into Claude.md, file to be deleted

---

### **docs/** (Reference Documentation)

#### Purpose
Store all **reference guides** that don't change frequently and aren't DO-178C deliverables.

#### Files

##### `docs/DATABASE_SCHEMA.md` ⭐ **SINGLE SOURCE OF TRUTH**
**Purpose:** Complete database schema documentation
**Content:** All 42 tables, relationships, queries
**Update:** When schema changes
**Owner:** Database Engineer

##### `docs/SQL_requirement.md`
**Purpose:** Original database requirements specification
**Content:** Requirements for database design, ERD
**Update:** Rarely (original spec)
**Owner:** System Architect

##### `docs/GAP_ANALYSIS.md`
**Purpose:** Gap analysis between plan and reality
**Content:** All identified gaps, remediation roadmap
**Update:** Monthly during remediation
**Owner:** Compliance Officer

##### `docs/DO178C_COMPLIANCE.md`
**Purpose:** DO-178C compliance explanation
**Content:** How AISET meets DO-178C objectives
**Update:** When compliance level changes
**Owner:** Compliance Officer

##### `docs/TRACEABILITY_MATRIX.md`
**Purpose:** Requirements traceability documentation
**Content:** Traceability approach, matrix examples
**Update:** When traceability structure changes
**Owner:** Requirements Engineer

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

## 🎯 Single Source of Truth (SSOT)

| Topic | Authoritative File |
|-------|-------------------|
| Database Schema | `docs/DATABASE_SCHEMA.md` |
| Software Development Plan | `01_PLANNING/SDP_Software_Development_Plan.md` |
| Daily Workflow | `01_PLANNING/Standards/DO178C_Daily_Workflow_Guide.md` |
| Tool Qualification | `01_PLANNING/Tool_Qualification/Tool_Qualification_Plan_DO330.md` |
| Compliance Status | `PROJECT_STATUS.md` |
| Gap Analysis | `docs/GAP_ANALYSIS.md` |
| Claude Resume | `Claude.md` |

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
| 1.0 | 2025-11-14 | Initial structure definition, identified duplicates |

---

**This document is the authoritative guide for all AISET documentation.**
**When in doubt, refer to this file.**
