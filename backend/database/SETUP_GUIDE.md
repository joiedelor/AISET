# AISET Database Setup and Deployment Guide

**Version:** 1.0.0
**Date:** 2025-11-16
**For:** Solo developer (PostgreSQL on WSL2/Ubuntu)
**Audience:** You can review and execute this yourself

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Initial Setup](#initial-setup)
4. [Deployment Options](#deployment-options)
5. [Verification](#verification)
6. [Maintenance](#maintenance)
7. [Backup and Recovery](#backup-and-recovery)
8. [Troubleshooting](#troubleshooting)
9. [Security](#security)

---

## Quick Start

**If you just want to get the database running:**

```bash
# 1. Start PostgreSQL
sudo service postgresql start

# 2. Navigate to backend
cd /home/joiedelor/aiset/backend

# 3. Deploy using Alembic (recommended)
alembic upgrade head

# 4. Verify
PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql -h localhost -U aiset_user -d aiset_db -c "\dt"

# Done! You should see 47 tables
```

---

## Prerequisites

### 1. PostgreSQL 15+ Installed

```bash
# Check if installed
psql --version

# If not installed (Ubuntu/WSL2):
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### 2. Database User Exists

**You already have:** `aiset_user` with password `3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R`

To verify:
```bash
PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql -h localhost -U aiset_user -d postgres -c "SELECT current_user;"
```

### 3. Database Exists

**You already have:** `aiset_db`

To verify:
```bash
PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql -h localhost -U aiset_user -d aiset_db -c "SELECT current_database();"
```

### 4. Python Dependencies

```bash
cd /home/joiedelor/aiset/backend
source venv/bin/activate
pip install alembic psycopg2-binary sqlalchemy
```

---

## Initial Setup

### Option A: Using Alembic (Recommended - Version Controlled)

```bash
cd /home/joiedelor/aiset/backend

# Apply all migrations
alembic upgrade head
```

**Why this is recommended:**
- ✅ Version controlled (can track changes)
- ✅ Reversible (can downgrade if needed)
- ✅ Team-friendly (if you add collaborators later)
- ✅ DO-178C compliant (migration history = audit trail)

### Option B: Using Direct SQL (Fast, but no version control)

```bash
cd /home/joiedelor/aiset/backend

PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql \
  -h localhost \
  -U aiset_user \
  -d aiset_db \
  -f database/schema_v1.sql
```

**When to use this:**
- Quick testing
- Resetting development database
- You don't need migration history

---

## Deployment Options

### Development Environment (Your Current Setup)

```bash
# Start PostgreSQL (if not running)
sudo service postgresql start

# Deploy schema
cd /home/joiedelor/aiset/backend
alembic upgrade head

# Verify
alembic current
```

### Production Environment (Future)

**Checklist before production:**
- [ ] Change default password
- [ ] Enable SSL connections
- [ ] Configure PostgreSQL for performance (shared_buffers, work_mem)
- [ ] Set up automated backups
- [ ] Configure pg_hba.conf for restricted access
- [ ] Enable connection pooling (pgBouncer)
- [ ] Monitor with pg_stat_statements

---

## Verification

### Check Table Count

```bash
PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql \
  -h localhost -U aiset_user -d aiset_db \
  -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"
```

**Expected:** 47 tables

### Check Tables Exist

```bash
PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql \
  -h localhost -U aiset_user -d aiset_db \
  -c "\dt"
```

**You should see:**
- users, roles, teams
- projects, project_standards
- configuration_items, bill_of_materials
- requirements, traceability_links
- ... (all 47 tables)

### Check Hybrid Identifier System

```bash
PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql \
  -h localhost -U aiset_user -d aiset_db \
  -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='configuration_items' AND column_name IN ('guid', 'display_id');"
```

**Expected:**
- `guid` - uuid
- `display_id` - character varying

### Check Extensions

```bash
PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql \
  -h localhost -U aiset_user -d aiset_db \
  -c "\dx"
```

**Expected:** `pgcrypto` (for UUID generation)

### Check Triggers

```bash
PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql \
  -h localhost -U aiset_user -d aiset_db \
  -c "SELECT tgname, tgrelid::regclass FROM pg_trigger WHERE tgname LIKE 'update_%_updated_at';"
```

**Expected:** Multiple triggers for automatic `updated_at` updates

---

## Maintenance

### Regular Tasks

#### 1. Vacuum and Analyze (Weekly)

```bash
PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql \
  -h localhost -U aiset_user -d aiset_db \
  -c "VACUUM ANALYZE;"
```

**What this does:**
- Reclaims storage from deleted rows
- Updates query planner statistics
- Improves query performance

#### 2. Check Database Size

```bash
PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql \
  -h localhost -U aiset_user -d aiset_db \
  -c "SELECT pg_size_pretty(pg_database_size('aiset_db'));"
```

#### 3. Check Table Sizes

```bash
PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql \
  -h localhost -U aiset_user -d aiset_db \
  -c "SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables WHERE schemaname='public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;"
```

#### 4. Release Expired Locks (Daily or as-needed)

```bash
PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql \
  -h localhost -U aiset_user -d aiset_db \
  -c "SELECT check_expired_locks();"
```

---

## Backup and Recovery

### Manual Backup

```bash
# Full database backup
pg_dump -h localhost -U aiset_user -d aiset_db \
  -F c -b -v \
  -f ~/aiset_backups/aiset_db_$(date +%Y%m%d_%H%M%S).backup

# Schema-only backup
pg_dump -h localhost -U aiset_user -d aiset_db \
  --schema-only \
  -f ~/aiset_backups/aiset_db_schema_$(date +%Y%m%d).sql
```

### Automated Backup (Cron)

Add to crontab (`crontab -e`):

```bash
# Daily backup at 2 AM
0 2 * * * PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" pg_dump -h localhost -U aiset_user -d aiset_db -F c -b -f ~/aiset_backups/aiset_db_$(date +\%Y\%m\%d).backup

# Weekly cleanup (keep last 30 days)
0 3 * * 0 find ~/aiset_backups -name "aiset_db_*.backup" -mtime +30 -delete
```

### Restore from Backup

```bash
# Drop existing database (⚠️ CAREFUL!)
dropdb -h localhost -U aiset_user aiset_db

# Create fresh database
createdb -h localhost -U aiset_user aiset_db

# Restore
pg_restore -h localhost -U aiset_user -d aiset_db \
  ~/aiset_backups/aiset_db_20251116_140000.backup
```

---

## Troubleshooting

### Problem: "Connection refused"

```bash
# Check if PostgreSQL is running
sudo service postgresql status

# Start if not running
sudo service postgresql start
```

### Problem: "Database does not exist"

```bash
# Create database
createdb -h localhost -U aiset_user aiset_db

# Then apply migrations
cd /home/joiedelor/aiset/backend
alembic upgrade head
```

### Problem: "Role does not exist"

```bash
# Connect as postgres superuser
sudo -u postgres psql

# Create user
CREATE USER aiset_user WITH PASSWORD '3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R';
ALTER USER aiset_user CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE aiset_db TO aiset_user;
\q
```

### Problem: "Too many connections"

```bash
# Check current connections
PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql \
  -h localhost -U aiset_user -d aiset_db \
  -c "SELECT count(*) FROM pg_stat_activity WHERE datname='aiset_db';"

# Kill idle connections
PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql \
  -h localhost -U aiset_user -d aiset_db \
  -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='aiset_db' AND state='idle' AND state_change < NOW() - INTERVAL '1 hour';"
```

### Problem: "Slow queries"

```bash
# Enable query logging (edit postgresql.conf)
sudo nano /etc/postgresql/15/main/postgresql.conf

# Add/uncomment:
# log_min_duration_statement = 1000  # Log queries > 1 second
# log_statement = 'all'              # Log all queries (verbose!)

# Restart PostgreSQL
sudo service postgresql restart

# View logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### Problem: "Table already exists" (during migration)

```bash
# Check migration status
alembic current

# If database is ahead of migrations:
alembic stamp head

# If database is behind:
alembic upgrade head

# If completely out of sync (⚠️ nuclear option):
alembic downgrade base  # Destroys all data!
alembic upgrade head    # Re-apply all migrations
```

---

## Security

### 1. Change Default Password (Production)

```sql
-- Connect as postgres
sudo -u postgres psql

-- Change password
ALTER USER aiset_user WITH PASSWORD 'new_secure_password_here';
\q
```

**Then update:**
- `alembic.ini` - `sqlalchemy.url`
- Backend connection string
- Environment variables

### 2. Restrict Network Access

Edit `/etc/postgresql/15/main/pg_hba.conf`:

```
# TYPE  DATABASE    USER        ADDRESS         METHOD

# Local connections
local   aiset_db    aiset_user                  md5

# Localhost only (default)
host    aiset_db    aiset_user  127.0.0.1/32    md5
host    aiset_db    aiset_user  ::1/128         md5

# Specific IP range (if needed)
# host    aiset_db    aiset_user  192.168.1.0/24  md5
```

Reload PostgreSQL:
```bash
sudo service postgresql reload
```

### 3. Enable SSL (Production)

```bash
# Generate SSL certificate
sudo openssl req -new -x509 -days 365 -nodes \
  -text -out /etc/ssl/certs/server.crt \
  -keyout /etc/ssl/private/server.key

# Set permissions
sudo chmod 600 /etc/ssl/private/server.key
sudo chown postgres:postgres /etc/ssl/private/server.key
sudo chown postgres:postgres /etc/ssl/certs/server.crt

# Edit postgresql.conf
sudo nano /etc/postgresql/15/main/postgresql.conf

# Enable SSL
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'

# Restart
sudo service postgresql restart
```

### 4. Audit Trail Monitoring

```sql
-- Check recent audit trail entries
SELECT
  table_name,
  operation,
  changed_by_guid,
  changed_at
FROM audit_trail
ORDER BY changed_at DESC
LIMIT 20;

-- Check suspicious activity
SELECT
  user_guid,
  activity_type,
  activity_result,
  occurred_at
FROM activity_log
WHERE activity_result = 'failed'
ORDER BY occurred_at DESC
LIMIT 20;
```

---

## Performance Tuning

### For Development (Current)

PostgreSQL defaults are fine for development.

### For Production (Future)

Edit `/etc/postgresql/15/main/postgresql.conf`:

```
# Memory settings (adjust based on available RAM)
shared_buffers = 2GB                 # 25% of RAM
effective_cache_size = 6GB           # 50-75% of RAM
work_mem = 50MB                      # For sorting/hashing
maintenance_work_mem = 512MB         # For VACUUM, index creation

# Parallelism (adjust based on CPU cores)
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_worker_processes = 8

# Write-ahead log
wal_buffers = 16MB
checkpoint_completion_target = 0.9

# Query planner
random_page_cost = 1.1              # For SSD storage
effective_io_concurrency = 200      # For SSD storage

# Logging
log_min_duration_statement = 1000   # Log slow queries (>1s)
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

Restart after changes:
```bash
sudo service postgresql restart
```

---

## Database Information

**Created:** 2025-11-16
**Schema Version:** 1.0.0 (schema_v1.sql)
**Migration:** 20251116_001 (Alembic)
**Total Tables:** 47
**Requirements Coverage:** REQ-DB-001 through REQ-DB-070 (all 70)
**Traceability:** LLD_Database_Schema_Design.md v1.0.0

**Key Features:**
- ✅ Hybrid identifiers (guid + display_id) on all tables
- ✅ Audit trail (created_at, updated_at, created_by, updated_by)
- ✅ Soft deletes (deleted_at)
- ✅ Version stamping for optimistic locking
- ✅ Pessimistic locking for check-out/check-in (ci_locks)
- ✅ RBAC with 7 role types and CI-level ACL
- ✅ Multi-instance merge support (source_instances, id_mappings, merge_conflicts)
- ✅ Full-text search on CIs and requirements
- ✅ Automatic timestamp updates (triggers)
- ✅ Complete audit trail with before/after snapshots

---

## Quick Reference Commands

```bash
# Start PostgreSQL
sudo service postgresql start

# Connect to database
PGPASSWORD="3/P5JDV/KWR6nwCfwtKOpvbarwCDn88R" psql -h localhost -U aiset_user -d aiset_db

# Apply migrations
cd /home/joiedelor/aiset/backend && alembic upgrade head

# Check migration status
alembic current

# Backup database
pg_dump -h localhost -U aiset_user -d aiset_db -F c -f ~/aiset_backup_$(date +%Y%m%d).backup

# List tables
\dt

# Describe table
\d configuration_items

# Check table size
SELECT pg_size_pretty(pg_total_relation_size('configuration_items'));

# Vacuum
VACUUM ANALYZE;

# Release expired locks
SELECT check_expired_locks();
```

---

## Getting Help

**Documentation:**
- This guide (SETUP_GUIDE.md)
- Alembic README (backend/alembic/README.md)
- LLD (03_DESIGN/LLD_Database_Schema_Design.md)
- Schema DDL (backend/database/schema_v1.sql)

**PostgreSQL Documentation:**
- https://www.postgresql.org/docs/15/

**Alembic Documentation:**
- https://alembic.sqlalchemy.org/

---

**Last Updated:** 2025-11-16
**Maintained by:** You (solo developer)
**Status:** Ready for Development Use
