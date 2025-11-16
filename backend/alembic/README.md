# AISET Database Migrations (Alembic)

**Version:** 1.0.0
**Date:** 2025-11-16
**Purpose:** Version-controlled database schema migrations for AISET

---

## What is Alembic?

Alembic is a database migration tool for SQLAlchemy (Python). It allows you to:
- Track database schema changes over time
- Apply migrations incrementally (upgrade)
- Revert migrations if needed (downgrade)
- Collaborate on schema changes (version control)

---

## Directory Structure

```
backend/
├── alembic.ini          # Alembic configuration
├── alembic/
│   ├── env.py           # Migration environment setup
│   ├── script.py.mako   # Template for new migrations
│   ├── README.md        # This file
│   └── versions/        # Migration files (chronological)
│       └── 20251116_001_initial_schema_v1.py  # Initial 47 tables
└── database/
    └── schema_v1.sql    # Complete DDL (for reference)
```

---

## Quick Start

### Prerequisites

```bash
# Install Alembic (if not already installed)
pip install alembic

# Ensure PostgreSQL is running
sudo service postgresql start

# Set database connection (or use alembic.ini default)
export DATABASE_URL="postgresql://aiset_user:your_password@localhost:5432/aiset_db"
```

### Apply Migrations (Upgrade)

```bash
# Navigate to backend directory
cd /home/joiedelor/aiset/backend

# View current database version
alembic current

# View migration history
alembic history --verbose

# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade 20251116_001
```

### Revert Migrations (Downgrade)

```bash
# Revert one migration
alembic downgrade -1

# Revert to specific version
alembic downgrade 20251116_001

# Revert all migrations (⚠️ DESTROYS ALL DATA!)
alembic downgrade base
```

### Create New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new_table for feature_x"

# Create empty migration (manual)
alembic revision -m "Add index on configuration_items.part_number"

# Edit the generated file in alembic/versions/
# Then apply with: alembic upgrade head
```

---

## Migration Workflow

### For Solo Development (You)

1. **Make schema changes** in design documents (LLD)
2. **Create migration file:**
   ```bash
   alembic revision -m "Add column xyz to table abc"
   ```
3. **Edit migration file** in `alembic/versions/`
   - Add `upgrade()` code (CREATE, ALTER, etc.)
   - Add `downgrade()` code (revert changes)
4. **Test migration:**
   ```bash
   alembic upgrade head     # Apply
   # Test your application
   alembic downgrade -1     # Revert
   # Fix if needed, repeat
   alembic upgrade head     # Re-apply
   ```
5. **Commit migration file** to Git
6. **Update LLD documentation** to match implementation

### For Team Development (Future)

- Each developer creates migrations for their features
- Git tracks migration files
- Alembic resolves migration order
- Team members apply migrations with `alembic upgrade head`

---

## Important Commands Reference

| Command | Purpose |
|---------|---------|
| `alembic current` | Show current database version |
| `alembic history` | Show all migrations |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic upgrade +1` | Apply next migration |
| `alembic downgrade -1` | Revert last migration |
| `alembic downgrade base` | Revert all (⚠️ DANGER) |
| `alembic revision -m "msg"` | Create new migration |
| `alembic stamp head` | Mark DB as current (no changes) |

---

## Migrations vs Direct SQL

### Use Alembic Migrations When:
- ✅ Making schema changes (ALTER TABLE, CREATE TABLE)
- ✅ Adding/removing columns
- ✅ Changing indexes or constraints
- ✅ Need to track changes over time
- ✅ Working with a team
- ✅ Deploying to multiple environments (dev, staging, production)

### Use Direct SQL (schema_v1.sql) When:
- ✅ Fresh database installation
- ✅ Resetting development database
- ✅ Creating test databases
- ✅ Documentation reference

---

## Initial Migration (20251116_001)

The first migration creates the complete AISET schema with:

**47 Tables:**
1. Users & Auth (users, roles, teams)
2. Projects (projects, project_standards, lifecycles)
3. Source Instances (source_instances)
4. Suppliers (suppliers)
5. Configuration Items (configuration_items, bill_of_materials, ci_baselines)
6. Requirements (requirements, traceability_links, requirement_changes)
7. Design (design_elements)
8. Collaboration (user_sessions, ci_locks, work_assignments)
9. RBAC (user_roles, team_members, team_permissions, ci_access_control_list)
10. Merge (id_mappings, merge_sessions, merge_conflicts, duplicate_candidates)
11. AI (ai_conversations, ai_messages)
12. Documents (documents, document_associations)
13. Notifications (notifications, comments)
14. Audit (activity_log, audit_trail)

**Features:**
- Hybrid identifiers (guid + display_id) on all tables
- Audit trail (created_at, updated_at, created_by, updated_by)
- Soft deletes (deleted_at)
- Version stamping for optimistic locking
- Comprehensive indexes for performance
- Full-text search on CIs and requirements
- Automatic timestamp updates (triggers)

**Traceability:**
- REQ-DB-001 through REQ-DB-070 (all 70 database requirements)
- Based on LLD_Database_Schema_Design.md v1.0.0

---

## Troubleshooting

### "No module named 'alembic'"
```bash
pip install alembic
```

### "Can't connect to database"
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Check connection string
echo $DATABASE_URL

# Or edit alembic.ini and set sqlalchemy.url
```

### "Current revision: None"
```bash
# Database is empty - apply initial migration
alembic upgrade head
```

### "Multiple heads detected"
```bash
# Merge multiple migration branches
alembic merge heads -m "merge branches"
```

### Migration fails halfway
```bash
# Revert to last known good state
alembic downgrade <previous_version>

# Fix the migration file
# Re-apply
alembic upgrade head
```

---

## DO-178C Compliance Notes

Alembic migrations support DO-178C configuration management by:

1. **Version Control:** Each migration is version-controlled (Git)
2. **Traceability:** Migration IDs and messages trace to requirements
3. **Reversibility:** All migrations have downgrade() for rollback
4. **Audit Trail:** Migration history shows who/when/what changed
5. **Testing:** Migrations can be tested before production deployment

**For Certification:**
- Keep migration files in Git
- Document each migration's purpose and requirements
- Test both upgrade() and downgrade() paths
- Review migrations as part of design review

---

## Examples

### Example 1: Add a New Column

```python
# In alembic/versions/xxx_add_ci_color.py

def upgrade() -> None:
    op.add_column('configuration_items',
                  sa.Column('color', sa.String(50), nullable=True))

def downgrade() -> None:
    op.drop_column('configuration_items', 'color')
```

### Example 2: Create an Index

```python
def upgrade() -> None:
    op.create_index('idx_ci_color',
                    'configuration_items',
                    ['color'])

def downgrade() -> None:
    op.drop_index('idx_ci_color')
```

### Example 3: Add a Foreign Key

```python
def upgrade() -> None:
    op.create_foreign_key('fk_ci_color_ref',
                          'configuration_items', 'colors',
                          ['color'], ['name'])

def downgrade() -> None:
    op.drop_constraint('fk_ci_color_ref',
                       'configuration_items',
                       type_='foreignkey')
```

---

## References

- **Alembic Documentation:** https://alembic.sqlalchemy.org/
- **AISET LLD:** `03_DESIGN/LLD_Database_Schema_Design.md`
- **AISET Schema DDL:** `backend/database/schema_v1.sql`
- **Requirements:** `REQUIREMENTS.md` v0.8.0 (REQ-DB-001 through REQ-DB-070)

---

**Last Updated:** 2025-11-16
**Maintainer:** AISET Development Team
**Status:** Initial Setup Complete
