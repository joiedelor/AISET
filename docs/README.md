# AISET Documentation Reference

**⚠️ CRITICAL:** This folder is PHYSICALLY SEPARATED by documentation levels

See `/DOCUMENTATION_LEVELS.md` for complete level definitions.

---

## 📂 Folder Structure

```
docs/
├── Level_1_AISET_Development/     [Level 1] AISET Tool Development (DO-178C DAL D)
│   ├── DATABASE_SCHEMA.md         Complete AISET database schema (47 tables)
│   ├── SQL_requirement.md         AISET database requirements specification
│   ├── GAP_ANALYSIS.md            AISET DO-178C compliance gap analysis
│   └── DO178C_COMPLIANCE.md       AISET DO-178C compliance status
│
└── Level_2_User_Framework/        [Level 2] AISET Usage Framework (ARP4754A)
    ├── Project_Plan.md            10-phase ARP4754A process (what AISET users follow)
    └── TRACEABILITY_MATRIX.md     Template of traceability matrices AISET generates
```

---

## 🎯 Key Distinction

### Level 1: AISET Development (in `Level_1_AISET_Development/`)
- **Purpose:** Document AISET tool development per DO-178C DAL D
- **Audience:** AISET developers, DO-178C auditors
- **Standard:** DO-178C DAL D
- **Files:** Technical documentation for AISET tool itself
- **Also see:** `/01_PLANNING/` through `/09_CERTIFICATION/` folders

### Level 2: User Framework (in `Level_2_User_Framework/`)
- **Purpose:** Reference framework for what AISET helps USERS create
- **Audience:** AISET-AI (for context), future AISET users
- **Standard:** ARP4754A system development process
- **Files:** Process templates and examples
- **⚠️ CRITICAL:** These describe what AISET USERS do, NOT what AISET developers do!

---

## ⚠️ NEVER MIX THESE TWO LEVELS!

- **AISET Development (Level 1):** We develop AISET tool per DO-178C
- **User Systems (Level 2):** AISET helps users develop their systems per ARP4754A
- **These are DIFFERENT processes with DIFFERENT standards!**

---

## 📚 Related Documentation

- **Level Separation Guide:** `/DOCUMENTATION_LEVELS.md` ⭐ READ THIS FIRST
- **Documentation Structure:** `/DOCUMENTATION_STRUCTURE.md`
- **Project Structure:** `/PROJECT_STRUCTURE.md`
- **DO-178C Index:** `/00_DO178C_INDEX.md`

---

**Last Updated:** 2025-11-15 (Physically separated into level folders)
