# AISET Project Structure

Complete file structure of the AISET project with **4 DOCUMENTATION LEVELS** clearly separated.

**⚠️ CRITICAL:** See `DOCUMENTATION_LEVELS.md` for complete level separation guide.

---

## 🎯 Four Documentation Levels

### **Level 1:** AISET Tool Development (DO-178C DAL D)
### **Level 2:** AISET Usage Framework (ARP4754A - what AISET helps users create)
### **Level 3:** Claude Session Documentation (internal development)
### **Level 4:** Specification Roleplay (requirements capture)

---

## 📁 Project Root

```
aiset/
├── README.md                          # Main project documentation
├── LICENSE                            # MIT License
├── CONTRIBUTING.md                    # Contribution guidelines
│
├── 📄 **[Meta]** Documentation Organization
├── DOCUMENTATION_LEVELS.md           # ⭐ MASTER: 4-level separation guide
├── DOCUMENTATION_STRUCTURE.md        # ⭐ Documentation organization (v2.0)
├── PROJECT_STRUCTURE.md              # This file - codebase structure
│
├── 📄 **[Level 3]** Claude Session Documentation (Internal Development)
├── Claude.md                          # ⭐ Claude Code resume file
├── PROJECT_STATUS.md                  # ⭐ Human-readable project status
│
├── 📄 **[Level 4]** Specification Roleplay (Requirements Capture)
├── ROLEPLAY_REQUIREMENTS.md           # ⭐ Working requirements file (v0.8.0, 167 requirements)
│                                      # → Source for Level 1 SRS (02_REQUIREMENTS/SRS)
├── ROLEPLAY_RULES.md                 # ⭐ Specification roleplay methodology
├── ROLEPLAY_SESSION.md               # Roleplay session status (COMPLETED)
│
├── 📄 **[Level 1]** DO-178C Index
├── 00_DO178C_INDEX.md                # Master index for AISET DO-178C compliance
│
├── 📄 **[Level 1]** AISET Development Infrastructure
├── .gitignore                        # Git ignore rules
├── docker-compose.yml                # Docker orchestration (AISET deployment)
│
├── 📂 **[Level 1]** backend/         # AISET Tool Source Code (Python FastAPI)
│   ├── main.py                       # FastAPI application entry point
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Backend container image
│   ├── .env.example                  # Environment variables template
│   ├── pytest.ini                    # Pytest configuration
│   │
│   ├── 📂 config/                    # Configuration management
│   │   └── settings.py               # Pydantic settings (REQ-CONFIG-002)
│   │
│   ├── 📂 database/                  # Database layer
│   │   └── connection.py             # SQLAlchemy setup (REQ-DB-001)
│   │
│   ├── 📂 models/                    # SQLAlchemy ORM Models (18 tables)
│   │   ├── __init__.py               # Models export (REQ-DB-MODEL-001)
│   │   ├── project.py                # Projects (REQ-DB-MODEL-002)
│   │   ├── requirement.py            # Requirements (REQ-DB-MODEL-003)
│   │   ├── design_component.py       # Design components (REQ-DB-MODEL-004)
│   │   ├── test_case.py              # Test cases (REQ-DB-MODEL-005)
│   │   ├── ai_conversation.py        # AI conversations & messages (REQ-DB-MODEL-006)
│   │   ├── ai_extracted_entity.py    # AI extractions (REQ-DB-MODEL-007)
│   │   ├── user.py                   # Users & auth (REQ-DB-MODEL-008)
│   │   ├── traceability.py           # Traceability links & gaps (REQ-DB-MODEL-009)
│   │   ├── audit.py                  # Version history & change requests (REQ-DB-MODEL-010)
│   │   ├── document_export.py        # Document exports (REQ-DB-MODEL-011)
│   │   └── configuration_item.py     # Configuration Items & BOM (REQ-AI-038-040)
│   │
│   ├── 📂 process_engine/            # State Machine Framework (REQ-SM, REQ-IS, REQ-DC, REQ-AG)
│   │   ├── __init__.py               # Package exports (updated with all services)
│   │   ├── README.md                 # Process engine documentation
│   │   ├── 📂 schemas/
│   │   │   ├── process_template_schema.json  # JSON Schema for templates
│   │   │   └── process_engine_ddl.sql        # Database schema (10 tables)
│   │   ├── 📂 services/
│   │   │   ├── state_machine_generator.py    # Core state machine logic (~550 lines)
│   │   │   ├── data_capture.py               # **NEW** Validation & storage (~350 lines)
│   │   │   ├── interview_executor.py         # **NEW** Script execution (~400 lines)
│   │   │   └── artifact_generator.py         # **NEW** Document generation (~400 lines)
│   │   ├── 📂 templates/             # Process definition templates
│   │   │   ├── arp4754a_system_process.json  # ARP4754A (10 phases)
│   │   │   ├── do178c_software_process.json  # DO-178C (9 phases)
│   │   │   ├── do254_hardware_process.json   # DO-254 (8 phases)
│   │   │   ├── product_development_process.json  # Physical products (7 phases)
│   │   │   └── component_part_process.json   # Components/Parts (5 phases)
│   │   ├── 📂 interview_scripts/     # **NEW** Interview script definitions
│   │   │   └── 📂 project_initialization/
│   │   │       ├── script.json               # Main script (6 sub-phases)
│   │   │       └── 📂 questions/             # 17 question JSON files
│   │   │           └── PI-001.json through PI-016.json
│   │   └── 📂 document_templates/    # **NEW** Jinja2 document templates
│   │       ├── SRS_template.md               # Software Requirements Spec
│   │       ├── RTM_template.md               # Requirements Traceability Matrix
│   │       └── Gap_Analysis_template.md      # Gap Analysis Report
│   │
│   ├── 📂 services/                  # Business logic layer
│   │   ├── ai_service.py             # Claude/LM Studio integration (REQ-SERVICE-001)
│   │   ├── ai_context_loader.py      # AI context management (REQ-AI-045-047)
│   │   ├── approval_service.py       # AI approval workflow (REQ-AI-017-019)
│   │   ├── auth_service.py           # JWT authentication (REQ-BE-003, REQ-BE-004)
│   │   ├── auth_dependencies.py      # FastAPI auth dependencies (REQ-BE-003)
│   │   ├── requirements_service.py   # Requirements management (REQ-SERVICE-002)
│   │   ├── traceability_service.py   # Traceability management (REQ-SERVICE-003)
│   │   ├── document_service.py       # Document generation (REQ-SERVICE-004)
│   │   └── configuration_item_service.py  # Product Structure/BOM (REQ-AI-038-040)
│   │
│   ├── 📂 routers/                   # API endpoints
│   │   ├── __init__.py               # Routers export (REQ-API-001)
│   │   ├── health.py                 # Health check (REQ-API-002)
│   │   ├── auth.py                   # Authentication API (REQ-BE-003, REQ-BE-004)
│   │   ├── projects.py               # Projects API (REQ-API-003)
│   │   ├── requirements.py           # Requirements API (REQ-API-004)
│   │   ├── ai_conversation.py        # AI chat API (REQ-API-005)
│   │   ├── approval.py               # Approval workflow API (REQ-AI-017-019)
│   │   ├── traceability.py           # Traceability API (REQ-API-006)
│   │   ├── documents.py              # Document generation API (REQ-API-007)
│   │   ├── design_components.py      # Design API (REQ-API-008)
│   │   ├── test_cases.py             # Test cases API (REQ-API-009)
│   │   ├── users.py                  # Users API (REQ-API-010)
│   │   ├── configuration_items.py    # Product Structure/BOM API (REQ-AI-038-040)
│   │   └── process_engine.py         # **NEW** Process Engine API (REQ-SM, REQ-IS)
│   │
│   └── 📂 tests/                     # Test suites
│       ├── __init__.py               # Tests initialization
│       ├── test_requirements_service.py  # Requirements tests (REQ-TEST-001)
│       ├── test_traceability_service.py  # Traceability tests (REQ-TEST-002)
│       ├── test_ai_behavior.py           # AI behavior tests (REQ-AI-001-010)
│       ├── test_project_initialization.py # Project init tests (REQ-AI-032-037)
│       ├── test_approval_workflow.py     # Approval workflow tests (REQ-AI-017-019)
│       └── test_auth_service.py          # Auth service tests (REQ-BE-003, REQ-BE-004)
│
├── 📂 **[Level 1]** frontend/        # AISET Tool Source Code (React TypeScript)
│   ├── package.json                  # NPM dependencies
│   ├── tsconfig.json                 # TypeScript configuration
│   ├── tsconfig.node.json            # TypeScript node config
│   ├── vite.config.ts                # Vite build config (REQ-FRONTEND-001)
│   ├── tailwind.config.js            # TailwindCSS config
│   ├── postcss.config.js             # PostCSS config
│   ├── Dockerfile                    # Frontend container image
│   ├── index.html                    # HTML entry point
│   │
│   └── 📂 src/                       # Source code
│       ├── main.tsx                  # React entry point (REQ-FRONTEND-002)
│       ├── App.tsx                   # Main app component (REQ-FRONTEND-003)
│       ├── index.css                 # Global styles (REQ-FRONTEND-004)
│       │
│       ├── 📂 types/                 # TypeScript types
│       │   └── index.ts              # Type definitions (REQ-FRONTEND-005)
│       │
│       ├── 📂 services/              # API clients
│       │   └── api.ts                # Backend API client (REQ-FRONTEND-006)
│       │
│       ├── 📂 components/            # React components
│       │   └── Layout.tsx            # Main layout (REQ-FRONTEND-007)
│       │
│       ├── 📂 contexts/              # React contexts
│       │   └── AuthContext.tsx       # Auth state management (REQ-BE-003, REQ-BE-004)
│       │
│       └── 📂 pages/                 # Page components
│           ├── Dashboard.tsx         # Dashboard page (REQ-FRONTEND-008)
│           ├── Projects.tsx          # Projects list (REQ-FRONTEND-009)
│           ├── ProjectDetails.tsx    # Project details (REQ-FRONTEND-010)
│           ├── ProjectInitializationWizard.tsx  # Project init wizard (REQ-AI-032-037)
│           ├── Requirements.tsx      # Requirements page (REQ-FRONTEND-011)
│           ├── Chat.tsx              # AI chat page (REQ-FRONTEND-012)
│           ├── Traceability.tsx      # Traceability matrix (REQ-FRONTEND-013)
│           ├── Documents.tsx         # Document generation (REQ-FRONTEND-014)
│           ├── ProductStructure.tsx  # Product Structure/BOM tree (REQ-AI-038-040)
│           ├── Login.tsx             # Login page (REQ-BE-003)
│           └── Register.tsx          # Registration page (REQ-BE-003)
│
├── 📂 docs/                          # Reference Documentation (PHYSICALLY SEPARATED BY LEVEL)
│   ├── README.md                     # ⭐ Explains level separation
│   │
│   ├── 📂 Level_1_AISET_Development/ # **[Level 1]** AISET Tool Development (DO-178C DAL D)
│   │   ├── DATABASE_SCHEMA.md        # ⭐ AISET database schema (47 tables)
│   │   ├── SQL_requirement.md        # AISET database requirements spec
│   │   ├── GAP_ANALYSIS.md           # AISET DO-178C compliance gaps
│   │   └── DO178C_COMPLIANCE.md      # AISET DO-178C compliance status
│   │
│   └── 📂 Level_2_User_Framework/    # **[Level 2]** AISET Usage Framework (ARP4754A)
│       ├── Project_Plan.md           # ⭐ 10-phase ARP4754A process (475 lines)
│       │                             # ⚠️ This is for USERS, NOT AISET development
│       └── TRACEABILITY_MATRIX.md    # Template of what AISET generates
│
├── 📂 **[Level 1]** scripts/         # AISET Development Utility Scripts
│   ├── setup.sh                      # Initial setup script (REQ-SETUP-001)
│   └── init_db.py                    # Database initialization (REQ-SETUP-002)
│
└── 📂 **[Level 1]** .github/         # AISET Development CI/CD
    └── workflows/
        └── ci.yml                    # CI/CD pipeline (REQ-CI-001)
```

## 📊 File Count Summary **[Level 1]**
*AISET Tool Development Components*

### Backend (Python)
- **Configuration:** 3 files (settings, database, main)
- **Models:** 11 files (16 database tables)
- **Services:** 4 files (AI, requirements, traceability, documents)
- **Routers:** 10 files (9 API route groups + init)
- **Tests:** 3 files (requirements, traceability, init)
- **Total Backend:** ~31 files

### Frontend (TypeScript/React)
- **Configuration:** 8 files (package.json, tsconfig, vite, etc.)
- **Types:** 1 file (all interfaces and enums)
- **Services:** 1 file (API client)
- **Components:** 1 file (Layout)
- **Pages:** 7 files (all main pages)
- **Total Frontend:** ~18 files

### Documentation & Infrastructure
- **Documentation:** 5 files (README, DO-178C, traceability, contributing, project structure)
- **Scripts:** 2 files (setup, init_db)
- **Docker:** 3 files (docker-compose, 2 Dockerfiles)
- **CI/CD:** 1 file (GitHub Actions)
- **Configuration:** 3 files (.gitignore, LICENSE, Claude.md)
- **Total Infrastructure:** ~14 files

### Grand Total
**~63 files** covering:
- ✅ Complete backend with 16-table database
- ✅ Full frontend with 7 pages
- ✅ DO-178C compliance documentation
- ✅ Docker deployment
- ✅ CI/CD pipeline
- ✅ Test suites
- ✅ Setup scripts

## 🎯 DO-178C Traceability Coverage **[Level 1]**
*AISET Tool Development Requirements Coverage*

### Requirements Implemented

**Backend Requirements:** 27
- Database: REQ-DB-001 to REQ-DB-MODEL-011
- Services: REQ-SERVICE-001 to REQ-SERVICE-004
- API: REQ-API-001 to REQ-API-010

**Frontend Requirements:** 14
- REQ-FRONTEND-001 to REQ-FRONTEND-014

**Compliance Requirements:** 14
- Traceability: REQ-TRACE-001 to REQ-TRACE-019
- Audit: REQ-AUDIT-001 to REQ-AUDIT-010
- Validation: REQ-VALID-001 to REQ-VALID-006
- Document: REQ-DOC-001 to REQ-DOC-006
- Certification: REQ-CERT-001 to REQ-CERT-009

**Total Requirements:** 55+

**Implementation Coverage:** 100%

## 🚀 Key Features Implemented **[Level 1]**
*AISET Tool Capabilities*

### 1. Database (16 Tables)
✅ Projects, Requirements, Design, Tests
✅ AI Conversations & Messages
✅ Traceability Links (3 types)
✅ Version History & Audit Trail
✅ Users & Authentication
✅ Document Exports

### 2. Backend Services
✅ AI Service (Claude + LM Studio)
✅ Requirements Management
✅ Traceability Management
✅ Document Generation (SRS, RTM)

### 3. API Endpoints
✅ Projects CRUD
✅ Requirements CRUD with validation
✅ AI Chat & Extraction
✅ Traceability Matrix
✅ Document Generation
✅ Health Checks

### 4. Frontend Pages
✅ Dashboard with statistics
✅ Projects management
✅ Requirements list
✅ AI Chat interface
✅ Traceability matrix
✅ Document generation

### 5. DO-178C Compliance
✅ Complete audit trail
✅ Human-in-the-loop validation
✅ Gap detection
✅ Requirements quality validation
✅ Bidirectional traceability
✅ Certification artifacts

### 6. DevOps
✅ Docker Compose setup
✅ CI/CD pipeline
✅ Automated tests
✅ Code quality checks
✅ Setup scripts

## 📝 Next Steps **[Level 1]**
*AISET Tool Setup & Deployment*

1. **Run Setup:**
   ```bash
   ./scripts/setup.sh
   ```

2. **Configure Environment:**
   - Edit `backend/.env` with API keys
   - Set database credentials

3. **Initialize Database:**
   ```bash
   python scripts/init_db.py
   ```

4. **Start Application:**
   ```bash
   docker-compose up
   ```

5. **Access:**
   - Frontend: http://localhost:5173
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

**Status:** ✅ Prototype 70% Complete
**Version:** 0.2.5
**Last Updated:** 2025-11-23 (Requirements 182, DO-178C 60%)

**⚠️ IMPORTANT:** All folders and sections now tagged with documentation levels.
**See:** `DOCUMENTATION_LEVELS.md` for level definitions and anti-mixing guidelines.
