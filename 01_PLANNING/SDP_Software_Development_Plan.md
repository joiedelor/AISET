# Software Development Plan (SDP)
## AISET - AI Systems Engineering Tool
### DO-178C Compliant

---

**Document Information**
- **Document ID:** SDP-AISET-001
- **Version:** 1.0
- **Date:** 14 Novembre 2025
- **Status:** Draft
- **DAL Level:** D
- **Author:** [Joy Bousquet]
- **Approver:** [Manager/Lead]

---

## 1. PURPOSE AND SCOPE

### 1.1 Purpose
This Software Development Plan (SDP) defines the software development process, standards, and environment for the AI Systems Engineering Tool (AISET) in accordance with DO-178C guidance.

### 1.2 Scope
This plan covers:
- Software development processes and activities
- Software development standards
- Software development environment
- Development tools and their qualification status
- Software lifecycle data to be produced

### 1.3 Software Overview
**AISET** is an AI-assisted tool for systems engineering that helps engineers:
- Capture and structure requirements through conversational AI
- Maintain design traceability
- Generate documentation automatically
- Ensure compliance with engineering standards

**System Architecture:**
- Frontend: React/TypeScript (Port 5173)
- Backend: Python FastAPI (Port 8000)
- Database: PostgreSQL
- AI Engine: LM Studio (Mistral local) + Claude Sonnet 4 API

---

## 2. SOFTWARE LIFECYCLE

### 2.1 Software Lifecycle Model
AISET follows a **Modified V-Model** adapted for agile development with AI assistance.

```
Requirements → Design → Implementation → Unit Test
     ↓            ↓           ↓              ↑
     ↓            ↓     Integration Test ←──┘
     ↓            ↓           ↑
     ↓      System Test ←────┘
     ↓            ↑
  Validation ←───┘
```

### 2.2 Development Phases

#### Phase 1: Requirements Analysis
- **Input:** Stakeholder needs, system requirements
- **Activities:** 
  - Requirements elicitation (AI-assisted)
  - Requirements documentation (SRS)
  - Requirements review
  - Baseline establishment
- **Output:** Software Requirements Specification (SRS)
- **Criteria:** All requirements reviewed and approved

#### Phase 2: Design
- **Input:** Approved SRS
- **Activities:**
  - High-Level Design (architecture)
  - Low-Level Design (detailed components)
  - Design reviews
  - Traceability to requirements
- **Output:** Software Design Description (SDD)
- **Criteria:** Design traces 100% to requirements

#### Phase 3: Implementation
- **Input:** Approved SDD
- **Activities:**
  - Code development (with Claude Code assistance)
  - Code reviews (mandatory)
  - Unit test development
  - Static analysis
- **Output:** Source code + Unit tests
- **Criteria:** 
  - Code complies with coding standards
  - Code reviews completed
  - 100% statement coverage

#### Phase 4: Integration
- **Input:** Unit-tested modules
- **Activities:**
  - Module integration
  - Integration testing
  - Interface verification
- **Output:** Integrated system + Integration test results
- **Criteria:** All interfaces verified

#### Phase 5: System Verification
- **Input:** Integrated system
- **Activities:**
  - System testing
  - Requirements verification
  - Performance testing
- **Output:** Software Verification Results
- **Criteria:** All requirements verified

---

## 3. SOFTWARE DEVELOPMENT STANDARDS

### 3.1 Coding Standards

#### 3.1.1 Python Backend Standards
**Reference:** PEP 8 + DO-178C Adaptations

**Mandatory Rules:**
1. **Naming Conventions**
   - Functions: `snake_case`
   - Classes: `PascalCase`
   - Constants: `UPPER_SNAKE_CASE`
   - Private: prefix with `_`

2. **Documentation**
   - Every function MUST have a docstring with:
     - Purpose
     - Parameters
     - Return value
     - Exceptions
   - Example:
   ```python
   def extract_requirements(user_response: str, context: Dict) -> Dict:
       """
       Extract structured requirements from user natural language response.
       
       Args:
           user_response: User's description in natural language
           context: Project context dictionary
           
       Returns:
           Dictionary containing extracted requirements with confidence scores
           
       Raises:
           ValueError: If user_response is empty
           AIServiceError: If AI extraction fails
       
       Traceability:
           REQ-045: AI shall extract requirements from user responses
       """
   ```

3. **Error Handling**
   - NEVER use bare `except:`
   - Always specify exception types
   - Log all errors with context
   - Example:
   ```python
   try:
       result = ai_service.extract(data)
   except AIServiceError as e:
       logger.error(f"AI extraction failed: {e}", extra={"data": data})
       raise
   ```

4. **Type Hints**
   - MANDATORY for all function signatures
   - Use `typing` module for complex types
   - Example:
   ```python
   from typing import List, Dict, Optional
   
   def process_requirements(
       req_list: List[Dict[str, Any]], 
       project_id: UUID
   ) -> Optional[List[Requirement]]:
       ...
   ```

5. **Complexity Limits**
   - Max cyclomatic complexity: 10
   - Max function length: 50 lines
   - Max file length: 500 lines
   - If exceeded, refactor is MANDATORY

6. **Testing**
   - Every function MUST have unit tests
   - Minimum 90% code coverage
   - Tests MUST be in `tests/` directory mirroring source structure

7. **Forbidden Constructs**
   - `eval()` - NEVER use
   - `exec()` - NEVER use
   - Global mutable state - AVOID
   - Monkey patching - AVOID

#### 3.1.2 TypeScript Frontend Standards
**Reference:** Airbnb Style Guide + DO-178C Adaptations

**Mandatory Rules:**
1. **Naming Conventions**
   - Components: `PascalCase`
   - Functions: `camelCase`
   - Constants: `UPPER_SNAKE_CASE`
   - Interfaces: `PascalCase` with `I` prefix

2. **Type Safety**
   - NEVER use `any` type (exception: gradual migration)
   - Define interfaces for all data structures
   - Example:
   ```typescript
   interface IRequirement {
       id: string;
       title: string;
       description: string;
       type: 'functional' | 'non_functional';
       priority: 'critical' | 'high' | 'medium' | 'low';
   }
   ```

3. **Documentation**
   - TSDoc comments for all exported functions/components
   - Example:
   ```typescript
   /**
    * Fetches requirements from backend API
    * @param projectId - UUID of the project
    * @returns Promise resolving to array of requirements
    * @throws APIError if fetch fails
    * @traceability REQ-102: Frontend shall retrieve requirements
    */
   async function fetchRequirements(projectId: string): Promise<IRequirement[]> {
       ...
   }
   ```

4. **Component Structure**
   - One component per file
   - Props interface defined
   - Functional components preferred
   - Hooks for state management

5. **Error Handling**
   - Try-catch for all async operations
   - User-friendly error messages
   - Log errors to backend

### 3.2 Design Standards

#### 3.2.1 Architectural Principles
1. **Separation of Concerns**
   - Presentation layer (React)
   - Business logic (FastAPI)
   - Data access (PostgreSQL)

2. **Loose Coupling**
   - Services communicate via well-defined APIs
   - No direct database access from frontend

3. **Single Responsibility**
   - Each module/service has ONE clear purpose

4. **Dependency Injection**
   - Use FastAPI's DI system
   - Mock dependencies in tests

#### 3.2.2 Database Design Standards
1. **Naming**
   - Tables: `snake_case`, plural
   - Columns: `snake_case`, descriptive
   - Foreign keys: `referenced_table_id`

2. **Constraints**
   - Primary keys: UUID (not auto-increment)
   - Foreign keys: WITH CASCADE or SET NULL
   - Check constraints for enums

3. **Indexing**
   - Index all foreign keys
   - Index frequently queried columns
   - Composite indexes for complex queries

### 3.3 Testing Standards

#### 3.3.1 Unit Testing
- **Framework:** pytest (Python), Jest (TypeScript)
- **Coverage:** Minimum 90%
- **Test Structure:**
  ```python
  def test_extract_requirements_valid_input():
      """
      Test: AI service extracts requirements from valid user input
      Requirement: REQ-045
      """
      # Arrange
      user_input = "I need user authentication"
      context = {"project_id": "test-123"}
      
      # Act
      result = ai_service.extract_requirements(user_input, context)
      
      # Assert
      assert len(result['requirements']) > 0
      assert result['requirements'][0]['type'] == 'functional'
  ```

#### 3.3.2 Integration Testing
- **Scope:** API endpoints, database interactions
- **Tools:** pytest + httpx, testcontainers
- **Isolation:** Each test uses isolated database

#### 3.3.3 System Testing
- **Scope:** End-to-end workflows
- **Tools:** Playwright (E2E)
- **Scenarios:** Based on use cases in SRS

---

## 4. SOFTWARE DEVELOPMENT ENVIRONMENT

### 4.1 Hardware Environment
- **Development Machines:** Windows 11, 16GB RAM minimum
- **Server (if deployed):** Linux Ubuntu 24, 32GB RAM, 8 CPU cores

### 4.2 Software Tools

| Tool | Version | Purpose | Qualification Status |
|------|---------|---------|---------------------|
| Python | 3.12+ | Backend development | Compiler - Not required |
| Node.js | 20+ LTS | Frontend tooling | Build tool - Not required |
| PostgreSQL | 14+ | Database | COTS - Not required |
| VS Code | Latest | IDE | Not required |
| Git | 2.40+ | Version control | CM tool - Required |
| pytest | 8.0+ | Unit testing | Verification tool - Required |
| mypy | 1.8+ | Static type checking | Verification tool - Required |
| LM Studio | 0.3+ | Local AI inference | **REQUIRES QUALIFICATION** |
| Claude Code | Latest | AI code generation | **REQUIRES QUALIFICATION** |
| FastAPI | 0.104+ | Web framework | Library - Review required |

### 4.3 Tool Qualification Requirements

#### 4.3.1 Tools Requiring Qualification
**Claude Code (Anthropic)**
- **Classification:** Tool that generates code (TQL-5 per DO-330)
- **Qualification Need:** HIGH
- **Justification:** Generates source code that becomes part of deliverable
- **Qualification Approach:**
  1. Define Tool Operational Requirements (TOR)
  2. Create Tool Qualification Plan
  3. Execute tool verification tests
  4. Document Tool Qualification Data

**LM Studio + Mistral Model**
- **Classification:** Tool for verification automation
- **Qualification Need:** MEDIUM
- **Justification:** Used for requirements parsing (critical process)
- **Qualification Approach:**
  1. Regression test suite
  2. Output validation procedures
  3. Version control of model

#### 4.3.2 Tool Usage Guidelines
1. **Code Generated by AI (Claude Code)**
   - MUST be reviewed by qualified engineer
   - MUST be traced to requirements
   - MUST pass all verification tests
   - Changes MUST be documented

2. **AI-Assisted Parsing (LM Studio)**
   - Output MUST be validated by human
   - Fallback manual process MUST exist
   - Confidence scores MUST be logged

---

## 5. SOFTWARE LIFECYCLE DATA

### 5.1 Documents to be Produced

| Document | Abbreviation | Responsibility | Review Required |
|----------|--------------|----------------|-----------------|
| Software Requirements Specification | SRS | Requirements Engineer | Yes |
| Software Design Description | SDD | Design Engineer | Yes |
| Source Code | CODE | Developer | Code Review |
| Software Verification Plan | SVP | Verification Engineer | Yes |
| Software Verification Results | SVR | Verification Engineer | Yes |
| Software Configuration Index | SCI | CM Engineer | No |
| Software Quality Assurance Records | SQAR | QA Engineer | No |
| Software Accomplishment Summary | SAS | Project Manager | Yes |

### 5.2 Traceability Requirements
- Requirements → Design: 100%
- Design → Code: 100%
- Requirements → Test: 100%
- Test Results → Requirements: 100%

### 5.3 Data Retention
- All lifecycle data MUST be retained for 10 years
- Baseline versions MUST be immutable
- Change history MUST be traceable

---

## 6. ADDITIONAL CONSIDERATIONS

### 6.1 Security
- All API endpoints authenticated
- Database credentials encrypted
- Secrets management (not in code)
- Input validation on all user data

### 6.2 Performance
- API response time: < 2 seconds
- Database queries: < 100ms
- AI response time: < 10 seconds

### 6.3 Scalability
- Support 100+ concurrent users
- Handle 10,000+ requirements per project

---

## 7. PLAN COMPLIANCE

### 7.1 Reviews and Audits
- **Code Reviews:** Mandatory for all code changes
- **Design Reviews:** At end of design phase
- **SQA Audits:** Quarterly
- **Management Reviews:** Monthly

### 7.2 Metrics
- Code coverage (target: >90%)
- Defect density (target: <0.5 defects/KLOC)
- Requirements traceability (target: 100%)

### 7.3 Training
- All developers trained on:
  - DO-178C overview
  - Coding standards
  - Tool usage (Claude Code, LM Studio)
  - Configuration management

---

## 8. REFERENCES

1. DO-178C: Software Considerations in Airborne Systems and Equipment Certification
2. DO-330: Software Tool Qualification Considerations
3. PEP 8: Python Style Guide
4. Airbnb JavaScript Style Guide
5. PostgreSQL Documentation

---

## 9. APPROVALS

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Author | [Joy Bousquet] | | |
| Reviewer | [Reviewer] | | |
| Approver | [Manager] | | |

---

**Document Control**
- **Location:** /01_PLANNING/SDP.docx
- **Revision History:**
  - v1.0 (2025-11-14): Initial draft

**DO-178C Objectives Addressed:**
- A-2.1: Software Development Plan (Table A-1, Objective 1)
- A-2.2: Software Development Standards (Table A-1, Objective 2)
- A-2.3: Software Development Environment (Table A-1, Objective 3)
