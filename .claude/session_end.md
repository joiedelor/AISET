# Session End Procedure
## Mandatory Steps Before Ending Any Session

**⚠️ CRITICAL:** Claude Code MUST execute these steps before running out of tokens or ending a session.

---

## ✅ Session End Checklist

### 1. Update Claude.md
**File:** `/home/joiedelor/aiset/Claude.md`

**Update sections:**
- [ ] Last Updated timestamp
- [ ] Session Summary with completed items
- [ ] System Status (if changed)
- [ ] Database table count (if changed)
- [ ] DO-178C Compliance percentage (if changed)
- [ ] Next Immediate Tasks

**Template for session summary:**
```markdown
### 🎯 SESSION SUMMARY (YYYY-MM-DD HH:MM-HH:MM UTC)

**COMPLETED ✅**
1. ✅ [Task 1]
2. ✅ [Task 2]
...
```

---

### 2. Update PROJECT_STATUS.md
**File:** `/home/joiedelor/aiset/PROJECT_STATUS.md`

**Update if any of these changed:**
- [ ] Last Updated timestamp
- [ ] Version number (if major changes)
- [ ] Current Compliance Level
- [ ] Code metrics (tables, files, lines)
- [ ] DO-178C Compliance Metrics
- [ ] Remediation Plan progress
- [ ] New Documentation Created section

---

### 3. Verify Todo List
**Check TodoWrite status:**
- [ ] All todos either completed or with clear status
- [ ] No todos left as "in_progress" without reason
- [ ] Document any blocked items

---

### 4. Check for New Files
```bash
git status --short
```
- [ ] All new files intentional
- [ ] No temporary files (*.tmp, *.bak, etc.)
- [ ] No sensitive data (.env files excluded)

---

### 5. Create Git Commit

**Commit message format:**
```
<type>: <short description>

<detailed description>

Changes:
- <change 1>
- <change 2>

DO-178C Compliance:
- <compliance info if relevant>

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

**Example:**
```bash
git add -A
git commit -m "docs: restructure documentation and remove duplicates

- Delete duplicate files (SESSION_RESUME.md, docs/DO178C_*, docs/SDP_*, docs/Tool_*)
- Create DOCUMENTATION_STRUCTURE.md as single source of truth
- Create GAP_ANALYSIS.md identifying 14 gaps
- Update Claude.md and PROJECT_STATUS.md

Documentation Structure:
- Defined clear file ownership and update responsibilities
- Identified which files to keep in docs/ vs 01_PLANNING/
- Eliminated 5 duplicate files

DO-178C Compliance:
- Gap analysis complete
- Structure clarified for certification readiness

Co-Authored-By: Claude <noreply@anthropic.com>
"
```

---

### 6. Provide Push Command
**Generate command for user:**
```bash
git push origin main
```

**Include authentication reminder:**
```
To push to GitHub, run:
  git push origin main

If authentication required:
  git push https://<your-token>@github.com/joiedelor/AISET.git main
```

---

### 7. Create Session Summary for User

**Provide clear summary:**
```markdown
## ✅ Session Complete

**Duration:** [start time] - [end time]
**Files Modified:** X files
**Lines Changed:** +X / -X

### Completed:
1. [Task 1]
2. [Task 2]

### Created/Updated:
- [File 1]
- [File 2]

### Commit:
- Commit hash: [hash]
- Files staged: X
- Ready to push: Yes

### Next Session:
To resume, say: "Continue AISET development"

Priority tasks:
1. [Next priority 1]
2. [Next priority 2]
```

---

## 🤖 Automated Checks (For Claude)

Before ending session, verify:

### Critical Files
```python
files_to_check = [
    "Claude.md",           # MUST be updated every session
    "PROJECT_STATUS.md",   # Update if status changed
]
```

### Git Status
```bash
# Ensure no unstaged critical changes
git diff --name-only Claude.md PROJECT_STATUS.md
```

### Documentation Consistency
- Claude.md "Last Updated" matches current session end time
- PROJECT_STATUS.md has today's date if modified
- No .Zone.Identifier files
- No duplicate files in docs/ and 01_PLANNING/

---

## 📋 Quick Verification Script

```bash
#!/bin/bash
# Run this before ending session

echo "=== SESSION END VERIFICATION ==="

echo -e "\n1. Checking Claude.md updated..."
if grep -q "$(date +%Y-%m-%d)" Claude.md; then
    echo "✅ Claude.md has today's date"
else
    echo "❌ WARNING: Claude.md may not be updated"
fi

echo -e "\n2. Checking for uncommitted changes..."
git status --short

echo -e "\n3. Checking for duplicate files..."
duplicates=$(find docs/ -name "DO178C_Project_Structure.md" -o -name "SDP_Software_Development_Plan.md" -o -name "DO178C_Daily_Workflow_Guide.md" -o -name "Tool_Qualification_Plan_DO330.md" | wc -l)
if [ "$duplicates" -eq 0 ]; then
    echo "✅ No duplicate files found"
else
    echo "❌ WARNING: $duplicates duplicate files found"
fi

echo -e "\n4. Checking for Zone.Identifier files..."
zone_files=$(find . -name "*.Zone.Identifier" | wc -l)
if [ "$zone_files" -eq 0 ]; then
    echo "✅ No Zone.Identifier files"
else
    echo "❌ WARNING: $zone_files Zone.Identifier files found"
fi

echo -e "\n=== END VERIFICATION ==="
```

---

## 🚫 Common Mistakes to Avoid

### ❌ DON'T
- End session without updating Claude.md
- Leave todos in "in_progress" state
- Commit without descriptive message
- Push without testing locally first
- Forget to update PROJECT_STATUS.md after major changes
- Leave duplicate files
- Include .env or sensitive files

### ✅ DO
- Update Claude.md EVERY session
- Mark todos as completed or pending
- Write detailed commit messages
- Review changes before committing
- Keep PROJECT_STATUS.md current
- Maintain single source of truth
- Use .gitignore properly

---

## 📝 Session End Template (For Claude)

```markdown
## 🎯 Session End Summary

**Date:** [YYYY-MM-DD]
**Duration:** [HH:MM - HH:MM UTC]
**Status:** Session Complete ✅

### Completed Tasks
1. ✅ [Task 1]
2. ✅ [Task 2]
3. ✅ [Task 3]

### Files Modified
- `Claude.md` - Updated session summary
- `PROJECT_STATUS.md` - Updated compliance metrics
- [Other files]

### Git Status
- Files staged: X
- Commit created: [commit hash]
- Ready to push: Yes

### To Push to GitHub
```bash
git push origin main
```

### Next Session Priorities
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

**Resume command:** "Continue AISET development"

---

**✅ All session end procedures completed**
```

---

## 🔄 Integration with Claude Code

This procedure should be triggered:
1. When token budget is low (<10,000 tokens remaining)
2. When user says "end session" or similar
3. Before final response in any session
4. After completing a major milestone

**Reminder in system prompt:**
```
Before ending any session:
1. Update Claude.md
2. Update PROJECT_STATUS.md if needed
3. Create commit
4. Provide push command
5. Summarize session
```

---

**Last Updated:** 2025-11-14
**Status:** Active Procedure
**Mandatory:** YES - Do not skip
