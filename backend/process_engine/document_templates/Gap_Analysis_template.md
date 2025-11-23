{# Gap Analysis Report Template #}
{# Traceability: REQ-AG-005 #}

# Gap Analysis Report
## {{ project.name }}

---

## Document Control

| Item | Value |
|------|-------|
| Document ID | {{ project.project_code or project.name | replace(' ', '-') | upper }}-GAP-001 |
| Version | {{ document.version | default('1.0') }} |
| Date | {{ document.generated_at | date if document.generated_at else 'DRAFT' }} |
| Status | {{ document.status | default('Generated - Needs Review') }} |
| Project | {{ project.name }} |

---

## 1. Executive Summary

This report identifies gaps in the requirements, design, and verification coverage for **{{ project.name }}**.

### 1.1 Gap Summary

| Gap Category | Count | Severity |
|--------------|-------|----------|
| Requirements without Design | {{ gaps.requirements_without_design | length if gaps.requirements_without_design else 0 }} | {% if gaps.requirements_without_design | length | default(0) > 0 %}High{% else %}None{% endif %} |
| Requirements without Tests | {{ gaps.requirements_without_tests | length if gaps.requirements_without_tests else 0 }} | {% if gaps.requirements_without_tests | length | default(0) > 0 %}High{% else %}None{% endif %} |
| Orphan Design Components | {{ gaps.design_without_requirements | length if gaps.design_without_requirements else 0 }} | {% if gaps.design_without_requirements | length | default(0) > 0 %}Medium{% else %}None{% endif %} |
| Orphan Test Cases | {{ gaps.orphan_tests | length if gaps.orphan_tests else 0 }} | {% if gaps.orphan_tests | length | default(0) > 0 %}Low{% else %}None{% endif %} |
| CIs without Requirements | {{ gaps.cis_without_requirements | length if gaps.cis_without_requirements else 0 }} | {% if gaps.cis_without_requirements | length | default(0) > 0 %}Medium{% else %}None{% endif %} |

### 1.2 Overall Status

{% set total_gaps = (gaps.requirements_without_design | length | default(0)) + (gaps.requirements_without_tests | length | default(0)) + (gaps.design_without_requirements | length | default(0)) %}
{% if total_gaps == 0 %}
**STATUS: COMPLIANT** - No critical gaps identified.
{% elif total_gaps <= 5 %}
**STATUS: MINOR GAPS** - {{ total_gaps }} gaps requiring attention.
{% else %}
**STATUS: SIGNIFICANT GAPS** - {{ total_gaps }} gaps requiring immediate attention.
{% endif %}

---

## 2. Requirements Analysis

### 2.1 Requirements Statistics

| Metric | Value |
|--------|-------|
| Total Requirements | {{ summary.total_requirements | default(0) }} |
| Functional Requirements | {{ summary.functional_count | default(0) }} |
| Non-Functional Requirements | {{ summary.non_functional_count | default(0) }} |
| Safety Requirements | {{ summary.safety_count | default(0) }} |

### 2.2 Requirements Coverage

| Coverage Type | Covered | Not Covered | Percentage |
|--------------|---------|-------------|------------|
| Design Allocation | {{ summary.reqs_with_design | default(0) }} | {{ summary.reqs_without_design | default(0) }} | {{ summary.design_coverage | default(0) }}% |
| Test Coverage | {{ summary.reqs_with_tests | default(0) }} | {{ summary.reqs_without_tests | default(0) }} | {{ summary.test_coverage | default(0) }}% |
| Full Traceability | {{ summary.fully_traced | default(0) }} | {{ summary.not_fully_traced | default(0) }} | {{ summary.full_trace_coverage | default(0) }}% |

---

## 3. Gap Details

### 3.1 Requirements Without Design Allocation

{% if gaps.requirements_without_design %}
These requirements have not been allocated to any design component.

| Req ID | Title | Type | Priority | Recommended Action |
|--------|-------|------|----------|-------------------|
{% for gap in gaps.requirements_without_design %}
| {{ gap.requirement_id }} | {{ gap.title | default('-') | truncate(35) }} | {{ gap.type | default('-') }} | {{ gap.priority | default('Medium') }} | Create design component |
{% endfor %}

**Action Required:** Allocate each requirement to appropriate design component(s).
{% else %}
*All requirements have design allocation. No gaps in this category.*
{% endif %}

---

### 3.2 Requirements Without Test Coverage

{% if gaps.requirements_without_tests %}
These requirements have no associated test cases.

| Req ID | Title | Verification Method | Priority | Recommended Action |
|--------|-------|---------------------|----------|-------------------|
{% for gap in gaps.requirements_without_tests %}
| {{ gap.requirement_id }} | {{ gap.title | default('-') | truncate(35) }} | {{ gap.verification_method | default('Test') }} | {{ gap.priority | default('Medium') }} | Create test case(s) |
{% endfor %}

**Action Required:** Create test cases for each requirement based on verification method.
{% else %}
*All requirements have test coverage. No gaps in this category.*
{% endif %}

---

### 3.3 Orphan Design Components

{% if gaps.design_without_requirements %}
These design components are not linked to any requirements.

| Design ID | Name | Type | Recommended Action |
|-----------|------|------|-------------------|
{% for gap in gaps.design_without_requirements %}
| {{ gap.component_id }} | {{ gap.name | default('-') | truncate(35) }} | {{ gap.type | default('-') }} | Link to requirement or justify |
{% endfor %}

**Action Required:** Either link to appropriate requirements or document justification for existence.
{% else %}
*All design components are linked to requirements. No orphans.*
{% endif %}

---

### 3.4 Orphan Test Cases

{% if gaps.orphan_tests %}
These test cases are not linked to any requirements.

| Test ID | Name | Type | Recommended Action |
|---------|------|------|-------------------|
{% for gap in gaps.orphan_tests %}
| {{ gap.test_id }} | {{ gap.name | default('-') | truncate(35) }} | {{ gap.type | default('-') }} | Link to requirement or remove |
{% endfor %}

**Action Required:** Either link to appropriate requirements or remove if no longer needed.
{% else %}
*All test cases are linked to requirements. No orphans.*
{% endif %}

---

### 3.5 Configuration Items Without Requirements

{% if gaps.cis_without_requirements %}
These Configuration Items have no allocated requirements.

| CI ID | Name | Type | Recommended Action |
|-------|------|------|-------------------|
{% for gap in gaps.cis_without_requirements %}
| {{ gap.display_id }} | {{ gap.name | default('-') | truncate(35) }} | {{ gap.ci_type | default('-') }} | Allocate requirements or justify |
{% endfor %}

**Action Required:** Allocate requirements to each CI or document justification.
{% else %}
*All Configuration Items have allocated requirements.*
{% endif %}

---

## 4. Recommendations

### 4.1 Immediate Actions (High Priority)

{% if gaps.requirements_without_design or gaps.requirements_without_tests %}
1. **Complete Design Allocation** - Ensure all requirements are allocated to design components
2. **Complete Test Coverage** - Create test cases for all untested requirements
{% if project.safety_critical %}
3. **Safety Analysis Review** - Review safety requirements for completeness
{% endif %}
{% else %}
*No immediate actions required.*
{% endif %}

### 4.2 Medium Priority Actions

{% if gaps.design_without_requirements or gaps.cis_without_requirements %}
1. **Review Orphan Components** - Evaluate orphan design components for linking or removal
2. **CI Allocation Review** - Ensure all CIs have appropriate requirement allocation
{% else %}
*No medium priority actions required.*
{% endif %}

### 4.3 Low Priority Actions

{% if gaps.orphan_tests %}
1. **Test Case Cleanup** - Review and link or remove orphan test cases
{% else %}
*No low priority actions required.*
{% endif %}

---

## 5. Compliance Impact

{% if project.safety_critical %}
### 5.1 Safety-Critical Compliance

| Standard | Requirement | Status | Impact |
|----------|-------------|--------|--------|
{% if project.domain == 'aerospace' %}
| DO-178C 5.1.2 | HLR Traceability | {% if summary.design_coverage | default(0) >= 100 %}Compliant{% else %}Gap{% endif %} | {{ 'None' if summary.design_coverage | default(0) >= 100 else 'High - Required for certification' }} |
| DO-178C 6.3.4 | Test Coverage | {% if summary.test_coverage | default(0) >= 100 %}Compliant{% else %}Gap{% endif %} | {{ 'None' if summary.test_coverage | default(0) >= 100 else 'High - Required for certification' }} |
{% elif project.domain == 'automotive' %}
| ISO 26262-6 | Requirements Tracing | {% if summary.design_coverage | default(0) >= 100 %}Compliant{% else %}Gap{% endif %} | {{ 'None' if summary.design_coverage | default(0) >= 100 else 'High - Required for ASIL compliance' }} |
{% endif %}

{% endif %}

---

## 6. Appendix: Gap Resolution Tracking

| Gap ID | Category | Item ID | Status | Assigned To | Due Date | Resolution |
|--------|----------|---------|--------|-------------|----------|------------|
{% set gap_counter = namespace(count=1) %}
{% for gap in gaps.requirements_without_design | default([]) %}
| GAP-{{ '%03d' | format(gap_counter.count) }} | Req-Design | {{ gap.requirement_id }} | Open | TBD | TBD | - |
{% set gap_counter.count = gap_counter.count + 1 %}
{% endfor %}
{% for gap in gaps.requirements_without_tests | default([]) %}
| GAP-{{ '%03d' | format(gap_counter.count) }} | Req-Test | {{ gap.requirement_id }} | Open | TBD | TBD | - |
{% set gap_counter.count = gap_counter.count + 1 %}
{% endfor %}

---

**Generated by AISET Process Engine**

**Generation timestamp:** {{ document.generated_at | datetime if document.generated_at else 'N/A' }}
