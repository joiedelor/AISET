# Documentation Consistency Strategy

**Version:** 1.0
**Date:** 2025-11-16
**Purpose:** Prevent documentation inconsistencies across the project

---

## Problem Statement

Documentation inconsistencies occur when the same information is duplicated across multiple files and updates are applied inconsistently:

**Recent Example:**
- Database table count changed from 42 → 47
- REQUIREMENTS.md renamed to ROLEPLAY_REQUIREMENTS.md + SRS created
- DO-178C compliance changed 25% → 40%

**Result:** Inconsistencies in Claude.md, PROJECT_STATUS.md, DOCUMENTATION_LEVELS.md, DOCUMENTATION_STRUCTURE.md, PROJECT_STRUCTURE.md

---

## Proposed Solutions

### **Solution 1: Single Source of Truth (SSOT) - Metrics File** ⭐ RECOMMENDED

**Create:** `PROJECT_METRICS.md` as the **ONLY** place where key metrics are defined.

**Structure:**
```markdown
# Project Metrics - Single Source of Truth

**Last Updated:** 2025-11-16 21:00 UTC
**Version:** 0.5.0

## Database Metrics
- **Total Tables:** 47
- **Database Engine:** PostgreSQL 15+
- **Schema Status:** DDL implemented (schema_v1.sql)
- **Migration Framework:** Alembic

## Requirements Metrics
- **Total Requirements:** 167
  - AI: 44
  - Frontend: 23
  - Backend: 29
  - Database: 70
  - Documentation: 1
- **Official Document:** 02_REQUIREMENTS/SRS_Software_Requirements_Specification.md v1.0.0
- **Working File:** ROLEPLAY_REQUIREMENTS.md v0.8.0 (source material)

## DO-178C Compliance
- **Overall:** 40%
- **Requirements:** 100% ✅
- **Design:** 90%
- **Traceability:** 100% ✅
- **Verification:** 10%
- **Code Quality:** 40%

## File Counts
- **Source Files:** 68
- **DO-178C Documents:** 20+
- **Lines of Code:** ~8,000 (source) + ~6,500 (design/reviews)

## Design Documents
- **HLD:** 03_DESIGN/HLD_High_Level_Design.md (800+ lines)
- **LLD:** 03_DESIGN/LLD_Database_Schema_Design.md (1400+ lines)
- **Traceability:** 08_TRACEABILITY/Requirements_to_Design_Traceability.md (600+ lines)
```

**Other files reference this:**
```markdown
<!-- In Claude.md, PROJECT_STATUS.md, etc. -->
**Database:** See PROJECT_METRICS.md - currently {{47 tables}}
**DO-178C Compliance:** See PROJECT_METRICS.md - currently {{40%}}
```

**Benefits:**
- ✅ Single place to update metrics
- ✅ Clear ownership of metrics
- ✅ Easy to find current values
- ❌ Still requires manual updates in referencing files

---

### **Solution 2: Automated Consistency Checks** ⭐ RECOMMENDED

**Create:** `.github/workflows/doc-consistency-check.yml` or local script

**Script:** `scripts/check_documentation_consistency.sh`

```bash
#!/bin/bash
# Documentation Consistency Checker

echo "Checking documentation consistency..."

# Source metrics from PROJECT_METRICS.md
DB_TABLES=$(grep "Total Tables:" PROJECT_METRICS.md | grep -oP '\d+')
REQUIREMENTS=$(grep "Total Requirements:" PROJECT_METRICS.md | grep -oP '\d+')
COMPLIANCE=$(grep "Overall:" PROJECT_METRICS.md | grep -oP '\d+')

# Check all documentation files
ISSUES=0

# Check database table references
echo "Checking database table count..."
for FILE in Claude.md PROJECT_STATUS.md DOCUMENTATION_STRUCTURE.md PROJECT_STRUCTURE.md; do
    if grep -q "42 table" "$FILE"; then
        echo "❌ ERROR: $FILE still references 42 tables (should be $DB_TABLES)"
        ISSUES=$((ISSUES + 1))
    fi
done

# Check requirements references
echo "Checking requirements references..."
for FILE in Claude.md PROJECT_STATUS.md DOCUMENTATION_LEVELS.md; do
    if grep -q "REQUIREMENTS.md" "$FILE" && ! grep -q "ROLEPLAY_REQUIREMENTS.md" "$FILE"; then
        echo "⚠️  WARNING: $FILE may have outdated REQUIREMENTS.md reference"
    fi
done

# Check DO-178C compliance
echo "Checking DO-178C compliance percentages..."
if grep -q "25%" Claude.md && ! grep -q "40%" Claude.md; then
    echo "❌ ERROR: Claude.md has outdated compliance percentage"
    ISSUES=$((ISSUES + 1))
fi

if [ $ISSUES -eq 0 ]; then
    echo "✅ All documentation consistency checks passed!"
    exit 0
else
    echo "❌ Found $ISSUES documentation inconsistencies"
    exit 1
fi
```

**Usage:**
```bash
# Before committing
./scripts/check_documentation_consistency.sh

# In GitHub Actions (optional)
# Runs automatically on PR to catch inconsistencies
```

**Benefits:**
- ✅ Automated detection of inconsistencies
- ✅ Can run before commits
- ✅ Can integrate with CI/CD
- ❌ Requires maintenance of check script

---

### **Solution 3: Documentation Generation from Code**

**For database metrics:**
```python
# scripts/update_db_metrics.py
import re

# Count tables in schema_v1.sql
with open('backend/database/schema_v1.sql', 'r') as f:
    schema = f.read()
    table_count = len(re.findall(r'CREATE TABLE', schema))

# Update PROJECT_METRICS.md
with open('PROJECT_METRICS.md', 'r+') as f:
    content = f.read()
    content = re.sub(r'Total Tables:\*\* \d+', f'Total Tables:** {table_count}', content)
    f.seek(0)
    f.write(content)
    f.truncate()

print(f"✅ Updated database table count to {table_count}")
```

**Benefits:**
- ✅ Truth comes from source code
- ✅ Can't get out of sync
- ❌ Only works for metrics derivable from code
- ❌ Requires Python scripts

---

### **Solution 4: Template Variables** (Advanced)

**Use a documentation preprocessor:**
```markdown
<!-- In Claude.md -->
**Database:** PostgreSQL 15+ ({{DB_TABLES}} tables)
**DO-178C Compliance:** {{COMPLIANCE_OVERALL}}%

<!-- Variables defined in PROJECT_METRICS.md -->
<!-- Build step expands variables -->
```

**Build step:**
```bash
# scripts/build_docs.sh
envsubst < Claude.template.md > Claude.md
```

**Benefits:**
- ✅ True single source of truth
- ✅ Variables expanded automatically
- ❌ More complex build process
- ❌ Two versions of files (template + generated)

---

### **Solution 5: Session End Checklist Enhancement**

**Update:** `.claude/session_end.md`

**Add consistency check section:**
```markdown
### Step 7: Documentation Consistency Check

If you changed any of these values, update ALL locations:

**Database Table Count:**
- [ ] Claude.md (search for "table")
- [ ] PROJECT_STATUS.md (search for "table")
- [ ] DOCUMENTATION_STRUCTURE.md
- [ ] PROJECT_STRUCTURE.md
- [ ] docs/Level_1_AISET_Development/DATABASE_SCHEMA.md

**Requirements Count/Location:**
- [ ] Claude.md
- [ ] PROJECT_STATUS.md
- [ ] DOCUMENTATION_LEVELS.md
- [ ] DOCUMENTATION_STRUCTURE.md

**DO-178C Compliance %:**
- [ ] Claude.md (2 locations)
- [ ] PROJECT_STATUS.md
- [ ] docs/Level_1_AISET_Development/DO178C_COMPLIANCE.md

**Or run:** `./scripts/check_documentation_consistency.sh`
```

**Benefits:**
- ✅ Simple, no coding required
- ✅ Catches issues at session end
- ❌ Manual, can be forgotten
- ❌ Relies on discipline

---

## Recommended Approach (Hybrid)

**Implement a combination of solutions:**

### Phase 1: Immediate (This Session)

1. ✅ **Create PROJECT_METRICS.md** - Single source of truth for all metrics
2. ✅ **Update session_end.md** - Add consistency check section
3. ✅ **Document the problem** - This file

### Phase 2: Short-term (Next Week)

4. **Create consistency check script** - `scripts/check_documentation_consistency.sh`
5. **Add pre-commit hook** - Run consistency check before commits
6. **Update DOCUMENTATION_STRUCTURE.md** - Document SSOT principle

### Phase 3: Long-term (Next Month)

7. **Automate metrics extraction** - Python scripts to count tables, requirements from source
8. **GitHub Actions** - Automated consistency checks on PRs
9. **Consider template system** - For frequently updated values

---

## Implementation Priority

| Solution | Effort | Impact | Priority | Status |
|----------|--------|--------|----------|--------|
| PROJECT_METRICS.md (SSOT) | Low | High | 🔴 **CRITICAL** | ⏳ To Do |
| Session End Checklist | Low | Medium | 🟡 High | ⏳ To Do |
| Consistency Check Script | Medium | High | 🟡 High | ⏳ To Do |
| Metrics from Code | High | Medium | 🟢 Medium | Future |
| Template Variables | High | Medium | 🟢 Low | Future |

---

## Metrics That Should Have SSOT

**Critical Metrics (frequently change):**
1. Database table count
2. Requirements count (total + by category)
3. DO-178C compliance percentages
4. File counts (source files, docs, LOC)
5. Version numbers (SRS version, tool version)

**Design Document Locations:**
6. HLD location and size
7. LLD location and size
8. Traceability matrix location

**File References:**
9. Official requirements document (SRS location)
10. Roleplay working file (ROLEPLAY_REQUIREMENTS.md)

---

## Best Practices Going Forward

### When You Change a Metric:

1. **Check PROJECT_METRICS.md first** - Is this metric tracked?
2. **Update PROJECT_METRICS.md** - Change the canonical value
3. **Run consistency check** - `./scripts/check_documentation_consistency.sh`
4. **Update referencing files** - Or let automation do it
5. **Commit together** - Metric change + all doc updates in one commit

### When You Add a New File:

1. **Avoid duplicating metrics** - Reference PROJECT_METRICS.md instead
2. **If you must duplicate** - Add to consistency check script

### Session End:

1. **Review PROJECT_METRICS.md** - Did anything change?
2. **Run consistency check** - Before final commit
3. **Update session_end.md** - If new metrics added

---

## Example: Correct Workflow

**Scenario:** Database changes from 47 → 50 tables

**Old Way (Error-Prone):**
```bash
# Edit schema_v1.sql - add 3 tables
git commit -m "feat: add 3 new tables"
# ❌ Forgot to update documentation!
# Claude.md, PROJECT_STATUS.md, etc. now say "47 tables" (wrong!)
```

**New Way (Systematic):**
```bash
# 1. Edit schema_v1.sql - add 3 tables

# 2. Update SSOT
echo "Updating PROJECT_METRICS.md: 47 → 50 tables"
sed -i 's/Total Tables:** 47/Total Tables:** 50/' PROJECT_METRICS.md

# 3. Run consistency check
./scripts/check_documentation_consistency.sh
# Output: "❌ Claude.md still references 47 tables"

# 4. Fix all inconsistencies
sed -i 's/47 tables/50 tables/g' Claude.md PROJECT_STATUS.md ...

# 5. Re-run check
./scripts/check_documentation_consistency.sh
# Output: "✅ All documentation consistency checks passed!"

# 6. Commit everything together
git add -A
git commit -m "feat: add 3 new tables + update all documentation

- Added tables: X, Y, Z
- Updated table count: 47 → 50
- Updated: PROJECT_METRICS.md, Claude.md, PROJECT_STATUS.md, ...
- Consistency check: PASSED"
```

---

## Decision: What to Implement Now?

**Recommended immediate actions:**

### 1. Create PROJECT_METRICS.md ✅

Single source of truth for all key metrics. Simple, effective, low effort.

### 2. Create check script ✅

Automated detection before it becomes a problem.

### 3. Update session_end.md ✅

Remind to check consistency at end of each session.

**These three give 80% of the benefit with 20% of the effort.**

---

## Questions for User

1. **Which solution(s) do you want to implement?**
   - SSOT file (PROJECT_METRICS.md)? ✅ Recommended
   - Consistency check script? ✅ Recommended
   - Session end checklist? ✅ Recommended
   - Code generation? (more complex)
   - Template system? (most complex)

2. **How automated do you want this?**
   - Manual checks (simple, relies on discipline)
   - Pre-commit hooks (automated, catches before commit)
   - GitHub Actions (automated, catches in PR)

3. **What other metrics should be tracked?**
   - Version numbers?
   - Compliance percentages?
   - File counts?
   - Documentation sizes?

---

**Next Step:** Implement chosen solution(s) based on user feedback.
