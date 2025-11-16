# Configuration Item (CI) Management in AISET

**Document Level:** [Level 2] AISET User Framework
**Purpose:** Defines how AISET manages Configuration Items for user projects
**Audience:** AISET users developing safety-critical and complex systems
**Standards:** Based on IEEE 828, MIL-STD-973, DO-178C, DO-254, ISO 26262
**Version:** 1.0
**Last Updated:** 2025-11-16

---

## Document Purpose

This document defines how AISET manages Configuration Items (CIs) throughout the product lifecycle. Configuration Management is a critical discipline for complex systems development, especially for safety-critical products requiring certification.

**What is a Configuration Item?**

A Configuration Item is any artifact that:
1. Is formally controlled and baselined
2. Can change independently
3. Requires formal approval for changes
4. Needs traceability to requirements, tests, and other CIs

Examples: Software modules, hardware assemblies, design documents, test procedures, tools, models

---

## CI Table - Content Structure

AISET stores comprehensive CI data to support full lifecycle configuration management. The following fields define the complete CI information model.

### Core Identification Fields

#### 1. CI Identifier (Unique ID)

**Format:** Structured alphanumeric code
**Example:** `SYS-SW-001`, `HW-PCBA-023`, `DOC-REQ-005`
**Purpose:** Unique, persistent identifier across entire lifecycle
**Best Practice:** Use hierarchical naming (System-Subsystem-Component)

**AISET Implementation:**
- Automatically assigns CI IDs based on project naming convention
- Ensures uniqueness within project
- Supports custom ID format configuration
- Never reuses IDs (retired IDs are marked obsolete, not deleted)

---

#### 2. CI Name/Title

**Description:** Human-readable name
**Example:** "Flight Control Software Module", "Power Supply Board Rev C", "System Requirements Specification"
**Purpose:** Clear identification for team members

**AISET Implementation:**
- Extracted from document titles or user input
- Searchable full-text field
- Supports aliases and alternate names

---

#### 3. CI Type/Category

**Common Types:**
- **Software:** Source code, executables, databases, scripts
- **Hardware:** PCBAs, assemblies, electronic components
- **Firmware:** Embedded software in hardware devices
- **Mechanical:** Parts, assemblies, drawings, 3D models
- **Documentation:** Requirements, design docs, test procedures, manuals
- **Data:** Configuration files, calibration data, databases
- **Tools:** Compilers, test equipment, development tools (require qualification per DO-330)
- **Models:** Simulation models, AI/ML models, digital twins

**Purpose:** Groups similar items, defines applicable processes

**AISET Implementation:**
- Predefined CI types with extensibility
- Type determines applicable standards and processes
- Type drives traceability requirements (e.g., software CIs require DO-178C compliance)

---

#### 4. Version/Revision

**Format:** Depends on CI type
- **Software:** Semantic versioning (e.g., v2.3.1) or build numbers
- **Hardware:** Revision letters (Rev A, B, C) or engineering change levels
- **Documents:** Version numbers with major.minor (e.g., 1.0, 1.1, 2.0)

**Purpose:** Track evolution and changes

**AISET Implementation:**
- Automatic version incrementing based on change type
- Supports multiple versioning schemes
- Full version history retained
- Links versions to baselines and change requests

---

#### 5. Baseline Status

**Values:** Draft, Under Review, Baselined, Released, Obsolete, Archived
**Purpose:** Indicates maturity and change control status

**Key Baselines:**
- **Functional Baseline:** Requirements approved and under configuration control
- **Allocated Baseline:** Architecture and high-level design baselined
- **Product Baseline:** Final design ready for production/certification

**AISET Implementation:**
- Status workflow with automatic notifications
- Prevents unauthorized changes to baselined items
- Tracks which baseline(s) include this CI version

---

### Configuration Management Fields

#### 6. Configuration Control Level

**Values:**
- **Level 1:** Customer/Authority approval required (e.g., certification authority)
- **Level 2:** Internal CCB (Configuration Control Board) approval
- **Level 3:** Engineering Manager approval
- **Level 4:** Controlled but no formal approval (peer review)
- **Level 5:** Uncontrolled (working documents)

**Purpose:** Defines change approval authority

**AISET Implementation:**
- Control level determines approval workflow
- Higher levels require more rigorous review and documentation
- Automatically routes change requests to appropriate approvers

---

#### 7. Change Control Status

**Values:** Open for Change, Change Controlled, Frozen
**Purpose:** Indicates whether changes are permitted and process required

**AISET Implementation:**
- Prevents unauthorized edits to change-controlled CIs
- Requires change request (CR/ECO/ECN) for modifications
- "Frozen" status for CIs in production or certified products

---

#### 8. Owner/Responsible Party

**Content:** Person, team, or organization responsible
**Example:** "Software Team Lead", "Supplier XYZ", "Systems Engineering"
**Purpose:** Accountability for CI maintenance and changes

**AISET Implementation:**
- Links to user/team database
- Owner receives notifications for change requests
- Owner approves baseline transitions
- Delegation support for temporary ownership transfer

---

#### 9. Custodian/Location

**Content:** Physical or digital location
**Example:** "Git repository - main branch", "PLM system - vault A", "Supplier facility"
**Purpose:** Where to find the current version

**AISET Implementation:**
- Supports links to external repositories (Git, PLM, file shares)
- Tracks physical location for hardware items
- Supports multiple storage locations (primary + backups)

---

### Traceability & Relationships

#### 10. Parent CI(s)

**Content:** CI identifier(s) of parent assemblies
**Example:** Software module belongs to software subsystem
**Purpose:** Hierarchical structure, roll-up of changes

**AISET Implementation:**
- Many-to-many relationship (CI can have multiple parents)
- Visual product structure tree
- Change impact analysis rolls up to parent CIs

---

#### 11. Child CI(s) / Components

**Content:** List of CI identifiers that compose this CI
**Example:** Assembly contains multiple boards and mechanical parts
**Purpose:** Impact analysis for changes

**AISET Implementation:**
- Automatic BOM generation from parent-child relationships
- Multi-level explosion (show all descendants)
- Where-used analysis (which CIs use this component?)

---

#### 12. Related/Interface CIs

**Content:** CIs that interface with this one
**Example:** Software interfaces with specific hardware; document describes this CI
**Purpose:** Interface management, impact analysis

**AISET Implementation:**
- Interface relationship type (mechanical, electrical, data, control)
- Interface Control Documents (ICDs) linked to interface relationships
- Impact analysis: changes to this CI may affect related CIs

---

#### 13. Requirements Traceability

**Content:** Links to requirements satisfied by this CI
**Example:** Requirements IDs from System Requirements Specification (SyRS)
**Purpose:** Verification and impact analysis

**AISET Implementation:**
- Bidirectional traceability: requirement → CI and CI → requirement
- Supports multiple requirement levels (system, software, hardware)
- Traceability matrix generation
- Gap analysis: requirements without CIs, CIs without requirements

---

### Development & Quality Fields

#### 14. Development Assurance Level (DAL) / Criticality

**Values:**
- **Aerospace:** DAL A, B, C, D, E (DO-178C/DO-254)
- **Industrial:** SIL 1, 2, 3, 4 (IEC 61508)
- **Automotive:** ASIL A, B, C, D (ISO 26262)
- **Medical:** Class I, II, III (IEC 62304)

**Purpose:** Determines rigor of development and verification
**Note:** May be "N/A" for non-safety-related items

**AISET Implementation:**
- DAL/criticality inherited from requirements or manually assigned
- Determines applicable processes and verification requirements
- Higher DAL = more reviews, more documentation, more testing

---

#### 15. Applicable Standards

**Content:** List of standards/processes applied
**Example:** "DO-178C DAL B", "DO-254 Level C", "ISO 9001"
**Purpose:** Compliance tracking

**AISET Implementation:**
- Links to project's applicable standards (from project initialization)
- Standard clauses traced to CIs
- Compliance checklist generated based on standards

---

#### 16. Verification Status

**Values:** Not Started, In Progress, Verified, Accepted
**Purpose:** Track completion of verification activities

**AISET Implementation:**
- Links to test cases and test results
- Automatic status update when all tests pass
- Verification coverage metrics (% of requirements verified)

---

#### 17. Qualification/Certification Status

**Values:** Not Applicable, Required, In Progress, Qualified, Certified
**Purpose:** Track regulatory compliance status

**AISET Implementation:**
- Tracks certification milestones
- Links to certification artifacts (SOIs, SCRs, etc.)
- Certification authority approval tracking

---

### Change Management Fields

#### 18. Last Change Date

**Format:** ISO date (YYYY-MM-DD HH:MM:SS)
**Purpose:** Track when CI was last modified

**AISET Implementation:**
- Automatic timestamp on every change
- Change frequency metrics
- Stability analysis (frequently changing CIs = risk)

---

#### 19. Last Change Reference

**Content:** Change Request/ECO/ECN number
**Example:** "ECR-2024-156", "ECO-745"
**Purpose:** Traceability to approved changes

**AISET Implementation:**
- Links to change request database
- No changes without approved CR (for change-controlled CIs)
- Audit trail: all changes traceable to CRs

---

#### 20. Change History Summary

**Content:** Brief description of major changes per version
**Example:** "v2.0: Added redundancy feature per ECR-123"
**Purpose:** Quick understanding of evolution

**AISET Implementation:**
- Version-by-version change log
- Searchable change descriptions
- Comparison between versions (diff/delta)

---

#### 21. Deviation/Waiver Status

**Values:** None, Active Deviation, Waived Requirement
**Content:** Reference to deviation/waiver documentation
**Purpose:** Track approved non-conformances

**AISET Implementation:**
- Links to deviation/waiver requests
- Expiration dates for temporary deviations
- Impact analysis: which CIs are affected by deviation

---

### Lifecycle & Support Fields

#### 22. Lifecycle Phase

**Values:** Concept, Development, Qualification, Production, In-Service, Obsolete
**Purpose:** Indicates current lifecycle state

**AISET Implementation:**
- Automatic phase transitions based on status gates
- Phase-specific processes and checklists
- Metrics: time in each phase, phase gate completion

---

#### 23. Effectivity

**Content:** Serial numbers, production lots, or dates where this CI applies
**Example:** "Effective S/N 1001 and later", "Aircraft MSN 5000+"
**Purpose:** Track which products contain which CI versions

**AISET Implementation:**
- Effectivity rules: by S/N range, by date, by product variant
- As-built configuration: which S/N units have which CI versions
- Retrofit planning: which units need updates

---

#### 24. Interchangeability

**Values:**
- **Form-Fit-Function (F3):** Fully interchangeable (drop-in replacement)
- **Form-Fit (F2):** Physical fit, but functional differences (may need config changes)
- **Not Interchangeable:** Requires design/approval before substitution

**Purpose:** Maintenance and support planning

**AISET Implementation:**
- Interchangeability matrix
- Alerts when non-interchangeable parts are substituted
- Approved alternates list

---

#### 25. Obsolescence Status

**Values:** Active, Obsolescence Risk, Obsolete, Replacement Available
**Purpose:** Lifecycle management and procurement planning

**AISET Implementation:**
- Automatic obsolescence monitoring (for COTS parts)
- Last-time-buy alerts
- Replacement part recommendations
- Obsolescence risk score

---

### Manufacturing & Procurement Fields (for Hardware/Physical CIs)

#### 26. Part Number

**Content:** Manufacturing part number (may differ from CI ID)
**Purpose:** Procurement and manufacturing reference

**AISET Implementation:**
- Supports multiple part number types: internal, manufacturer, supplier, customer
- Cross-reference table between part numbers
- Part number search across all types

---

#### 27. Supplier/Manufacturer

**Content:** Supplier name and code
**Purpose:** Supply chain management

**AISET Implementation:**
- Links to supplier database (from product structure requirements)
- Approved Vendor List (AVL) status
- Supplier qualification tracking
- Multi-source parts tracking

---

#### 28. Material/Technology

**Content:** Key materials or technologies used
**Purpose:** Obsolescence tracking, environmental compliance (RoHS, REACH)

**AISET Implementation:**
- Material composition database
- Conflict minerals tracking
- Environmental compliance reporting
- Technology refresh planning

---

### Documentation Fields

#### 29. Associated Documentation

**Content:** Links to related documents
**Examples:**
- Design specifications
- Test procedures
- User manuals
- Safety assessments
- Interface Control Documents (ICDs)
- Certification artifacts

**Purpose:** Complete configuration package

**AISET Implementation:**
- Document-to-CI many-to-many relationships
- Document generation from CI data (automated reporting)
- Configuration package export (all docs for a CI)

---

#### 30. Data Rights/IP Classification

**Values:** Proprietary, Limited Rights, Government Purpose Rights, Unlimited Rights, Open Source
**Purpose:** Legal and licensing management

**AISET Implementation:**
- Data rights specified per CI
- License compliance tracking (for open source CIs)
- Export restrictions enforcement
- IP ownership tracking (especially for supplier-developed CIs)

---

#### 31. Export Control Classification

**Values:** EAR99, ITAR, Dual-Use, etc.
**Purpose:** International trade compliance

**AISET Implementation:**
- Export control database integration
- ECCN (Export Control Classification Number) tracking
- ITAR flagging and access controls
- Export license requirement alerts

---

### Safety & Security Fields (for Critical Systems)

#### 32. Safety Classification

**Values:** Safety-Critical, Safety-Related, Non-Safety
**Purpose:** Identifies items requiring safety assessment

**AISET Implementation:**
- Safety classification inherited from requirements or FHA (Functional Hazard Assessment)
- Safety-critical CIs require additional verification
- Safety assessment linkage (FTA, FMEA, etc.)

---

#### 33. Security Classification

**Values:** Security-Critical, Security-Relevant, Non-Security
**Purpose:** Cybersecurity management

**AISET Implementation:**
- Security classification per DO-326A/ED-202A
- Threat modeling linkage
- Security verification requirements
- Cybersecurity controls tracking

---

#### 34. Failure Mode Impact

**Content:** Brief summary of potential failure impact
**Purpose:** Risk management and prioritization

**AISET Implementation:**
- Links to FMEA/FTA analyses
- Failure severity classification
- Mitigation strategy tracking
- Risk score calculation

---

## Example CI Table Entry

| Field | Value |
|-------|-------|
| **CI ID** | SYS-SW-FCC-001 |
| **CI Name** | Flight Control Computer - Main Software |
| **Type** | Software (Executable Object Code) |
| **Version** | 3.2.1 |
| **Baseline Status** | Released |
| **Control Level** | Level 1 (Customer Approval Required) |
| **Change Status** | Change Controlled |
| **Owner** | Software Engineering Team |
| **Custodian** | Git Repo: projects/fcc/main |
| **Parent CI** | SYS-FCC-001 (Flight Control Computer) |
| **Child CIs** | SYS-SW-FCC-001-A (Boot Loader), SYS-SW-FCC-001-B (Application) |
| **Interface CIs** | HW-FCC-PROC-001 (Processor Board), SYS-SW-NAV-002 (Navigation SW) |
| **Requirements** | SYS-REQ-045, SYS-REQ-067, SYS-REQ-089 |
| **DAL** | DAL A (DO-178C) |
| **Standards** | DO-178C, DO-326A (Security) |
| **Verification Status** | Verified |
| **Cert Status** | Certified (EASA) |
| **Last Change** | 2024-09-15 |
| **Change Ref** | ECR-2024-234 |
| **Change Summary** | v3.2.1: Fixed FDIR logic for dual sensor failure |
| **Deviation** | None |
| **Lifecycle Phase** | Production |
| **Effectivity** | Aircraft S/N 2500 and subsequent |
| **Interchangeability** | Not interchangeable with v3.1.x (structural change) |
| **Associated Docs** | SDD-FCC-001 (Design), STP-FCC-001 (Test), SAS-FCC-001 (Cert) |
| **Data Rights** | Proprietary - Company XYZ |
| **Export Control** | ITAR Category VIII(h) |
| **Safety Class** | Safety-Critical |
| **Failure Impact** | Loss of flight control (Catastrophic) |

---

## Best Practices for CI Table Management

### 1. Granularity

**Too Coarse:**
- Lose traceability and change impact visibility
- Example: "All flight control software" as one CI

**Too Fine:**
- Administrative burden becomes unmanageable
- Example: Every function in source code as separate CI

**Sweet Spot:**
- Items that change independently and require formal approval
- Compiled software modules, hardware assemblies, design documents
- Rule of thumb: 50-500 CIs for typical aerospace product

---

### 2. Unique Identification

**Best Practices:**
- Never reuse CI IDs (retired IDs marked obsolete, not deleted)
- Use structured naming conventions (hierarchical, readable)
- Consider product lifecycle (IDs remain valid for 20+ years)
- Plan for product families (shared CIs across variants)

**Example Naming Convention:**
```
[SYSTEM]-[TYPE]-[SUBSYSTEM]-[SEQUENCE]

SYS-SW-FCC-001   = System / Software / Flight Control Computer / Item 001
HW-PCBA-PWR-023  = Hardware / PCBA / Power / Item 023
DOC-REQ-SYS-005  = Documentation / Requirements / System / Item 005
```

---

### 3. Tool Integration

**AISET integrates with:**
- **PLM (Product Lifecycle Management)** systems
- **Version control systems** (Git, SVN, Perforce)
- **Change management tools** (Jira, ServiceNow)
- **Requirements management tools** (DOORS, Polarion)
- **Test management tools** (TestRail, qTest)

**Benefits:**
- Automatic CI data synchronization
- Single source of truth
- Reduced manual data entry
- Real-time status updates

---

### 4. Maintenance

**Regular Activities:**
- **Quarterly audits:** Verify CI data accuracy
- **Automated status updates:** From linked systems
- **Clear ownership:** Every CI has active owner
- **Training:** All team members understand CI management

**AISET Automated Maintenance:**
- Orphan CI detection (no parent, no requirements)
- Stale CI detection (no changes in X years, still "In Development")
- Missing traceability alerts
- Inconsistency detection (child DAL higher than parent)

---

### 5. Scalability

**Start Simple:**
- Begin with core mandatory fields
- Add fields as project matures
- Don't try to fill all 34+ fields at once

**Scale Up:**
- Use database (not spreadsheet) for >100 CIs
- Plan for search and filtering capabilities
- Consider reporting needs upfront
- Design for multi-project environments

**AISET Scalability:**
- Supports projects from 10 to 10,000+ CIs
- Custom views per user role
- Batch operations for bulk updates
- Import/export for data migration

---

## Mandatory vs. Optional Fields

### Always Required (Core Set)

✅ **Must Have for ALL CIs:**
1. CI Identifier
2. CI Name
3. CI Type
4. Version/Revision
5. Baseline Status
6. Owner
7. Configuration Control Level

---

### Required for Safety-Critical Products

✅ **Must Have for DAL A-C, SIL 2-4, ASIL B-D:**
8. Development Assurance Level
9. Safety Classification
10. Verification Status
11. Certification Status
12. Requirements Traceability
13. Applicable Standards

---

### Highly Recommended

⭐ **Should Have for Most Projects:**
14. Parent/Child relationships
15. Change history
16. Associated documentation
17. Change control status
18. Last change date/reference

---

### Optional (Depends on Domain/Needs)

📋 **Add If Applicable:**
- Export control (aerospace, defense)
- Supplier information (hardware, purchased items)
- Effectivity (production systems)
- Security classification (connected systems, cybersecurity)
- Material/technology (obsolescence-prone hardware)
- Interchangeability (maintainable systems)

---

## AISET CI Management Features

### Automated CI Lifecycle

AISET automates CI management throughout the lifecycle:

1. **CI Creation:** AISET-AI identifies CIs from user requirements and design documents
2. **Automatic Classification:** AI suggests CI type, DAL, and applicable standards
3. **Traceability Generation:** Auto-links CIs to requirements, tests, documents
4. **Change Impact Analysis:** Shows which CIs are affected by a change
5. **Baseline Management:** Automates baseline creation and approval workflows
6. **Compliance Reporting:** Generates CI reports for certification authorities

### CI Table Views

AISET provides multiple views of CI data:

- **Hierarchical View:** Product structure tree
- **BOM View:** Bill of Materials with quantities
- **Traceability View:** Requirements ↔ CIs ↔ Tests
- **Change View:** CIs affected by change request
- **Verification View:** CI verification status dashboard
- **Certification View:** CI certification package status

### Search and Filtering

AISET supports advanced CI search:

- Full-text search across all fields
- Filter by type, status, owner, DAL, lifecycle phase
- Saved searches and custom views
- Export filtered results to Excel/CSV

---

## Integration with Standards

### DO-178C/DO-254 (Aerospace Software/Hardware)

**CI Requirements from DO-178C/DO-254:**
- Software Configuration Index (SCI)
- Software Life Cycle Environment Configuration Index (SECI)
- Hardware Configuration Index (HCI)
- Problem Reports (PR)
- Software Configuration Management Records (SCMR)

**AISET Implementation:**
- CI table serves as Configuration Index
- Automatic SCI/HCI generation for certification
- PR tracking linked to CIs
- SCMR audit trail

---

### ISO 26262 (Automotive)

**Configuration Management Requirements:**
- Configuration items identified for each safety element
- Traceability to safety requirements
- Change management with impact analysis
- Version control for all work products

**AISET Implementation:**
- ASIL classification per CI
- Safety requirement traceability
- Automotive SPICE compliance reporting

---

### IEC 62304 (Medical Device Software)

**Configuration Management Requirements:**
- Software item identification
- Controlled changes to software items
- Traceability of software items to system requirements
- Software configuration before release

**AISET Implementation:**
- Medical device class per CI
- FDA compliance package generation
- Design History File (DHF) automation

---

## Conclusion

Configuration Management is not just "version control" – it's a comprehensive discipline that ensures:
- ✅ Traceability from requirements to delivered product
- ✅ Control over changes (what, when, why, by whom)
- ✅ Reproducibility (ability to rebuild/recreate any version)
- ✅ Auditability (certification authorities can verify compliance)

AISET automates CI management to reduce engineering overhead while maintaining full compliance with safety and certification standards.

---

**Document Status:** Active
**Review Frequency:** Annually or when standards are updated
**Owner:** AISET Product Team
**Approvals:** TBD
