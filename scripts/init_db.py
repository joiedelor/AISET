#!/usr/bin/env python3
"""
Database Initialization Script
DO-178C Traceability: REQ-SETUP-002
Purpose: Initialize database schema and create sample data
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database.connection import init_db, SessionLocal, engine
from models import *
from sqlalchemy import inspect

def check_database_connection():
    """Check if database is accessible."""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_tables():
    """Create all database tables."""
    print("\n📊 Creating database tables...")
    try:
        init_db()

        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"✓ Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")

        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def create_sample_project():
    """Create a sample project for testing."""
    print("\n🎯 Creating sample project...")

    db = SessionLocal()
    try:
        # Check if sample project already exists
        from models.project import Project
        existing = db.query(Project).filter(Project.project_code == "AISET-DEMO-001").first()

        if existing:
            print("⚠ Sample project already exists")
            return

        # Create sample project
        project = Project(
            name="AISET Demo Project",
            description="Sample project for testing AISET features",
            project_code="AISET-DEMO-001",
            certification_level="C",
            industry="aerospace",
            status="active",
            created_by="system"
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        print(f"✓ Created sample project: {project.name} (ID: {project.id})")

    except Exception as e:
        print(f"❌ Failed to create sample project: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main initialization function."""
    print("🚀 AISET Database Initialization")
    print("=" * 50)

    # Check database connection
    if not check_database_connection():
        print("\n❌ Please ensure PostgreSQL is running and configured correctly.")
        print("Check your DATABASE_URL in .env file.")
        sys.exit(1)

    # Create tables
    if not create_tables():
        print("\n❌ Database initialization failed.")
        sys.exit(1)

    # Create sample data
    create_sample_project()

    print("\n" + "=" * 50)
    print("✅ Database initialization complete!")
    print("\nYou can now start the application:")
    print("  Backend: uvicorn main:app --reload")
    print("  Frontend: npm run dev")
    print("\nAccess the application at:")
    print("  API: http://localhost:8000")
    print("  Frontend: http://localhost:5173")
    print("  API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
