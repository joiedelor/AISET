# Design Reviews - Instructions and Tracking

**Purpose:** Document design reviews for DO-178C compliance (Section 5.3, 5.4)
**Reviewer:** You (solo developer)
**Approach:** File-based review tracking (no development database needed)

---

## What Are Design Reviews?

Design reviews are a critical DO-178C verification activity where you:
1. **Check completeness** - Does the design address all requirements?
2. **Check correctness** - Is the design technically sound?
3. **Check consistency** - Does LLD match HLD? Does HLD match requirements?
4. **Check verifiability** - Can the design be tested?
5. **Document results** - Record findings for audit trail

**DO-178C requires reviews of:**
- High-Level Design (HLD)
- Low-Level Design (LLD)
- Source Code (later)
- Test procedures (later)

---

## How to Conduct a Review (Solo Developer)

### Step 1: Choose Which Document to Review

Available review checklists:
- `HLD_Review_Checklist.md` - Review HLD_High_Level_Design.md
- `LLD_Database_Review_Checklist.md` - Review LLD_Database_Schema_Design.md

### Step 2: Make a Copy with Date

```bash
cd /home/joiedelor/aiset/03_DESIGN/Design_Reviews

# For HLD review
cp HLD_Review_Checklist.md HLD_Review_2025-11-16_Your_Name.md

# For LLD review
cp LLD_Database_Review_Checklist.md LLD_Database_Review_2025-11-16_Your_Name.md
```

**Why copy?**
- Keeps template clean for next review
- Creates dated review record
- Git tracks when review was done

### Step 3: Fill Out the Checklist

Open your copy and fill in:

```markdown
**Reviewer:** Your Name Here
**Review Date:** 2025-11-16
```

Work through each section:
- Mark `[x]` for Yes, `[ ]` for No
- Fill in counts (e.g., `__/44` → `44/44`)
- Add comments in "Notes" fields
- Document any issues found

**Tips:**
- **Be thorough** - Check every item
- **Be honest** - Don't skip issues you find
- **Be specific** - "Missing validation" is better than "bad design"
- **Take your time** - A good review takes 2-4 hours

### Step 4: Make a Decision

At the end, choose one of:

- ✅ **APPROVED** - Design is good, no changes needed
- ✅ **APPROVED WITH COMMENTS** - Good, but I noted some improvements
- ⚠️ **CONDITIONAL APPROVAL** - Good after I fix specific items
- ❌ **REJECTED** - Needs major rework

### Step 5: Sign the Review

```markdown
**Reviewer Name:** Your Name
**Signature:** Your Name (electronic signature acceptable)
**Date:** 2025-11-16
```

For DO-178C, your name and date are sufficient for solo development.

### Step 6: Commit to Git

```bash
git add 03_DESIGN/Design_Reviews/HLD_Review_2025-11-16_Your_Name.md
git commit -m "review: HLD v1.0.0 design review - APPROVED

Completed design review of HLD v1.0.0 per DO-178C Section 5.3.

Review Results:
- All 167 requirements addressed in HLD
- Architecture clear and complete
- Technology choices justified
- Safety and security addressed
- Traceability verified

Decision: APPROVED

Reviewer: Your Name
Date: 2025-11-16"
```

**Why commit?** Git provides:
- Audit trail (who, when, what)
- Version control (can see review history)
- DO-178C compliance (reviewers can be identified)

---

## Review Checklist Templates

### HLD_Review_Checklist.md

**What it reviews:** HLD_High_Level_Design.md
**Sections:**
1. Completeness Check
2. Architecture Review
3. Design Quality
4. Safety and Security
5. Traceability
6. Issues and Action Items
7. Review Decision

**Estimated time:** 2-3 hours

---

### LLD_Database_Review_Checklist.md

**What it reviews:** LLD_Database_Schema_Design.md
**Sections:**
1. Completeness Check
2. Schema Design Review (hybrid IDs, audit trail)
3. Referential Integrity (foreign keys, constraints)
4. Performance Optimization (indexes, data types)
5. Special Features (locking, RBAC, merge)
6. Traceability Verification
7. Implementability
8. Issues and Action Items
9. Review Decision

**Estimated time:** 3-4 hours (47 tables to check!)

---

## Review Status Tracking

Update `Review_Status_Tracker.md` after each review:

| Document | Version | Reviewer | Review Date | Result | File |
|----------|---------|----------|-------------|--------|------|
| HLD | 1.0.0 | Your Name | 2025-11-16 | APPROVED | HLD_Review_2025-11-16_Your_Name.md |
| LLD Database | 1.0.0 | | | | |

---

## DO-178C Compliance Notes

### Why File-Based Reviews Work

DO-178C doesn't mandate a *database* for tracking reviews. It requires:

✅ **Evidence reviews were performed** - Your filled-out checklist
✅ **Identification of reviewer** - Your name and signature
✅ **Date of review** - Documented in checklist and Git
✅ **Review findings** - Issues and action items documented
✅ **Review decision** - Approved, conditional, or rejected
✅ **Retention** - Git provides permanent record

**File-based reviews satisfy all of these!**

### What Auditors Need to See

When certification auditors review your work, they'll look for:

1. **Review checklists** (these files)
2. **Completed checklists** (your filled-out copies)
3. **Git history** (showing when reviews occurred)
4. **Traceability** (checklist → document being reviewed)
5. **Action items** (and evidence they were closed)

**You'll have all of this in Git.**

---

## Best Practices

### For Solo Development

**DO:**
- ✅ Fill out checklists honestly
- ✅ Take breaks (don't rush)
- ✅ Check a few requirements deeply (not just skim all)
- ✅ Document issues you find
- ✅ Fix critical issues before approval
- ✅ Commit reviews to Git
- ✅ Date your review files

**DON'T:**
- ❌ Skip sections ("I'll do it later")
- ❌ Approve without reading
- ❌ Ignore issues you find
- ❌ Lose review files
- ❌ Forget to commit to Git

### When to Re-Review

You need a new review if:
- Document version changes significantly
- Critical requirements added/changed
- Major design changes made
- Previous review found major issues (re-review after fixes)

---

## Example: Complete Review Workflow

```bash
# 1. Start review
cd /home/joiedelor/aiset/03_DESIGN/Design_Reviews
cp HLD_Review_Checklist.md HLD_Review_2025-11-16_YourName.md

# 2. Fill out checklist (use your text editor)
nano HLD_Review_2025-11-16_YourName.md

# 3. Review the actual HLD document
less ../HLD_High_Level_Design.md

# 4. Go back and forth, filling checklist

# 5. Found an issue? Document it in checklist "Issues" section

# 6. Fix issue in HLD (if critical)
nano ../HLD_High_Level_Design.md

# 7. Complete checklist, make decision

# 8. Commit both files
git add HLD_Review_2025-11-16_YourName.md
git add ../HLD_High_Level_Design.md  # if you fixed issues
git commit -m "review: HLD v1.0.0 design review - APPROVED

Completed comprehensive design review of HLD v1.0.0.
All 167 requirements verified as addressed.
Architecture and design quality verified.

Issues found: 2 minor (documented in review)
Decision: APPROVED WITH COMMENTS

Reviewer: Your Name
Date: 2025-11-16"

# 9. Update review tracker
nano Review_Status_Tracker.md
git add Review_Status_Tracker.md
git commit -m "docs: update review status tracker"
```

---

## Tips for Effective Reviews

### Focus Areas

**For HLD:**
- Architecture makes sense?
- All requirements addressed?
- Technology choices justified?
- Scalability considered?

**For LLD:**
- All tables needed?
- Columns have correct types?
- Foreign keys make sense?
- Indexes for performance?
- Can I code this directly?

### Common Issues to Look For

- Missing requirements coverage
- Ambiguous specifications
- Inconsistencies between documents
- Missing constraints or validation
- Performance concerns
- Security gaps
- Unclear traceability

### When Stuck

If you're unsure about something during review:
- Mark it as an issue
- Research the topic
- Ask me (Claude) for clarification
- Document your uncertainty
- Better to flag it than miss it!

---

## Files in This Directory

```
Design_Reviews/
├── README.md                              # This file
├── HLD_Review_Checklist.md               # Template for HLD reviews
├── LLD_Database_Review_Checklist.md      # Template for LLD reviews
├── Review_Status_Tracker.md              # Track review completion
└── [Completed reviews...]                 # Your completed reviews
    ├── HLD_Review_2025-11-16_YourName.md
    ├── LLD_Database_Review_2025-11-16_YourName.md
    └── etc.
```

---

## Questions?

**Q: How long should a review take?**
A: HLD: 2-3 hours, LLD: 3-4 hours. Don't rush!

**Q: Can I review my own design?**
A: Yes, for solo development. DO-178C prefers independent reviewers, but solo is acceptable for DAL D. Document that you're solo.

**Q: What if I find a critical issue?**
A: Mark as CONDITIONAL or REJECTED, fix the issue, update the design doc, re-review.

**Q: Do I need to review every table in LLD?**
A: Check structure of a representative sample (10-15 tables). Check all critical tables (configuration_items, ci_locks, requirements).

**Q: How do I know if my review is good enough?**
A: If an auditor could read your checklist and understand what you reviewed, what you found, and why you approved/rejected, it's good enough.

---

**Last Updated:** 2025-11-16
**For:** Solo development (you can manage yourself)
**DO-178C Compliance:** Satisfies Sections 5.3, 5.4 review requirements
