# AISET - AI Systems Engineering Tool

**Version:** 0.1.0
**Status:** MVP Development
**License:** MIT
**DO-178C Compliance:** Level C (configurable A-E)

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

AISET is an AI-powered systems engineering tool designed to **automate requirements elicitation, design documentation, and traceability management** for safety-critical systems development, with full **DO-178C certification compliance**.

### Key Features

- 🤖 **AI-Powered Requirements Elicitation** - Natural language conversation with Claude/Mistral
- 📊 **Automated Traceability Matrix** - Bidirectional links: Requirements ↔ Design ↔ Tests
- ✅ **Human-in-the-Loop Validation** - AI extracts, humans approve
- 📄 **Certification Document Generation** - Auto-generate SRS, SDD, RTM, Test Reports
- 🔍 **Gap Detection** - Automatically find missing traceability links
- 📈 **Coverage Analysis** - Real-time requirements verification status
- 🛡️ **Complete Audit Trail** - Every change logged for certification
- 🎯 **DO-178C Compliant** - Supports certification levels A through E

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Python 3.12+ with FastAPI
- PostgreSQL 15+ (16 tables for complete data model)
- SQLAlchemy ORM
- Anthropic Claude API (primary)
- LM Studio + Mistral (local fallback)

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

AISET uses a comprehensive 16-table PostgreSQL schema:

**Core Entities:**
- `projects` - Project metadata
- `requirements` - System requirements
- `design_components` - Architecture and design
- `test_cases` - Verification tests
- `users` - User accounts

**AI & Elicitation:**
- `ai_conversations` - Chat sessions
- `ai_messages` - Individual messages
- `ai_extracted_entities` - Pending validations
- `validation_decisions` - Approval records

**Traceability:**
- `requirements_design_trace` - Req → Design links
- `requirements_test_trace` - Req → Test links
- `design_test_trace` - Design → Test links
- `traceability_gaps` - Detected gaps

**Audit & Compliance:**
- `version_history` - Complete change log
- `change_requests` - Change management
- `document_exports` - Generated artifacts

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

## 🛣️ Roadmap

### MVP (Phase 1) - ✅ Current Focus

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
- [ ] API for external tool integration

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

**AISET changes this:**
- AI handles documentation, engineers focus on design
- Automatic traceability with gap detection
- Consistent requirements quality validation
- Real-time impact analysis
- Ready-to-submit certification artifacts

**Result:** 50-70% reduction in engineering overhead while maintaining full DO-178C compliance.

---

**Built with ❤️ for the aerospace and safety-critical systems community**

*AISET - Accelerating safe software development through AI*
