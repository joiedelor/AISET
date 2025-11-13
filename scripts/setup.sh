#!/bin/bash
# AISET Setup Script
# DO-178C Traceability: REQ-SETUP-001
# Purpose: Initial project setup

set -e

echo "🚀 AISET Setup Script"
echo "====================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.12"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required (found $python_version)"
    exit 1
fi
echo "✓ Python $python_version"

# Check Node version
echo "Checking Node.js version..."
node_version=$(node --version 2>&1 | sed 's/v//')
required_node="20.0.0"

if [ "$(printf '%s\n' "$required_node" "$node_version" | sort -V | head -n1)" != "$required_node" ]; then
    echo "❌ Node.js $required_node or higher is required (found $node_version)"
    exit 1
fi
echo "✓ Node.js $node_version"

# Check PostgreSQL
echo "Checking PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo "⚠ PostgreSQL not found. You'll need to install it or use Docker."
else
    pg_version=$(psql --version | awk '{print $3}')
    echo "✓ PostgreSQL $pg_version"
fi

echo ""
echo "📦 Installing Dependencies"
echo "=========================="

# Backend setup
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Backend dependencies installed"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file (please configure with your settings)"
fi

cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install
echo "✓ Frontend dependencies installed"
cd ..

echo ""
echo "🗄️  Database Setup"
echo "=================="
echo "To initialize the database:"
echo "1. Ensure PostgreSQL is running"
echo "2. Create database: createdb aiset_db"
echo "3. Run: cd backend && python -c 'from database.connection import init_db; init_db()'"

echo ""
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Configure backend/.env with your API keys and database URL"
echo "2. Start the database (or use Docker: docker-compose up -d postgres)"
echo "3. Initialize the database schema"
echo "4. Run the application:"
echo "   - Backend: cd backend && uvicorn main:app --reload"
echo "   - Frontend: cd frontend && npm run dev"
echo "   - Or use Docker: docker-compose up"
echo ""
echo "📚 Documentation: docs/DO178C_COMPLIANCE.md"
echo "🔍 Traceability: docs/TRACEABILITY_MATRIX.md"
echo ""
echo "Happy engineering! 🎯"
