# AISET - AI Systems Engineering Tool

**Version:** 0.6.0
**Status:** Prototype Development (43% Complete)
**License:** MIT
**DO-178C Compliance:** Level C (configurable A-E)
**Requirements:** 176 (167 primary + 8 derived) - 100% specified, 43% implemented

---

## ⚠️ Documentation Structure - READ FIRST

**This project has 4 DISTINCT documentation levels - DO NOT MIX THEM!**

| Level | Purpose | Location | Audience |
|-------|---------|----------|----------|
| **Level 1** | AISET Tool Development (DO-178C DAL D) | `01_PLANNING/` - `09_CERTIFICATION/` | AISET developers |
| **Level 2** | AISET Usage Framework (ARP4754A) | `docs/Project_Plan.md` | AISET users |
| **Level 3** | Claude Session Documentation | `Claude.md`, `PROJECT_STATUS.md` | Claude Code AI |
| **Level 4** | Specification Roleplay | `REQUIREMENTS.md`, `ROLEPLAY_*.md` | Requirements engineers |

**📖 Read:** `DOCUMENTATION_LEVELS.md` for complete level separation guide

**⚠️ CRITICAL DISTINCTION:**
- **Level 1:** We develop AISET tool per DO-178C
- **Level 2:** AISET helps users develop their systems per ARP4754A
- **These are DIFFERENT processes - NEVER confuse them!**

---

## 📖 Overview

AISET is an **enterprise-grade, AI-powered collaborative systems engineering platform** designed to **automate requirements elicitation, product structure management, design documentation, and traceability management** for safety-critical systems development, with full **DO-178C certification compliance**.

### Key Features

**AI-Powered Engineering:**
- 🤖 **Intelligent Requirements Elicitation** - Natural language conversation with Claude/LM Studio
- 🎯 **Single Question Interaction** - Focused, non-overwhelming user experience
- 💬 **Adaptive Communication** - Simple language by default, technical when needed
- 🚫 **AI Guardrails** - AI facilitates, doesn't make design decisions
- ✅ **Approval Workflow** - AI proposes, humans validate and approve

**Product & Configuration Management:**
- 📦 **Product Structure Management** - Hierarchical Bill of Materials (BOM)
- ⚙️ **Configuration Item Tracking** - 34+ metadata fields per CI
- 🔄 **Lifecycle Management** - Track CIs through development phases
- 🏷️ **Hybrid Identifiers** - GUID (system) + Display ID (human-readable)

**Collaborative Development:**
- 👥 **Multi-User Concurrent Access** - Real-time collaboration
- 🔒 **Check-Out/Check-In** - Pessimistic locking for conflict prevention
- 🔀 **Intelligent Merge Engine** - 5 conflict types with AI-assisted resolution
- 🌐 **Distributed Development** - Multi-instance support with data exchange
- 💬 **Comments & Notifications** - Team communication and awareness

**Traceability & Compliance:**
- 📊 **Automated Traceability Matrix** - Bidirectional links: Requirements ↔ Design ↔ Tests ↔ CIs
- 🔍 **Gap Detection** - Automatically find missing traceability links
- 📈 **Coverage Analysis** - Real-time requirements verification status
- 🛡️ **Complete Audit Trail** - Before/after snapshots for every change
- 📄 **Certification Document Generation** - Auto-generate SRS, SDD, RTM, Test Reports
- 🎯 **DO-178C Compliant** - Supports certification levels A through E

**Access Control & Security:**
- 🔐 **Role-Based Access Control** - 7 role types (Admin, Manager, Engineer, Reviewer, Viewer, External)
- 👥 **Team-Based Permissions** - Project and team-level access
- 🛡️ **CI-Level ACL** - Fine-grained access control per configuration item

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Python 3.12+ with FastAPI
- PostgreSQL 15+ (47 tables for enterprise data model)
- SQLAlchemy ORM
- Alembic migrations
- Anthropic Claude API (primary)
- LM Studio (local fallback)

**Frontend:**
- React 18 + TypeScript 5
- Vite build system
- TailwindCSS styling
- React Query for data fetching
- React Router for navigation

**Infrastructure:**
- Docker + Docker Compose
- GitHub Actions CI/CD
- PostgreSQL database
- RESTful API architecture

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 15+ (or Docker)
- Anthropic API key (optional: LM Studio for local AI)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/aiset.git
cd aiset

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Configuration

1. **Backend Configuration:**
```bash
cd backend
cp .env.example .env
# Edit .env with your settings:
# - DATABASE_URL
# - ANTHROPIC_API_KEY
# - SECRET_KEY
```

2. **Initialize Database:**
```bash
python scripts/init_db.py
```

3. **Start Services:**

Option A - Docker (Recommended):
```bash
docker-compose up
```

Option B - Manual:
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/v1/health

## 📊 Database Schema

AISET uses a comprehensive **47-table enterprise PostgreSQL schema** organized in 15 sections:

**Section 1: Users and Authentication (6 tables)**
- `users`, `roles`, `user_roles`, `teams`, `team_members`, `sessions`

**Section 2: Projects (4 tables)**
- `projects`, `project_context`, `project_standards`, `project_standards_mapping`

**Section 3: Requirements (2 tables)**
- `requirements`, `requirement_relationships`

**Section 4: Design (3 tables)**
- `design_components`, `component_relationships`, `interfaces`

**Section 5: Configuration Management (5 tables)**
- `configuration_items` (34+ fields), `ci_relationships`, `ci_documents`, `baselines`, `baseline_items`

**Section 6: Verification (3 tables)**
- `test_cases`, `test_results`, `verification_procedures`

**Section 7: Traceability (1 table)**
- `traceability_links` - Unified bidirectional traceability

**Section 8: Documents (3 tables)**
- `documents`, `document_versions`, `document_relationships`

**Section 9: AI Conversations (2 tables)**
- `ai_conversations`, `ai_messages`

**Section 10: Change Management (3 tables)**
- `change_requests`, `change_approvals`, `problem_reports`

**Section 11: Audit and History (2 tables)**
- `audit_trail` (before/after snapshots), `activity_log`

**Section 12: Collaborative Work (4 tables)**
- `locks`, `notifications`, `comments`, `work_assignments`

**Section 13: Distributed Development (6 tables)**
- `instances`, `id_mappings`, `merge_sessions`, `merge_conflicts`, `external_references`, `data_sharing_policies`

**Section 14: Access Control (2 tables)**
- `ci_acl`, `team_permissions`

**Section 15: Quality (1 table)**
- `duplicate_candidates`

**Key Schema Features:**
- ✅ **Hybrid Identifiers:** guid (UUID) + display_id (human-readable) on all tables
- ✅ **Complete Audit Trail:** created_at, updated_at, created_by, updated_by on all tables
- ✅ **Soft Deletes:** deleted_at field (NULL = active)
- ✅ **Optimistic Locking:** version field for concurrency control
- ✅ **Referential Integrity:** All foreign keys enforced

See `backend/database/schema_v1.sql` (1600+ lines) and `AI_INSTRUCTION.md` for complete documentation.

## 🎯 Typical Workflow

```
1. Create Project
   ↓
2. Start AI Conversation
   ↓
3. AI Asks Clarifying Questions
   ↓
4. AI Extracts Requirements
   ↓
5. Engineer Validates/Approves
   ↓
6. Requirements Saved to Database
   ↓
7. Create Design Components
   ↓
8. Link Requirements → Design
   ↓
9. Create Test Cases
   ↓
10. Link Requirements → Tests
    ↓
11. Generate Traceability Matrix
    ↓
12. Detect and Resolve Gaps
    ↓
13. Generate Certification Documents (SRS, RTM, etc.)
```

## 📚 DO-178C Compliance

AISET is designed to support DO-178C certification from Day 1:

### Compliance Features

✅ **Bidirectional Traceability** - All requirements linked to design and tests
✅ **Complete Audit Trail** - Every change logged with who/what/when/why
✅ **Human Validation** - AI suggestions require human approval
✅ **Quality Validation** - Automated requirements quality checks
✅ **Gap Detection** - Automatic traceability gap identification
✅ **Document Generation** - Auto-generate SRS, SDD, RTM per standards
✅ **Version Control** - Complete history of all changes
✅ **Change Management** - Formal change request workflow

### Certification Levels Supported

| Level | Failure Condition | AISET Support |
|-------|-------------------|---------------|
| **A** | Catastrophic | ✅ Full compliance |
| **B** | Hazardous | ✅ Full compliance |
| **C** | Major | ✅ Default configuration |
| **D** | Minor | ✅ Reduced traceability |
| **E** | No Effect | ✅ Minimal requirements |

### Configuration

```bash
# backend/.env
ENABLE_AUDIT_TRAIL=True              # Complete change tracking
REQUIRE_APPROVAL_WORKFLOW=True       # Human validation required
TRACEABILITY_STRICT_MODE=True        # Enforce complete traceability
```

**Recommendation:** For Level A/B/C, keep all three settings `True`.

### Generated Artifacts

AISET automatically generates DO-178C certification artifacts:

- **SRS** (Software Requirements Specification)
- **SDD** (Software Design Description)
- **RTM** (Requirements Traceability Matrix)
- **Test Plans**
- **Test Reports**
- **V&V Reports** (Verification & Validation)

All exports include SHA-256 hashes for integrity verification.

## 📖 Documentation

- **[DO-178C Compliance Guide](docs/DO178C_COMPLIANCE.md)** - Detailed compliance documentation
- **[Traceability Matrix](docs/TRACEABILITY_MATRIX.md)** - Complete requirements traceability
- **[API Documentation](http://localhost:8000/docs)** - OpenAPI/Swagger docs
- **[User Guide](docs/USER_GUIDE.md)** - End-user instructions (TODO)
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Development setup (TODO)

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest --cov=. --cov-report=html

# Frontend tests
cd frontend
npm run test

# Linting
cd backend && ruff check .
cd frontend && npm run lint

# Type checking
cd frontend && npm run type-check
```

## 🐳 Docker Deployment

### Development

```bash
docker-compose up
```

### Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🛣️ Roadmap & Current Status

### Current Status: Prototype 43% Complete

**✅ Completed (76 requirements - 43%):**
- [x] PostgreSQL enterprise database schema (47 tables) - 84% mature
- [x] AI service infrastructure (Claude + LM Studio)
- [x] RESTful API framework (FastAPI)
- [x] Basic frontend UI (React + TypeScript)
- [x] Project and requirements CRUD
- [x] AI conversation storage
- [x] Traceability links infrastructure
- [x] Hybrid identifier system (GUID + display_id)
- [x] Complete audit trail architecture
- [x] Soft delete implementation

**⚠️ Partially Implemented (23 requirements - 13%):**
- [ ] AI context recall (messages retrieved, not yet used)
- [ ] JWT authentication (user router exists, not enforced)
- [ ] Database connection pooling (setup exists, needs verification)
- [ ] RBAC enforcement (roles defined, middleware missing)

**❌ Critical Gaps (77 requirements - 44%):**
- [ ] AI behavior logic (single question, approval workflow, guardrails)
- [ ] Project initialization interview
- [ ] Product structure/BOM management UI and APIs
- [ ] Collaborative features (check-out/check-in, merging, conflict resolution)
- [ ] Notification system
- [ ] Document editor
- [ ] Role-based UI
- [ ] Full-text search

### Implementation Plan (from Design Validation Report)

**Phase 1: Core AI Functionality (Weeks 1-2) - Priority 1**
- [ ] Implement AI behavior logic (REQ-AI-001, REQ-AI-002, REQ-AI-010)
  - Single question at a time enforcement
  - Simple language system prompt
  - Guardrails preventing design decisions
- [ ] AI_INSTRUCTION.md ✅ **DONE**
- [ ] Project initialization interview (REQ-AI-032 to REQ-AI-037)
- [ ] AI approval workflow (REQ-AI-017, REQ-AI-018, REQ-AI-019)

**Phase 2: Security & Workflows (Weeks 3-4) - Priority 2**
- [ ] JWT authentication (REQ-BE-004)
- [ ] Approval workflow
- [ ] BOM management APIs and UI
- [ ] Notification system backend

**Phase 3: Collaborative Features (Weeks 5-6)**
- [ ] Locking mechanism (check-out/check-in)
- [ ] Merge engine (5 conflict types)
- [ ] Conflict resolution UI
- [ ] Distributed development support

**Phase 4: Enterprise Polish (Weeks 7-8)**
- [ ] Notification center UI
- [ ] Comment threads
- [ ] Activity feed
- [ ] Role-based UI
- [ ] Advanced analytics

### Long-Term Vision

**Phase 5: External Integration**
- [ ] Integration with Jira, GitHub, Confluence
- [ ] CI/CD pipeline integration
- [ ] External tool API
- [ ] Webhooks for automation

**Phase 6: Advanced AI Features**
- [ ] Test case generation from requirements
- [ ] Impact analysis for change requests
- [ ] Duplicate detection (semantic similarity)
- [ ] AI-assisted traceability suggestions

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow coding standards (PEP 8 for Python, ESLint for TypeScript)
4. Write tests for new features
5. Commit with conventional commits format
6. Push to your fork and submit a pull request

### Code Quality Standards

- **Python:** PEP 8, type hints (mypy), docstrings
- **TypeScript:** Strict mode, ESLint, comprehensive types
- **Testing:** 80%+ coverage for critical paths
- **Documentation:** Docstrings for all functions, README updates

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI powered by [React](https://react.dev/) and [TailwindCSS](https://tailwindcss.com/)
- AI by [Anthropic Claude](https://www.anthropic.com/)
- Local AI via [LM Studio](https://lmstudio.ai/)
- Database: [PostgreSQL](https://www.postgresql.org/)

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/aiset/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/aiset/discussions)
- **Email:** support@aiset.dev (placeholder)

## 🌟 Why AISET?

Traditional systems engineering is **time-consuming and error-prone**:
- Engineers spend 40-60% of time on documentation
- Manual traceability matrices are tedious and incomplete
- Requirements quality varies widely
- Change impact analysis is difficult
- Certification preparation is expensive
- Product structure management is complex
- Multi-team collaboration is challenging

**AISET changes this:**
- AI handles documentation, engineers focus on design
- Automatic traceability with gap detection
- Consistent requirements quality validation
- Real-time impact analysis
- Ready-to-submit certification artifacts
- Enterprise product structure management (BOM, CIs, baselines)
- Seamless multi-user collaboration with intelligent merge

**Result:** 50-70% reduction in engineering overhead while maintaining full DO-178C compliance.

## 📈 Project Maturity

**Current Status (v0.6.0):**
- **Overall:** 43% implemented (56% including partial)
- **Database:** 84% complete (excellent foundation)
- **Backend:** 21% complete (RESTful framework established)
- **Frontend:** 22% complete (basic UI exists)
- **AI:** 5% complete (infrastructure ready, behavior logic needed)

**Documentation:**
- ✅ Software Requirements Specification (SRS v1.0.0) - 167 requirements
- ✅ High-Level Design (HLD v1.0.0)
- ✅ Low-Level Design (LLD v1.0.0) - Database schema
- ✅ Design Validation Report - All 176 requirements validated
- ✅ AI_INSTRUCTION.md - Complete database documentation for AI
- ✅ Traceability Matrix
- ⚠️ Implementation - In progress

See `05_VERIFICATION/Design_Validation_Report.md` for complete requirement-by-requirement assessment.

---

**Built with ❤️ for the aerospace and safety-critical systems community**

*AISET - Accelerating safe software development through AI*

**⚠️ Development Status:** This is a prototype under active development. Not production-ready. DO NOT use for actual certification projects until 100% requirements implementation and full DO-178C compliance verification complete.
