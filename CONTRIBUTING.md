# Contributing to AISET

**Document Type:** [Level 1] AISET Tool Development
**Version:** 1.0.0
**Last Updated:** 2025-11-22

Thank you for your interest in contributing to AISET! This document provides guidelines and information for contributors.

## 🎯 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards others

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 15+
- Git

### Development Setup

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/yourusername/aiset.git
cd aiset
```

3. Run the setup script:
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

4. Create a branch:
```bash
git checkout -b feature/your-feature-name
```

## 📝 Coding Standards

### Python (Backend)

- Follow **PEP 8** style guide
- Use **type hints** for all functions
- Write **docstrings** for all modules, classes, and functions
- Include **DO-178C traceability** comments:
  ```python
  """
  Module Description
  DO-178C Traceability: REQ-XXX-YYY
  Purpose: What this module does
  """
  ```
- Maximum line length: 100 characters
- Use meaningful variable names

**Example:**
```python
def create_requirement(
    self,
    project_id: int,
    requirement_id: str,
    title: str,
    description: str,
) -> Requirement:
    """
    Create a new requirement.

    Traceability: REQ-REQ-003

    Args:
        project_id: Project identifier
        requirement_id: Unique requirement ID
        title: Requirement title
        description: Detailed description

    Returns:
        Created Requirement instance
    """
    # Implementation
```

### TypeScript (Frontend)

- Follow **ESLint** rules
- Use **TypeScript strict mode**
- Define **interfaces** for all data structures
- Include **traceability comments**:
  ```typescript
  /**
   * Component Description
   * DO-178C Traceability: REQ-FRONTEND-XXX
   * Purpose: What this component does
   */
  ```
- Use functional components with hooks
- Prefer named exports

**Example:**
```typescript
/**
 * Requirements Page
 * DO-178C Traceability: REQ-FRONTEND-011
 * Purpose: Display and manage requirements
 */
export default function Requirements() {
  // Implementation
}
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest --cov=. --cov-report=html
```

**Test Requirements:**
- Unit tests for all services
- Integration tests for API endpoints
- Minimum 80% code coverage for new code
- All tests must pass before PR

### Frontend Tests

```bash
cd frontend
npm run test
```

## 📚 Documentation

- Update relevant documentation for any changes
- Add docstrings/JSDoc comments to new functions
- Update README.md for new features
- Update DO-178C traceability documentation

## 🔀 Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/descriptive-name
   ```

2. **Make Changes**
   - Follow coding standards
   - Write tests
   - Update documentation

3. **Commit Changes**
   Use conventional commits format:
   ```bash
   git commit -m "feat: add requirement validation"
   git commit -m "fix: resolve traceability bug"
   git commit -m "docs: update API documentation"
   ```

   **Commit Types:**
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation only
   - `style`: Code style changes (formatting)
   - `refactor`: Code refactoring
   - `test`: Adding tests
   - `chore`: Maintenance tasks

4. **Push to Fork**
   ```bash
   git push origin feature/descriptive-name
   ```

5. **Create Pull Request**
   - Provide clear description
   - Reference related issues
   - Include DO-178C traceability
   - Add screenshots for UI changes

6. **Code Review**
   - Address review feedback
   - Update as needed
   - Maintain clean commit history

## 🐛 Reporting Bugs

Use GitHub Issues with the bug template:

**Required Information:**
- AISET version
- Operating system
- Python/Node.js version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/logs

## 💡 Suggesting Features

Use GitHub Issues with the feature template:

**Required Information:**
- Feature description
- Use case / problem it solves
- Proposed implementation (optional)
- DO-178C compliance considerations

## 🏗️ Architecture Guidelines

### Backend Structure

```
backend/
├── models/          # SQLAlchemy models
├── services/        # Business logic
├── routers/         # API endpoints
├── database/        # Database configuration
├── config/          # Settings
└── tests/           # Test suites
```

### Frontend Structure

```
frontend/src/
├── components/      # Reusable React components
├── pages/           # Page components
├── services/        # API client
├── types/           # TypeScript types
└── utils/           # Utility functions
```

## 🔒 Security

- **Never commit secrets** (.env files, API keys)
- Use environment variables for configuration
- Validate all user inputs
- Follow OWASP security guidelines
- Report security vulnerabilities privately

## 📋 Checklist Before Submitting PR

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No linting errors
- [ ] DO-178C traceability maintained
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [DO-178C Overview](https://en.wikipedia.org/wiki/DO-178C)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## 📞 Getting Help

- GitHub Discussions for questions
- GitHub Issues for bugs/features
- Code review feedback for improvements

## 🙏 Thank You!

Your contributions make AISET better for everyone in the aerospace and safety-critical systems community!

---

**Happy Contributing! 🚀**
