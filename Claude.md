# AISET - AI Systems Engineering Tool

---

## 🚨 PROJECT STATUS (Last Updated: 2025-11-14 22:00 UTC)

### ⚠️ CURRENT STATE: FUNCTIONAL BUT NOT DO-178C COMPLIANT

**Repository:** https://github.com/joiedelor/AISET
**Status:** MVP Complete ✅ | DO-178C Compliance: 25% ⚠️
**Version:** 0.1.0

**⚠️ CRITICAL:** System is FUNCTIONAL but NOT production-ready. DO-178C remediation in progress.

### 🎯 SESSION SUMMARY (2025-11-14 19:00-23:00 UTC)

**COMPLETED ✅**
1. ✅ PostgreSQL 15 installed (manual, no Docker)
2. ✅ Python 3.12.3 virtual environment created
3. ✅ Backend dependencies installed (385 packages)
4. ✅ Frontend dependencies installed (Node.js 18)
5. ✅ Database configured and connected
6. ✅ Backend API running on port 8000
7. ✅ Frontend dev server running on port 5173
8. ✅ Fixed Pydantic v2 compatibility issues
9. ✅ Fixed SQLAlchemy model loading
10. ✅ LM Studio configured (Windows host)
11. ✅ DO-178C compliance review performed
12. ✅ DO-178C directory structure created
13. ✅ Retroactive documentation started
14. ✅ DO-178C guide documents created in docs/
15. ✅ Software Development Plan (SDP) completed
16. ✅ Tool Qualification Plan (DO-330) completed
17. ✅ Daily Workflow Guide completed
18. ✅ Database schema expanded: 16 → 42 tables
19. ✅ Full ARP4754/DO-178C/DO-254 compliance schema
20. ✅ Database schema documentation created

**DO-178C COMPLIANCE STATUS ⚠️**
- **Overall Compliance:** 25%
- **Planning:** 40% (SDP ✅, Tool Qualification Plan ✅, Daily Workflow Guide ✅, PSAC/SVP/SCMP/SQAP pending)
- **Requirements:** 0% (no SRS yet)
- **Design:** 0% (no HLD/LLD yet)
- **Code Quality:** 40% (exists but not reviewed/tested)
- **Verification:** 0% (no tests yet)
- **Traceability:** 0% (not established yet)

**ACTIVE NON-CONFORMANCE REPORTS (NCRs)**
1. NCR-2025-11-14-001: No Requirements (CRITICAL)
2. NCR-2025-11-14-002: No Design Documentation (CRITICAL)
3. NCR-2025-11-14-003: No Code Reviews (HIGH)
4. NCR-2025-11-14-004: No Unit Tests (HIGH)
5. NCR-2025-11-14-005: Tool Not Qualified (MEDIUM)

### 📋 CRITICAL INFORMATION FOR RESUMING

#### Location
- **Local Path:** `/home/joiedelor/aiset/`
- **Platform:** WSL2 Ubuntu on Windows
- **Access from Windows:** `\\wsl$\Ubuntu\home\joiedelor\aiset`

#### System Status (2025-11-14 23:00)
- ✅ **Backend API:** Running on http://localhost:8000
- ✅ **Frontend Dev:** Running on http://localhost:5173
- ✅ **PostgreSQL:** localhost:5432 (database: aiset_db, 42 tables)
- ✅ **LM Studio:** Configured (Windows host: 172.27.80.1:1234)
- ⚠️ **DO-178C Compliance:** 25% - NOT production-ready

#### Essential Files (68 source + DO-178C docs)
- **Backend:** 31 files (Python/FastAPI)
- **Frontend:** 18 files (React/TypeScript)
- **Database:** 42 tables (16 → 42, full compliance schema)
- **Migrations:** 002_add_compliance_schema_v2.sql
- **DO-178C Folders:** 9 folders (01_PLANNING through 09_CERTIFICATION)
- **DO-178C Guides (docs/):**
  - `DO178C_Daily_Workflow_Guide.md` - Guide pratique quotidien DO-178C
  - `DO178C_Project_Structure.md` - Structure de projet DO-178C
  - `SDP_Software_Development_Plan.md` - Plan de développement logiciel
  - `Tool_Qualification_Plan_DO330.md` - Plan de qualification des outils
  - `SQL_requirement.md` - Database requirements specification
  - `DATABASE_SCHEMA.md` - Complete database schema documentation
- **Project Docs:** PROJECT_STATUS.md, 00_DO178C_INDEX.md, SESSION_RESUME.md
- **AI Tool Usage:** TU-2025-11-14-001

#### Configuration Files (COMPLETED ✅)

1. **Backend Environment** (`backend/.env`)
   ```bash
   DATABASE_URL=postgresql://aiset_user:***@localhost:5432/aiset_db
   SECRET_KEY=*** (64-char hex)
   AI_SERVICE=lmstudio
   LM_STUDIO_URL=http://172.27.80.1:1234/v1
   ```

2. **Database** (PostgreSQL 15)
   ```bash
   # Already configured:
   - Database: aiset_db
   - User: aiset_user
   - Owner: aiset_user (full permissions)
   - Tables: 16 created successfully
   ```

#### Quick Start Commands (For Next Session)

```bash
# Navigate to project
cd /home/joiedelor/aiset

# Start PostgreSQL (if not running)
sudo service postgresql start

# Terminal 1 - Backend
cd backend && source venv/bin/activate && python -m uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend && npm run dev

# Access:
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Note:** Docker was NOT used (too complex for initial setup).

#### What's NOT in Git (Configure Locally)
- ❌ `backend/.env` (has secrets - CONFIGURED ✅)
- ❌ `backend/venv/` (virtual environment - CREATED ✅)
- ❌ `frontend/node_modules/` (npm packages - INSTALLED ✅)
- ❌ Database data (PostgreSQL local)
- ❌ API tokens

#### Next Immediate Tasks (DO-178C Remediation)
1. ✅ ~~Complete environment setup~~ (DONE 2025-11-14)
2. ✅ ~~DO-178C compliance review~~ (DONE 2025-11-14)
3. ✅ ~~Create DO-178C structure~~ (DONE 2025-11-14)
4. ✅ ~~Document today's session~~ (DONE 2025-11-14)
5. **URGENT:** Perform code reviews on all modified files
6. **URGENT:** Create retroactive requirements (REQ-SETUP-001 to 004)
7. **URGENT:** Write unit tests for configuration/database code
8. **SHORT-TERM:** Complete 4 missing plans (PSAC, SVP, SCMP, SQAP)
9. **SHORT-TERM:** Create SRS, HLD, LLD
10. **MEDIUM-TERM:** Achieve 90% test coverage

#### Critical DO-178C Documentation (⭐ READ FIRST)
- **00_DO178C_INDEX.md** - Master project index
- **PROJECT_STATUS.md** - Complete status and resume guide
- **SESSION_RESUME.md** - Session resume information
- **docs/DO178C_Daily_Workflow_Guide.md** - MANDATORY daily workflow (CRITICAL)
- **docs/DO178C_Project_Structure.md** - Complete DO-178C structure guide
- **docs/SDP_Software_Development_Plan.md** - Software Development Plan
- **docs/Tool_Qualification_Plan_DO330.md** - Tool qualification for Claude Code & LM Studio
- **01_PLANNING/** - Planning documents (in progress)
- **04_SOURCE_CODE/AI_Tool_Usage/TU-2025-11-14-001_Session_Setup.md** - Session record

---

## 🎯 Project Overview

AISET is an **AI-powered systems engineering tool** designed to automate requirements elicitation, design documentation, and traceability management for critical systems development.

### Primary Goal
Reduce engineering overhead by 50-70% while maintaining full compliance with aerospace and safety-critical standards, particularly **DO-178C** (Software Considerations in Airborne Systems and Equipment Certification).

---

## 🛡️ Certification Requirements

### DO-178C Compliance
This tool is being developed to support **DO-178C certification processes**:

- **Traceability**: Complete bidirectional traceability from requirements → design → tests
- **Documentation**: Automated generation of certification artifacts (SRS, SDD, Test Plans)
- **Quality Assurance**: Validation workflows with human-in-the-loop approval
- **Version Control**: Full audit trail of all changes and decisions
- **Standards Compliance**: Structured data conforming to ISO/IEEE standards

### Certification Artifacts Generated
- Software Requirements Specification (SRS)
- Software Design Description (SDD)
- Requirements Traceability Matrix (RTM)
- Test Coverage Reports
- Verification & Validation Documentation

---

## 💡 Core Problem Solved

**Current Challenge**: Engineers spend 40-60% of their time on:
- Manual requirements documentation
- Maintaining traceability matrices
- Generating certification documents
- Managing change impact analysis

**AISET Solution**: AI handles administrative tasks while engineers focus on design.

---

## 🏗️ Architecture

### Technology Stack
- **Backend**: Python FastAPI + PostgreSQL + SQLAlchemy
- **Frontend**: React + TypeScript + Vite
- **AI Engine**: Dual support
  - Claude API (Anthropic) - Primary for production
  - LM Studio + Mistral - Local fallback for offline/dev work
- **Database**: PostgreSQL 14+ with 15+ tables for complete data model

### Key Components

#### 1. AI Conversational Interface
- Natural language requirements elicitation
- Intelligent follow-up questions
- Context-aware parsing and extraction

#### 2. Requirements Management
- Structured requirement storage (ID, type, priority, status)
- Hierarchical decomposition
- Automatic numbering and versioning

#### 3. Validation Workflow
- AI extracts requirements with confidence scores
- Human validation before database insertion
- Approval/rejection with rationale tracking

#### 4. Traceability Engine
- Automatic requirement → design → test linking
- Gap detection and conflict resolution
- Real-time traceability matrix generation

#### 5. Document Generation
- Template-based export (Markdown, PDF)
- Customizable certification artifacts
- Version-controlled documentation

---

## 📊 Database Schema

### Core Tables
- `projects`: Project metadata and configuration
- `requirements`: All system requirements with full attributes
- `design_components`: System architecture and design elements
- `test_cases`: Verification test cases
- `ai_conversations`: Chat history and context
- `ai_extracted_entities`: Pending AI extractions awaiting validation

### Traceability Tables
- `requirements_design_trace`: Requirements ↔ Design mapping
- `requirements_test_trace`: Requirements ↔ Tests mapping
- `design_test_trace`: Design ↔ Tests mapping

### Audit Tables
- `version_history`: Complete change tracking
- `change_requests`: Impact analysis and approval workflow

---

## 🚀 Development Phases

### MVP (Phase 1) - Current Focus ✅
- [x] AI conversational requirements elicitation
- [x] Structured requirement extraction and validation
- [x] Basic traceability (requirements → design)
- [x] PostgreSQL database with complete schema
- [x] React frontend with chat interface
- [x] Export to Markdown/PDF

### Phase 2 - Enhanced Compliance
- [ ] Full DO-178C artifact generation
- [ ] Gap and inconsistency detection
- [ ] Advanced traceability matrix with filtering
- [ ] Test case generation from requirements
- [ ] Impact analysis for change requests
- [ ] Multi-user collaboration

### Phase 3 - Enterprise Features
- [ ] Integration with Jira, GitHub, Confluence
- [ ] Role-based access control (Engineer, Reviewer, Auditor)
- [ ] Advanced analytics and dashboards
- [ ] CI/CD pipeline integration
- [ ] Docker deployment
- [ ] API for external tool integration

---

## 🔄 Typical Workflow

```
1. Engineer starts conversation with AI
   ↓
2. AI asks structured questions
   ↓
3. AI extracts requirements from responses
   ↓
4. Engineer validates extracted requirements
   ↓
5. Approved requirements stored in database
   ↓
6. Engineer describes design approach
   ↓
7. AI creates design components with automatic requirement linking
   ↓
8. System generates traceability matrix
   ↓
9. Export certification documentation
```

---

## 🎨 Design Principles

### 1. Human-in-the-Loop
AI assists but humans approve. All critical decisions require human validation.

### 2. Audit Trail
Every action is logged with timestamp, user, and rationale for certification compliance.

### 3. Flexibility
Support both cloud AI (Claude) and local AI (Mistral) for different environments.

### 4. Standards-Based
Follow ISO/IEEE standards for requirements engineering and DO-178C for aerospace.

### 5. Open Source
MIT License - Community-driven development with transparency.

---

## 🌐 GitHub Repository

### Repository Structure
```
aiset/
├── backend/          # FastAPI application
├── frontend/         # React application
├── docs/             # Documentation and guides
├── scripts/          # Utility scripts
├── tests/            # Test suites
├── .github/          # CI/CD workflows
└── README.md         # Main documentation
```

### Contribution Guidelines
- Feature branches with descriptive names
- Pull requests with detailed descriptions
- Code review required before merge
- Automated tests must pass
- Follow Python PEP 8 and TypeScript ESLint standards

### GitHub Actions
- Automated testing on push
- Code quality checks (linting, type checking)
- Documentation generation
- Docker image building

---

## 📈 Success Metrics

### Development Goals
- ✅ Complete MVP in 4 weeks
- ✅ 100% test coverage for critical paths
- ✅ Documentation coverage for all APIs
- ✅ Zero critical security vulnerabilities

### User Impact Goals
- 50%+ reduction in documentation time
- 100% traceability coverage
- 90%+ user satisfaction
- Successful DO-178C audit support

---

## 🔒 Security & Privacy

- No sensitive data in version control
- Environment variables for all credentials
- PostgreSQL with encrypted connections
- API authentication via JWT tokens
- Role-based access control

---

## 📚 Documentation

### User Guides
- Getting Started Guide
- Requirements Elicitation Tutorial
- Traceability Matrix Guide
- Export and Reporting Guide

### Developer Guides
- API Documentation (OpenAPI/Swagger)
- Database Schema Reference
- AI Service Integration Guide
- Frontend Component Library

### Certification Guides
- DO-178C Compliance Checklist
- Artifact Generation Guide
- Audit Preparation Guide

---

## 🤝 Target Users

1. **Systems Engineers**: Primary users for requirements and design
2. **Certification Authorities**: Reviewers and auditors
3. **Project Managers**: Progress tracking and reporting
4. **QA Engineers**: Test case management and verification

---

## 🛠️ Development Standards

### Code Quality
- Type hints in Python (mypy)
- TypeScript strict mode
- Comprehensive unit tests (pytest, vitest)
- Integration tests for critical workflows
- Code review for all changes

### Documentation
- Docstrings for all functions
- README for each module
- API documentation auto-generated
- User guides with examples

### Version Control
- Conventional Commits format
- Semantic versioning (SemVer)
- Changelog maintained
- Release notes for each version

---

## 🎯 Current Status

**Version**: 0.1.0 (MVP in development)

**Latest Updates**:
- ✅ Complete database schema implemented
- ✅ AI service with Claude/Mistral switch
- ✅ Basic frontend with chat interface
- ✅ Requirements validation workflow
- 🔄 Documentation generation in progress
- 🔄 Enhanced traceability features in progress

---

## 📞 Project Information

- **License**: MIT
- **Language**: Python 3.12+, TypeScript 5+
- **Platform**: Linux (Ubuntu/WSL), macOS, Windows (via WSL)
- **Repository**: https://github.com/[username]/aiset (to be published)

---

## 🔮 Future Vision

AISET aims to become the **de facto open-source tool** for AI-assisted systems engineering in safety-critical industries (aerospace, automotive, medical devices, nuclear).

By combining AI automation with rigorous certification requirements, AISET will enable faster development cycles while maintaining the highest safety and quality standards.

---

**Last Updated**: November 2025  
**Status**: Active Development  
**Maintainers**: Open to contributors
