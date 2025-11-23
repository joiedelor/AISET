{# Software Requirements Specification Template #}
{# Traceability: REQ-AG-001, REQ-AG-002 #}

# Software Requirements Specification
## {{ project.name }}

---

## Document Control

| Item | Value |
|------|-------|
| Document ID | {{ project.project_code or project.name | replace(' ', '-') | upper }}-SRS-001 |
| Version | {{ document.version | default('1.0') }} |
| Date | {{ document.generated_at | date if document.generated_at else 'DRAFT' }} |
| Status | {{ document.status | default('Generated - Needs Review') }} |
| Project | {{ project.name }} |
| Domain | {{ project.domain | default('Not specified') | title }} |
{% if project.dal_level %}
| Assurance Level | {{ project.dal_level }} |
{% endif %}

### Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| {{ document.version | default('1.0') }} | {{ document.generated_at | date if document.generated_at else 'TBD' }} | AISET | Initial generation |

---

## 1. Introduction

### 1.1 Purpose

This document specifies the software requirements for **{{ project.name }}**.

{% if project.description %}
### 1.2 Scope

{{ project.description }}
{% endif %}

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| SRS | Software Requirements Specification |
| HLR | High-Level Requirement |
| LLR | Low-Level Requirement |
{% if project.domain == 'aerospace' %}
| DAL | Design Assurance Level (DO-178C) |
| FHA | Functional Hazard Assessment |
{% elif project.domain == 'automotive' %}
| ASIL | Automotive Safety Integrity Level (ISO 26262) |
{% elif project.domain == 'medical' %}
| IEC 62304 | Medical Device Software Lifecycle |
{% endif %}

### 1.4 References

{% if standards %}
| Document | Version | Description |
|----------|---------|-------------|
{% for std in standards %}
| {{ std.name }} | {{ std.version | default('-') }} | {{ std.description | default('-') }} |
{% endfor %}
{% else %}
*No standards references defined*
{% endif %}

---

## 2. Overall Description

### 2.1 Product Perspective

{% if project.product_type %}
**Product Type:** {{ project.product_type | title }}
{% endif %}

{% if project.initialization_context %}
{% if project.initialization_context.development_process %}
**Development Process:** {{ project.initialization_context.development_process | replace('_', ' ') | title }}
{% endif %}
{% if project.initialization_context.current_lifecycle_phase %}
**Current Phase:** {{ project.initialization_context.current_lifecycle_phase | title }}
{% endif %}
{% endif %}

### 2.2 Product Functions

*Product functions to be derived from requirements below.*

### 2.3 User Characteristics

*User characteristics to be defined.*

### 2.4 Constraints

{% if project.safety_critical %}
- **Safety-Critical System**: This system is safety-critical and requires rigorous development processes.
{% if project.dal_level %}
- **Assurance Level**: {{ project.dal_level }} - All development activities must comply with associated objectives.
{% endif %}
{% endif %}

### 2.5 Assumptions and Dependencies

*Assumptions and dependencies to be defined.*

---

## 3. Functional Requirements

{% set functional_reqs = requirements | selectattr("type", "equalto", "functional") | list %}
{% if functional_reqs %}
{% for req in functional_reqs | sort(attribute="requirement_id") %}

### {{ req.requirement_id }}: {{ req.title | default("Untitled") }}

**Statement:** {{ req.description }}

| Attribute | Value |
|-----------|-------|
| Priority | {{ req.priority | default("Medium") }} |
| Status | {{ req.status | default("Draft") }} |
| Rationale | {{ req.rationale | default("Not specified") }} |
| Verification Method | {{ req.verification_method | default("Test") }} |
{% if req.source %}
| Source | {{ req.source }} |
{% endif %}

---

{% endfor %}
{% else %}
*No functional requirements defined yet.*
{% endif %}

---

## 4. Performance Requirements

{% set performance_reqs = requirements | selectattr("type", "equalto", "performance") | list %}
{% if performance_reqs %}
{% for req in performance_reqs | sort(attribute="requirement_id") %}

### {{ req.requirement_id }}: {{ req.title | default("Untitled") }}

**Statement:** {{ req.description }}

| Attribute | Value |
|-----------|-------|
| Priority | {{ req.priority | default("Medium") }} |
| Status | {{ req.status | default("Draft") }} |

---

{% endfor %}
{% else %}
*No performance requirements defined yet.*
{% endif %}

---

## 5. Interface Requirements

{% set interface_reqs = requirements | selectattr("type", "equalto", "interface") | list %}
{% if interface_reqs %}
{% for req in interface_reqs | sort(attribute="requirement_id") %}

### {{ req.requirement_id }}: {{ req.title | default("Untitled") }}

**Statement:** {{ req.description }}

| Attribute | Value |
|-----------|-------|
| Priority | {{ req.priority | default("Medium") }} |
| Status | {{ req.status | default("Draft") }} |

---

{% endfor %}
{% else %}
*No interface requirements defined yet.*
{% endif %}

---

## 6. Design Constraints

{% set constraint_reqs = requirements | selectattr("type", "equalto", "constraint") | list %}
{% if constraint_reqs %}
{% for req in constraint_reqs | sort(attribute="requirement_id") %}

### {{ req.requirement_id }}: {{ req.title | default("Untitled") }}

**Statement:** {{ req.description }}

---

{% endfor %}
{% else %}
*No design constraints defined yet.*
{% endif %}

---

## 7. Safety Requirements

{% set safety_reqs = requirements | selectattr("type", "equalto", "safety") | list %}
{% if safety_reqs %}
{% for req in safety_reqs | sort(attribute="requirement_id") %}

### {{ req.requirement_id }}: {{ req.title | default("Untitled") }}

**Statement:** {{ req.description }}

| Attribute | Value |
|-----------|-------|
| Priority | {{ req.priority | default("High") }} |
| Status | {{ req.status | default("Draft") }} |
{% if req.safety_impact %}
| Safety Impact | {{ req.safety_impact }} |
{% endif %}

---

{% endfor %}
{% else %}
{% if project.safety_critical %}
*Safety requirements to be derived from safety analysis.*
{% else %}
*No safety requirements defined (non-safety-critical system).*
{% endif %}
{% endif %}

---

## 8. Quality Attributes

### 8.1 Reliability Requirements

{% set reliability_reqs = requirements | selectattr("type", "equalto", "reliability") | list %}
{% if reliability_reqs %}
{% for req in reliability_reqs | sort(attribute="requirement_id") %}
- **{{ req.requirement_id }}:** {{ req.description }}
{% endfor %}
{% else %}
*No reliability requirements defined yet.*
{% endif %}

### 8.2 Maintainability Requirements

{% set maintainability_reqs = requirements | selectattr("type", "equalto", "maintainability") | list %}
{% if maintainability_reqs %}
{% for req in maintainability_reqs | sort(attribute="requirement_id") %}
- **{{ req.requirement_id }}:** {{ req.description }}
{% endfor %}
{% else %}
*No maintainability requirements defined yet.*
{% endif %}

---

## Appendix A: Requirements Summary

| Req ID | Title | Type | Priority | Status |
|--------|-------|------|----------|--------|
{% for req in requirements | sort(attribute="requirement_id") %}
| {{ req.requirement_id }} | {{ req.title | default("-") | truncate(40) }} | {{ req.type | default("-") }} | {{ req.priority | default("-") }} | {{ req.status | default("-") }} |
{% endfor %}

**Total Requirements:** {{ requirements | length }}

---

## Appendix B: Traceability

*Traceability information maintained in Requirements Traceability Matrix (RTM).*

---

**Generated by AISET Process Engine**

**Generation timestamp:** {{ document.generated_at | datetime if document.generated_at else 'N/A' }}
