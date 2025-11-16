# AISET Documentation Levels - Separation Guide

**Version:** 1.0
**Date:** 2025-11-15
**Purpose:** Ensure clear separation of 4 distinct documentation levels

---

## 🎯 Four Documentation Levels

### **Level 1: AISET Tool Development (DO-178C DAL D)**
**Purpose:** Develop AISET software tool itself in compliance with DO-178C DAL D
**Audience:** AISET development team, DO-178C auditors, certification authorities
**Standards:** DO-178C DAL D, DO-330 (tool qualification)
**Location:** `01_PLANNING/` through `09_CERTIFICATION/`

**Key Documents:**
- Software Requirements Specification (SRS) for AISET tool
- Software Design Description (SDD) for AISET tool
- Software Verification Plan/Results for AISET tool
- Software Configuration Management Plan
- Software Quality Assurance Plan
- Source code and test cases for AISET
- Tool qualification data for AI models (Claude, LM Studio)

**Current Status:**
- ✅ SDP created
- ✅ Tool Qualification Plan (DO-330) created
- ✅ **COMPLETE:** Formal SRS created in 02_REQUIREMENTS/ (AISET-SRS-001 v1.0.0)
- ✅ Design documents created (HLD, LLD, Traceability Matrix)
- ❌ Missing: Test cases, verification reports

---

### **Level 2: AISET Tool Usage Documentation (ARP4754A Process)**
**Purpose:** Documentation that AISET tool helps USERS create for THEIR systems
**Audience:** AISET tool users developing their own safety-critical systems
**Standards:** ARP4754A, DO-178C (for user's software), DO-254 (for user's hardware)
**Location:** Should be OUTPUT of AISET tool, NOT in AISET development repo

**Process Framework:**
- `docs/PROJECT_PLAN.md` - Describes 10-phase ARP4754A process that AISET supports
- This is the REFERENCE for what AISET helps users create
- NOT documentation we create, but template/framework AISET provides

**What AISET Users Will Create (using AISET):**
- Their system requirements (StRS, SyRS)
- Their system architecture
- Their verification plans
- Their traceability matrices
- Their certification data packages

**Current Status:**
- ✅ PROJECT_PLAN.md exists as reference framework
- ✅ Correctly identified as USAGE documentation
- ✅ No mixing detected

**⚠️ CRITICAL DISTINCTION:**
- PROJECT_PLAN.md Phase 1-10 describes what AISET USERS do
- NOT what AISET development team does
- AISET development follows DO-178C, not ARP4754A system process

---

### **Level 3: Claude Code Session Documentation**
**Purpose:** Enable Claude Code to resume AISET development sessions
**Audience:** Claude Code (AI assistant), AISET developers
**Standards:** None (internal development support)
**Location:** Root level

**Key Documents:**
- `Claude.md` - Quick reference for Claude Code
- `PROJECT_STATUS.md` - Human-readable project status
- `DOCUMENTATION_STRUCTURE.md` - Documentation organization guide
- `PROJECT_STRUCTURE.md` - Codebase structure
- `.claude/session_end.md` - Session end procedure

**Current Status:**
- ✅ All files exist and properly organized
- ✅ Clear purpose (development continuity)
- ✅ Not part of DO-178C deliverables

---

### **Level 4: Specification Roleplay Documentation**
**Purpose:** Capture requirements for AISET tool via roleplay methodology
**Audience:** AISET requirements engineers, development team
**Standards:** None (requirements elicitation method)
**Location:** Root level (transition to Level 1)

**Key Documents:**
- `ROLEPLAY_REQUIREMENTS.md` - Captured requirements from roleplay (v0.8.0, 167 requirements - source material)
- `ROLEPLAY_RULES.md` - Specification roleplay methodology
- `ROLEPLAY_SESSION.md` - Roleplay session status and history

**Current Status:**
- ✅ Specification complete (167 requirements)
- ✅ **COMPLETE:** ROLEPLAY_REQUIREMENTS.md preserved as working file for future roleplay
- ✅ **COMPLETE:** Formal SRS created (02_REQUIREMENTS/SRS_Software_Requirements_Specification.md v1.0.0)
- ✅ Roleplay session completed

**Transition Complete:**
- ✅ REQUIREMENTS.md renamed to ROLEPLAY_REQUIREMENTS.md (working file)
- ✅ Formal SRS created in 02_REQUIREMENTS/ (official DO-178C deliverable)
- ✅ Clear separation: working file (Level 4) vs. official deliverable (Level 1)

---

## 🚨 Issues Identified & Resolutions

### **Issue 1: REQUIREMENTS.md Position**
**Current:** Root level, Level 4 (specification roleplay output)
**Should Be:** Also input to Level 1 as SRS source
**Resolution:**
- Keep REQUIREMENTS.md at root as specification source
- Create `02_REQUIREMENTS/SRS_Software_Requirements_Specification.md` in DO-178C format
- SRS references/derives from REQUIREMENTS.md

### **Issue 2: PROJECT_PLAN.md Confusion**
**Current:** In docs/ as reference
**Clarification:**
- This is Level 2 (AISET tool USAGE framework)
- Correctly placed in docs/
- Describes what AISET USERS follow, not AISET development
- ⚠️ **AISET development follows DO-178C, NOT ARP4754A system process**

### **Issue 3: Mixed Purpose in DO-178C Folders**
**Current:** 01_PLANNING through 09_CERTIFICATION might mix Level 1 and Level 2
**Resolution:**
- These folders are ONLY for Level 1 (AISET tool development per DO-178C)
- Remove any content related to user's system development
- Keep only AISET software development artifacts

---

## ✅ Correct Organization

### **Root Level**
```
AISET/
├── Level 3: Claude Session Docs
│   ├── Claude.md
│   ├── PROJECT_STATUS.md
│   ├── DOCUMENTATION_STRUCTURE.md
│   └── PROJECT_STRUCTURE.md
│
├── Level 4: Specification Docs (→ feeds Level 1)
│   ├── REQUIREMENTS.md ⭐ (source for Level 1 SRS)
│   ├── ROLEPLAY_RULES.md
│   └── ROLEPLAY_SESSION.md
│
└── This file
    └── DOCUMENTATION_LEVELS.md ⭐ (master separation guide)
```

### **docs/ Folder**
```
docs/
├── Level 1: AISET Development References
│   ├── DATABASE_SCHEMA.md (AISET database design)
│   ├── SQL_requirement.md (AISET database requirements)
│   ├── GAP_ANALYSIS.md (AISET DO-178C compliance gaps)
│   └── DO178C_COMPLIANCE.md (AISET compliance status)
│
└── Level 2: AISET Usage Framework
    ├── PROJECT_PLAN.md ⭐ (10-phase process AISET users follow)
    └── TRACEABILITY_MATRIX.md (example of what AISET generates)
```

### **01_PLANNING/ through 09_CERTIFICATION/ (DO-178C Structure)**
```
01-09_FOLDERS/
└── Level 1 ONLY: AISET Tool Development (DO-178C DAL D)
    ├── 01_PLANNING/
    │   ├── SDP_Software_Development_Plan.md (for AISET development)
    │   ├── PSAC (for AISET certification)
    │   ├── SVP (for AISET verification)
    │   └── Tool_Qualification/ (for AI tools used to develop AISET)
    │
    ├── 02_REQUIREMENTS/
    │   └── SRS_Software_Requirements_Specification.md (AISET requirements - derived from REQUIREMENTS.md)
    │
    ├── 03_DESIGN/
    │   ├── HLD (AISET architecture)
    │   └── LLD (AISET detailed design)
    │
    ├── 04_SOURCE_CODE/ (AISET source code)
    ├── 05_VERIFICATION/ (AISET tests)
    ├── 06_CONFIGURATION_MANAGEMENT/ (AISET CM)
    ├── 07_QUALITY_ASSURANCE/ (AISET QA)
    ├── 08_TRACEABILITY/ (AISET traceability)
    └── 09_CERTIFICATION/ (AISET certification data)
```

### **backend/ and frontend/ Folders**
```
backend/ & frontend/
└── Level 1: AISET Source Code
    └── Implementation of AISET tool per DO-178C DAL D
```

---

## 🔄 Key Principles

### **Principle 1: AISET Development ≠ User's System Development**
- **AISET Development (Level 1):** DO-178C DAL D for developing AISET software
- **User's System Development (Level 2):** ARP4754A process that AISET supports
- **NEVER MIX THESE TWO**

### **Principle 2: PROJECT_PLAN.md is Level 2, NOT Level 1**
- Describes what AISET USERS follow (ARP4754A)
- NOT what AISET developers follow (DO-178C)
- AISET developers follow DO-178C SDP, not ARP4754A system process

### **Principle 3: REQUIREMENTS.md Transition**
- Level 4 (specification) → Source
- Level 1 (DO-178C) → Formatted SRS derived from source
- Keep both, clearly linked

### **Principle 4: Clear Level Identification**
- Every document must be tagged with its level
- No document serves multiple levels (except REQUIREMENTS.md during transition)

---

## 📋 Action Items to Fix Mixing

### **Immediate Actions:**

1. **Create Level 1 SRS from REQUIREMENTS.md**
   - [ ] Create `02_REQUIREMENTS/SRS_Software_Requirements_Specification.md`
   - [ ] Format per DO-178C requirements
   - [ ] Trace back to REQUIREMENTS.md

2. **Update DOCUMENTATION_STRUCTURE.md**
   - [ ] Add Level 1, 2, 3, 4 sections
   - [ ] Tag each document with its level
   - [ ] Add cross-level relationships

3. **Audit DO-178C Folders (01-09)**
   - [ ] Ensure ONLY Level 1 content (AISET development)
   - [ ] Remove any Level 2 content (user system development)

4. **Update AI_INSTRUCTION.md** (when created)
   - [ ] Clarify AI operates at Level 2 (helps users)
   - [ ] AI is subject of Level 1 (tool qualification)
   - [ ] Document level awareness in AI behavior

5. **Create Level Tags**
   - [ ] Add `[Level 1]`, `[Level 2]`, `[Level 3]`, `[Level 4]` to document headers

---

## 🎯 Quick Reference Table

| Document | Current Location | Level | Purpose | Standards |
|----------|-----------------|-------|---------|-----------|
| Claude.md | Root | 3 | Session resume | None |
| PROJECT_STATUS.md | Root | 3 | Status tracking | None |
| REQUIREMENTS.md | Root | 4→1 | Specification → SRS source | None→DO-178C |
| ROLEPLAY_*.md | Root | 4 | Specification method | None |
| PROJECT_PLAN.md | docs/ | 2 | User process framework | ARP4754A |
| DATABASE_SCHEMA.md | docs/ | 1 | AISET DB design | DO-178C |
| SDP | 01_PLANNING/ | 1 | AISET development plan | DO-178C |
| SRS | 02_REQUIREMENTS/ | 1 | AISET requirements | DO-178C |
| Source code | backend/frontend/ | 1 | AISET implementation | DO-178C |

---

## ⚠️ Common Mixing Mistakes to Avoid

### **❌ WRONG:**
- Using PROJECT_PLAN.md phases for AISET development
- Putting user system requirements in AISET DO-178C folders
- Treating Level 3 docs as DO-178C deliverables
- Confusing AISET development with what AISET helps users do

### **✅ RIGHT:**
- AISET development follows DO-178C DAL D
- PROJECT_PLAN.md is what AISET tool SUPPORTS for users
- Level 3 docs are internal only
- Level 4 specs become Level 1 requirements

---

**This document is the authoritative guide for documentation level separation.**
**When in doubt, refer to this file.**
