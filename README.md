# 🤖 AISET - AI Systems Engineering Tool

> **Intelligent Requirements Elicitation and System Design Assistant**

An AI-powered tool that automates requirements gathering, system design documentation, and traceability management for engineering projects. Built with local AI (LM Studio + Mistral), FastAPI, React, and PostgreSQL.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technologies](#technologies)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**AISET** helps engineers focus on creative design while AI handles administrative tasks:

- **Problem**: Engineers spend 40-60% of their time on documentation, traceability, and requirement management
- **Solution**: AI-driven conversational interface that structures requirements, maintains traceability, and generates documentation automatically

### 💡 Value Proposition

- ⏱️ **Time Savings**: 50-70% reduction in administrative overhead
- ✅ **Quality**: Complete requirement coverage with automatic traceability
- 📊 **Compliance**: Structured documentation conforming to ISO/IEEE standards
- 🎨 **Focus**: Engineers concentrate on design, not paperwork

---

## ✨ Key Features

### MVP (Phase 1) - Available Now

- ✅ **AI-Assisted Requirements Elicitation**
  - Conversational interface with local AI
  - Automatic extraction and structuring
  - Validation workflow with confidence scoring
  
- ✅ **Structured Design Management**
  - Component hierarchy tracking
  - Automatic requirement-to-design linking
  
- ✅ **Documentation Export**
  - Generate SRS (Software Requirements Specification)
  - Markdown and PDF formats
  - Customizable templates

### Phase 2 (Planned)

- 🔍 **Gap & Inconsistency Detection**
- 📊 **Real-time Traceability Matrix**
- 🧪 **Automated Test Case Generation**

### Phase 3 (Future)

- 👥 **Multi-user Collaboration**
- 🔗 **Integration with Jira, GitHub, Confluence**
- 📈 **Advanced Visualizations & Analytics**

---

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │ (TypeScript + Vite)
│  Chat + Tables  │
└────────┬────────┘
         │ REST API
┌────────┴────────┐
│  FastAPI Backend│ (Python)
│  - Auth         │
│  - Business     │
│  - AI Manager   │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┐
    │          │          │
┌───┴───┐ ┌───┴────┐ ┌───┴────┐
│  DB   │ │ LM     │ │ Cache  │
│ (PG)  │ │ Studio │ │ (opt)  │
└───────┘ └────────┘ └────────┘
```

### Data Flow

```
User → Frontend → Backend API → AIService → LM Studio (Mistral)
                      ↓
                 PostgreSQL
                      ↓
              Structured Data
```

---

## 📦 Prerequisites

### Required

- **Python**: 3.12+
- **Node.js**: 18+
- **PostgreSQL**: 14+
- **LM Studio**: Latest version
- **Mistral Model**: 7B (quantized Q4 or Q8)

### Optional

- Git
- Docker (for containerized deployment)

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/aiset.git
cd aiset
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Database Setup

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE syseng_tool;
\q

# Initialize schema
python -c "from database.database import init_db; init_db()"
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env if needed (default: http://localhost:8000)
```

### 5. LM Studio Configuration

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Download Mistral-7B model (Q4 or Q8 quantization)
3. Load the model and start the local server
4. Ensure it's running on `http://localhost:1234`

---

## 🎮 Usage

### Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
# Backend runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:5173
```

**Terminal 3 - LM Studio:**
- Launch LM Studio app
- Load Mistral model
- Start local server

### Using the Application

1. **Open** http://localhost:5173 in your browser
2. **Create/Select a Project** from the dropdown
3. **Start Conversation** with AI (Chat tab)
4. **Describe your system** in natural language
5. **Validate extracted requirements** (Validation tab)
6. **Review approved requirements** (Requirements tab)

### Example Workflow

```
User: "I want to build a library management system. 
       Librarians should manage book loans and returns."

AI: "I've identified 3 requirements:
     - REQ-001: Loan management
     - REQ-002: Return processing
     - REQ-003: Overdue penalty calculation
     Do you want to add more details?"

User validates → Requirements stored → Traceability maintained
```

---

## 📁 Project Structure

```
aiset/
├── backend/
│   ├── api/
│   │   ├── project_router.py    # Project endpoints
│   │   └── ai_router.py          # AI conversation endpoints
│   ├── services/
│   │   └── ai_service.py         # LM Studio integration
│   ├── models/
│   │   └── models.py             # SQLAlchemy models
│   ├── database/
│   │   └── database.py           # Database connection
│   ├── main.py                   # FastAPI application
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProjectDashboard.tsx
│   │   │   └── EntityValidation.tsx
│   │   ├── services/
│   │   │   └── apiService.ts     # API client
│   │   ├── types/
│   │   │   └── index.ts          # TypeScript definitions
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── .env
│
├── database/
│   └── schema.sql                # Complete database schema
│
├── docs/
│   ├── API.md                    # API documentation
│   ├── DATABASE.md               # Database schema docs
│   └── WORKFLOW.md               # User workflows
│
├── tests/
│   ├── test_backend.py
│   └── test_frontend.html
│
└── README.md
```

---

## 🛠️ Technologies

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for PostgreSQL
- **Pydantic**: Data validation
- **OpenAI SDK**: For LM Studio API compatibility

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **Fetch API**: HTTP requests

### AI
- **LM Studio**: Local model hosting
- **Mistral 7B**: Language model
- **Custom prompts**: Optimized for requirements extraction

### Database
- **PostgreSQL 14+**: Relational database
- **15+ tables**: Complete data model
- **JSONB support**: Flexible metadata storage

---

## 🗺️ Roadmap

### ✅ Phase 1 - MVP (Completed)
- [x] AI conversational interface
- [x] Requirements extraction
- [x] Validation workflow
- [x] Basic traceability
- [x] Project management

### 🚧 Phase 2 - Enhanced Features (In Progress)
- [ ] Export to PDF/Word
- [ ] Design component management
- [ ] Traceability matrix visualization
- [ ] Gap detection
- [ ] Conflict resolution

### 📅 Phase 3 - Enterprise Features (Planned)
- [ ] Multi-user collaboration
- [ ] Role-based access control
- [ ] Jira/GitHub integration
- [ ] Advanced analytics dashboard
- [ ] CI/CD pipeline integration
- [ ] Docker deployment

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Integration Tests
```bash
# Run test_full_workflow.py
cd tests
python test_full_workflow.py
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards
- **Python**: PEP 8, type hints
- **TypeScript**: ESLint, Prettier
- **Commits**: Conventional Commits format

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)

---

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for Claude AI
- [LM Studio](https://lmstudio.ai/) for local model hosting
- [Mistral AI](https://mistral.ai/) for the language model
- Systems Engineering community for best practices

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/aiset/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/aiset/discussions)
- **Email**: your.email@example.com

---

## 🔒 Security

For security issues, please email security@yourdomain.com instead of using the issue tracker.

---

**⭐ If this project helps you, consider giving it a star!**

---

*Last updated: November 2025*
