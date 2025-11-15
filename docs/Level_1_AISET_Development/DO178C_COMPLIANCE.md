# DO-178C Compliance Documentation

## Overview

This document describes how AISET (AI Systems Engineering Tool) implements DO-178C requirements for software considerations in airborne systems and equipment certification.

**Document ID:** DO178C-AISET-001
**Version:** 1.0
**Date:** November 2025
**Classification:** Technical Documentation

---

## 1. Introduction

### 1.1 Purpose

This document demonstrates how AISET meets DO-178C objectives for tool qualification and provides traceability from requirements through implementation and verification.

### 1.2 Scope

AISET is designed as a **Development Tool** and potentially a **Verification Tool** per DO-178C Section 12.2, depending on usage context.

### 1.3 Applicable Documents

- RTCA DO-178C: Software Considerations in Airborne Systems and Equipment Certification
- RTCA DO-330: Software Tool Qualification Considerations
- IEEE 29148: Requirements Engineering
- ISO/IEC 12207: Software Life Cycle Processes

---

## 2. Tool Classification

### 2.1 Tool Qualification Level

AISET supports projects at all DO-178C levels (A through E):

- **Level A (Catastrophic):** Full traceability, strictest validation
- **Level B (Hazardous):** Complete traceability, comprehensive validation
- **Level C (Major):** Full traceability (default configuration)
- **Level D (Minor):** Reduced traceability requirements
- **Level E (No Effect):** Minimal requirements

### 2.2 Tool Impact

**Development Tool Impact:**
- Automates requirements elicitation and documentation
- Generates traceability matrices
- Produces certification artifacts (SRS, SDD, RTM)

**Verification Tool Impact:**
- Validates requirements quality
- Detects traceability gaps
- Verifies coverage completeness

---

## 3. DO-178C Objectives Coverage

### 3.1 Requirements (Section 5)

| Objective | Requirement | AISET Implementation | Traceability |
|-----------|-------------|---------------------|--------------|
| A-1 | High-level requirements developed | AI-assisted elicitation, manual validation | REQ-REQ-001 to REQ-REQ-008 |
| A-2 | Derived requirements provided to system | Requirement decomposition with parent-child | REQ-HIER-001 |
| A-3 | Requirements are traceable | Bidirectional traceability tables | REQ-TRACE-001 to REQ-TRACE-019 |
| A-4 | Requirements are accurate and consistent | AI validation + human approval | REQ-VALID-001 to REQ-VALID-006 |

### 3.2 Design (Section 6)

| Objective | Requirement | AISET Implementation | Traceability |
|-----------|-------------|---------------------|--------------|
| B-1 | Low-level requirements developed | Design component documentation | REQ-DESIGN-001, REQ-DESIGN-002 |
| B-2 | Design is traceable to requirements | Requirements-design trace links | REQ-TRACE-004, REQ-TRACE-009 |
| B-3 | Design is verifiable | Test case generation and linking | REQ-TEST-001, REQ-TEST-002 |

### 3.3 Verification (Section 8)

| Objective | Requirement | AISET Implementation | Traceability |
|-----------|-------------|---------------------|--------------|
| D-1 | Test cases developed | Test case management | REQ-TEST-001, REQ-TEST-002 |
| D-2 | Test coverage achieved | Coverage analysis and gap detection | REQ-TRACE-012, REQ-TRACE-013 |
| D-3 | Test results captured | Test execution tracking | REQ-TEST-002 |

### 3.4 Traceability (Section 6.3)

**Complete Bidirectional Traceability:**

```
System Requirements
        ↓↑
High-Level Requirements (AISET Requirements)
        ↓↑
Low-Level Requirements (AISET Design Components)
        ↓↑
Source Code (External - referenced by file_path)
        ↓↑
Test Cases (AISET Test Cases)
```

**AISET Traceability Tables:**
- `requirements_design_trace`: Requirements ↔ Design
- `requirements_test_trace`: Requirements ↔ Tests
- `design_test_trace`: Design ↔ Tests

---

## 4. Audit Trail and Configuration Management

### 4.1 Version History

Every change to critical entities is tracked in `version_history` table:

- **What changed:** Full before/after snapshots (JSON)
- **Who changed it:** User identification
- **When changed:** Timestamp (UTC)
- **Why changed:** Rationale and summary
- **Version number:** Incremental versioning

**Traceability:** REQ-AUDIT-008, REQ-VERSION-001

### 4.2 Change Management

All changes go through controlled workflow via `change_requests` table:

1. **Draft:** Initial proposal
2. **Pending Review:** Awaiting approval
3. **Approved:** Ready for implementation
4. **Implemented:** Changes applied
5. **Rejected/Cancelled:** Not implemented

**Impact Analysis:**
- Affected requirements, design, tests
- Risk assessment
- Business and technical justification

**Traceability:** REQ-CHANGE-001, REQ-IMPACT-001, REQ-APPROVAL-001

### 4.3 Human-in-the-Loop Validation

All AI extractions require human validation:

1. AI extracts requirement with confidence score
2. Human reviews extraction in `ai_extracted_entities`
3. Decision recorded in `validation_decisions`:
   - **Approved:** Entity created in database
   - **Rejected:** Not created (rationale required)
   - **Modified:** Approved with changes (diff tracked)

**Traceability:** REQ-VALID-002, REQ-VALID-003, REQ-HITL-001

---

## 5. Document Generation

### 5.1 Software Requirements Specification (SRS)

Generated from `requirements` table:

- **Format:** Markdown, PDF, HTML, DOCX
- **Content:**
  - All approved requirements
  - Hierarchical organization by type
  - Priority and status
  - Acceptance criteria
  - Rationale
- **Integrity:** SHA-256 hash for verification
- **Audit:** Tracked in `document_exports`

**Traceability:** REQ-DOC-003, REQ-CERT-008

### 5.2 Requirements Traceability Matrix (RTM)

Generated from traceability tables:

- **Coverage Statistics:**
  - Total requirements
  - Fully traced requirements
  - Design coverage percentage
  - Test coverage percentage
- **Matrix Columns:**
  - Requirement ID
  - Title, Type, Priority, Status
  - Linked design components
  - Linked test cases
  - Trace status (✓ complete, ⚠ partial, ✗ missing)

**Traceability:** REQ-DOC-004, REQ-CERT-009

### 5.3 Software Design Description (SDD)

Generated from `design_components` table:

- Component architecture
- Implementation details
- Interface specifications
- Dependencies
- Code references (file path + line number)

**Traceability:** REQ-DOC-002

---

## 6. Quality Assurance

### 6.1 Requirements Quality Validation

Per DO-178C Section 6.3.1, requirements must be:

1. **Unambiguous:** Detect ambiguous words (should, might, could)
2. **Verifiable:** Require acceptance criteria
3. **Complete:** Check for missing rationale
4. **Traceable:** Enforce traceability links
5. **Consistent:** Detect conflicts and gaps

**Implementation:** `RequirementsService.validate_requirement()`

**Quality Score Calculation:**
```
Base Score: 1.0
- 0.20 per critical issue (blocking)
- 0.05 per warning (non-blocking)
+ 0.05 if acceptance criteria present
+ 0.05 if rationale present
```

**Traceability:** REQ-VALID-005, REQ-QA-001

### 6.2 Traceability Gap Detection

Automated gap detection via `TraceabilityService.detect_gaps()`:

**Gap Types:**
- **Missing Design:** Requirement with no design implementation
- **Missing Test:** Requirement with no test coverage
- **Orphan Design:** Design component with no requirement
- **Orphan Test:** Test case with no requirement
- **Incomplete Coverage:** Partial traceability

**Severity Levels:**
- **Critical:** High/critical priority requirement missing tests
- **High:** Any requirement missing design or tests
- **Medium:** Orphan design components
- **Low:** Orphan test cases

**Traceability:** REQ-TRACE-013, REQ-QA-002

---

## 7. Configuration Settings

DO-178C compliance features are configurable via environment variables:

```bash
# Enable complete audit trail
ENABLE_AUDIT_TRAIL=True

# Require approval workflow for all changes
REQUIRE_APPROVAL_WORKFLOW=True

# Enforce strict traceability (block incomplete traces)
TRACEABILITY_STRICT_MODE=True
```

**Production Recommendation:** All three set to `True` for Level A/B/C

**Traceability:** REQ-CONFIG-001, REQ-AUDIT-001

---

## 8. Tool Qualification per DO-330

### 8.1 Tool Operational Requirements (TOR)

1. **Requirements Elicitation:**
   - Accept natural language input
   - Generate structured requirements
   - Request clarifications
   - Extract with confidence scores

2. **Traceability Management:**
   - Create bidirectional links
   - Detect gaps automatically
   - Generate traceability matrix
   - Calculate coverage metrics

3. **Document Generation:**
   - Generate SRS from database
   - Generate RTM from traces
   - Include version control metadata
   - Ensure file integrity (SHA-256)

### 8.2 Tool Qualification Plan

**Qualification Method:** Tool Operational Requirements + Test Cases

**Test Coverage:**
- Unit tests for all services
- Integration tests for workflows
- End-to-end tests for critical paths
- Validation tests for DO-178C compliance

**Traceability:** Each TOR maps to test cases in `test_cases` table

---

## 9. Certification Evidence

### 9.1 Generated Artifacts

For each project, AISET generates:

1. **SRS** - Software Requirements Specification
2. **SDD** - Software Design Description
3. **RTM** - Requirements Traceability Matrix
4. **Test Plan** - Verification approach
5. **Test Report** - Verification results
6. **V&V Report** - Verification & Validation summary

All exports tracked in `document_exports` with SHA-256 hashes.

### 9.2 Audit Evidence

Available for certification authority review:

- Complete conversation logs (`ai_conversations`, `ai_messages`)
- All validation decisions (`validation_decisions`)
- Full version history (`version_history`)
- Change request records (`change_requests`)
- Traceability gap reports (`traceability_gaps`)

---

## 10. Compliance Summary

### 10.1 DO-178C Objectives Met

✅ **Requirements:** Complete with AI assistance + human validation
✅ **Design:** Traceable to requirements
✅ **Traceability:** Bidirectional, automated gap detection
✅ **Verification:** Test cases linked to requirements
✅ **Configuration Management:** Full audit trail
✅ **Quality Assurance:** Automated validation + human oversight
✅ **Documentation:** Automated artifact generation

### 10.2 Certification Level Support

| Level | Supported | Configuration |
|-------|-----------|---------------|
| A (Catastrophic) | ✅ Yes | All compliance features ON |
| B (Hazardous) | ✅ Yes | All compliance features ON |
| C (Major) | ✅ Yes | Default configuration |
| D (Minor) | ✅ Yes | Reduced traceability OK |
| E (No Effect) | ✅ Yes | Minimal requirements |

---

## 11. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-13 | AISET Team | Initial DO-178C compliance documentation |

---

**End of Document**

*This document is version-controlled and tracked in the AISET repository.*
