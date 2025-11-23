{# Requirements Traceability Matrix Template #}
{# Traceability: REQ-AG-004 #}

# Requirements Traceability Matrix
## {{ project.name }}

---

## Document Control

| Item | Value |
|------|-------|
| Document ID | {{ project.project_code or project.name | replace(' ', '-') | upper }}-RTM-001 |
| Version | {{ document.version | default('1.0') }} |
| Date | {{ document.generated_at | date if document.generated_at else 'DRAFT' }} |
| Status | {{ document.status | default('Generated - Needs Review') }} |
| Project | {{ project.name }} |

---

## 1. Purpose

This Requirements Traceability Matrix (RTM) provides bidirectional traceability between:
- System Requirements and Software Requirements
- Software Requirements and Design Components
- Software Requirements and Test Cases

---

## 2. Traceability Summary

### 2.1 Coverage Statistics

| Metric | Value | Percentage |
|--------|-------|------------|
| Total Requirements | {{ coverage.total_requirements | default(requirements | length) }} | 100% |
| Requirements with Design | {{ coverage.with_design | default(0) }} | {{ coverage.design_coverage | default(0) }}% |
| Requirements with Tests | {{ coverage.with_tests | default(0) }} | {{ coverage.test_coverage | default(0) }}% |
| Fully Traced Requirements | {{ coverage.fully_traced | default(0) }} | {{ coverage.full_coverage | default(0) }}% |

### 2.2 Coverage Status

{% if coverage.design_coverage | default(0) | int >= 80 %}
- Design Coverage: **ACCEPTABLE** ({{ coverage.design_coverage | default(0) }}%)
{% else %}
- Design Coverage: **NEEDS WORK** ({{ coverage.design_coverage | default(0) }}%)
{% endif %}

{% if coverage.test_coverage | default(0) | int >= 80 %}
- Test Coverage: **ACCEPTABLE** ({{ coverage.test_coverage | default(0) }}%)
{% else %}
- Test Coverage: **NEEDS WORK** ({{ coverage.test_coverage | default(0) }}%)
{% endif %}

---

## 3. Requirements to Design Traceability

| Requirement ID | Requirement Title | Design Component(s) | Trace Type | Status |
|---------------|-------------------|---------------------|------------|--------|
{% for trace in traces %}
{% if trace.type == 'requirement_design' %}
| {{ trace.requirement_id }} | {{ trace.requirement_title | truncate(30) }} | {{ trace.design_ids | join(', ') if trace.design_ids else '-' }} | {{ trace.trace_type | default('derives') }} | {{ trace.status | default('Pending') }} |
{% endif %}
{% else %}
{% for req in requirements | sort(attribute="requirement_id") %}
| {{ req.requirement_id }} | {{ req.title | default('-') | truncate(30) }} | - | - | Not Traced |
{% endfor %}
{% endfor %}

---

## 4. Requirements to Test Traceability

| Requirement ID | Requirement Title | Test Case(s) | Test Status | Verification Method |
|---------------|-------------------|--------------|-------------|---------------------|
{% for trace in traces %}
{% if trace.type == 'requirement_test' %}
| {{ trace.requirement_id }} | {{ trace.requirement_title | truncate(30) }} | {{ trace.test_ids | join(', ') if trace.test_ids else '-' }} | {{ trace.test_status | default('Not Run') }} | {{ trace.verification_method | default('Test') }} |
{% endif %}
{% else %}
{% for req in requirements | sort(attribute="requirement_id") %}
| {{ req.requirement_id }} | {{ req.title | default('-') | truncate(30) }} | - | Not Tested | {{ req.verification_method | default('Test') }} |
{% endfor %}
{% endfor %}

---

## 5. Design to Test Traceability

| Design Component | Component Name | Test Case(s) | Test Status |
|-----------------|----------------|--------------|-------------|
{% for trace in traces %}
{% if trace.type == 'design_test' %}
| {{ trace.design_id }} | {{ trace.design_name | truncate(30) }} | {{ trace.test_ids | join(', ') if trace.test_ids else '-' }} | {{ trace.test_status | default('Not Run') }} |
{% endif %}
{% else %}
*No design-to-test traces defined yet.*
{% endfor %}

---

## 6. Gap Analysis

### 6.1 Requirements Without Design Allocation

{% if gaps.requirements_without_design %}
| Requirement ID | Title | Priority | Action Required |
|---------------|-------|----------|-----------------|
{% for gap in gaps.requirements_without_design %}
| {{ gap.requirement_id }} | {{ gap.title | truncate(30) }} | {{ gap.priority | default('Medium') }} | Allocate to design component |
{% endfor %}
{% else %}
*All requirements have design allocation.*
{% endif %}

### 6.2 Requirements Without Test Coverage

{% if gaps.requirements_without_tests %}
| Requirement ID | Title | Verification Method | Action Required |
|---------------|-------|---------------------|-----------------|
{% for gap in gaps.requirements_without_tests %}
| {{ gap.requirement_id }} | {{ gap.title | truncate(30) }} | {{ gap.verification_method | default('Test') }} | Create test case |
{% endfor %}
{% else %}
*All requirements have test coverage.*
{% endif %}

### 6.3 Orphan Design Components

{% if gaps.orphan_design %}
| Design ID | Name | Action Required |
|-----------|------|-----------------|
{% for gap in gaps.orphan_design %}
| {{ gap.design_id }} | {{ gap.name | truncate(30) }} | Link to requirement or remove |
{% endfor %}
{% else %}
*No orphan design components.*
{% endif %}

### 6.4 Orphan Test Cases

{% if gaps.orphan_tests %}
| Test ID | Name | Action Required |
|---------|------|-----------------|
{% for gap in gaps.orphan_tests %}
| {{ gap.test_id }} | {{ gap.name | truncate(30) }} | Link to requirement or remove |
{% endfor %}
{% else %}
*No orphan test cases.*
{% endif %}

---

## 7. Trace Status Legend

| Status | Description |
|--------|-------------|
| Complete | Fully traced with verified links |
| Partial | Some traces missing |
| Not Traced | No trace links established |
| Pending | Trace under review |
| Approved | Trace verified and approved |

---

**Generated by AISET Process Engine**

**Generation timestamp:** {{ document.generated_at | datetime if document.generated_at else 'N/A' }}
