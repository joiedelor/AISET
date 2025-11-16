# Requirements Reviews - Instructions and Tracking

**Purpose:** Document requirements reviews for DO-178C compliance (Section 5.1)
**Reviewer:** You (solo developer)
**Approach:** File-based review tracking

---

## What Are Requirements Reviews?

Requirements reviews are a critical DO-178C verification activity where you verify that:
1. **Requirements are complete** - All user needs addressed
2. **Requirements are correct** - Technically accurate and feasible
3. **Requirements are consistent** - No conflicts or duplicates
4. **Requirements are verifiable** - Can be tested/reviewed
5. **Requirements are traceable** - Source documented, traced to design
6. **Requirements conform to standards** - DO-178C format and quality

**DO-178C requires reviews of:**
- Software Requirements Specification (SRS) - High-level requirements

---

## How to Conduct SRS Review

### Step 1: Make a Copy with Date

```bash
cd /home/joiedelor/aiset/02_REQUIREMENTS/Requirements_Reviews

# Copy the template
cp SRS_Review_Checklist.md SRS_Review_2025-11-16_Your_Name.md
```

**Why copy?**
- Keeps template clean
- Creates dated review record
- Git tracks when review occurred

### Step 2: Open Side-by-Side in VS Code

```bash
# Open VS Code
code .

# Open both files:
# - Left pane: SRS_Review_2025-11-16_Your_Name.md (your checklist)
# - Right pane: ../SRS_Software_Requirements_Specification.md (SRS being reviewed)
```

### Step 3: Fill Out the Checklist

Work through all 9 sections:

1. **Document Completeness** - Is everything present?
2. **Requirements Quality** - Unambiguous, verifiable, consistent?
3. **Standards Conformance** - DO-178C, ARP4754A compliance?
4. **Traceability** - Source documented, traced to design?
5. **Requirements Attributes** - Priority, rationale appropriate?
6. **Derived Requirements** - Identified and appropriate?
7. **Special Checks** - Safety, security, collaboration features?
8. **Issues and Action Items** - Document problems found
9. **Review Decision** - Approve, conditional, or reject?

**Mark checkboxes:**
```markdown
Before: | Item | Present? | Comments |
        | xxx  | [ ] Yes [ ] No | |

After:  | Item | Present? | Comments |
        | xxx  | [x] Yes [ ] No | Found in Section 1 |
```

**Add comments:**
```markdown
**Notes:**
- All 167 requirements present and numbered correctly
- Found 2 minor ambiguities (documented in Issues section)
- Traceability matrix verified - 100% coverage
```

### Step 4: Make Your Decision

```markdown
[x] **APPROVED WITH COMMENTS** - SRS acceptable, minor improvements suggested

**Comments:**
SRS is well-structured, complete, and meets DO-178C Section 5.1 objectives.
Two minor clarifications needed (Issues #1, #2) but don't block approval.
```

### Step 5: Sign the Review

```markdown
**Reviewer Name:** Your Name
**Signature:** Your Name
**Date:** 2025-11-16
```

### Step 6: Commit to Git

```bash
git add SRS_Review_2025-11-16_Your_Name.md
git commit -m "review: SRS v1.0.0 requirements review - APPROVED WITH COMMENTS

Completed comprehensive requirements review of AISET-SRS-001 v1.0.0
per DO-178C Section 5.1.

Review Results:
- All 167 requirements present and verifiable
- Requirements are unambiguous and consistent
- Traceability to design verified (100% coverage)
- DO-178C Section 5.1 objectives satisfied

Issues Found:
- 2 Minor: Clarifications needed (documented)

Decision: APPROVED WITH COMMENTS

Reviewer: Your Name
Date: 2025-11-16"
```

### Step 7: Update Status Tracker

Edit `Review_Status_Tracker.md` and mark SRS review as complete.

---

## Review Checklist Template

### SRS_Review_Checklist.md

**What it reviews:** SRS_Software_Requirements_Specification.md (AISET-SRS-001)

**Sections:**
1. Document Completeness (structure, requirements count)
2. Requirements Quality (unambiguous, verifiable, consistent)
3. Standards Conformance (DO-178C Section 5.1, ARP4754A)
4. Traceability (source, forward to design)
5. Requirements Attributes (priority, rationale)
6. Derived Requirements
7. Special Checks (safety, security, collaboration)
8. Issues and Action Items
9. Review Decision

**Estimated time:** 3-4 hours (167 requirements to review!)

**Key checks:**
- ✓ All 167 requirements present
- ✓ Requirements use "shall" language
- ✓ Each requirement has verification method
- ✓ No conflicts or duplicates
- ✓ 100% traceability to design
- ✓ Derived requirements identified
- ✓ Safety and security requirements adequate

---

## DO-178C Compliance Notes

### Why File-Based Reviews Work

DO-178C Section 5.1 requires:

✅ **Evidence review was performed** - Your completed checklist
✅ **Reviewer identified** - Your name in checklist
✅ **Review date** - In checklist + Git commit timestamp
✅ **Review findings** - Issues section
✅ **Review decision** - Approved/conditional/rejected
✅ **Retention** - Git provides permanent record

**File-based reviews satisfy all requirements!**

### What Auditors Need to See

1. **Completed review checklist** (your file)
2. **SRS document** (AISET-SRS-001 v1.0.0)
3. **Git commit history** (showing when review occurred)
4. **Traceability** (checklist → SRS version)
5. **Action items closed** (if issues found)

**You'll have all of this in Git.**

---

## Best Practices

### For Solo Development

**DO:**
- ✅ Sample requirements across all subsystems
- ✅ Check for patterns (if one req has issue, check similar ones)
- ✅ Verify critical requirements thoroughly
- ✅ Document all issues found
- ✅ Take breaks (don't rush 3-4 hour review)
- ✅ Commit review to Git
- ✅ Fix critical issues before approval

**DON'T:**
- ❌ Skip sections
- ❌ Approve without sampling requirements
- ❌ Ignore inconsistencies you find
- ❌ Forget to commit to Git

### When to Re-Review

New review needed if:
- SRS version changes significantly
- Requirements added/changed/deleted
- Major issues found and fixed
- Compliance requirements change

---

## Tips for Effective SRS Review

### Focus Areas

**Critical checks:**
- All 167 requirements present and numbered correctly
- Requirements use "shall" (not "should" or "may")
- Each requirement has verification method
- No conflicts or duplicates
- Traceability to design complete (100%)
- Safety requirements adequate (REQ-AI-017, REQ-AI-018, etc.)
- Security requirements adequate (RBAC, authentication, etc.)

**Sample deeply:**
- Don't read all 167 requirements linearly
- Sample 10-15 requirements from each subsystem
- Check ALL critical priority requirements
- Verify derived requirements are appropriate

**Use Ctrl+F to search for:**
- "should" (should be "shall")
- "may" (should be "shall")
- "TBD" (shouldn't exist in released SRS)
- "appropriate" (often ambiguous)
- "reasonable" (often ambiguous)

### Common Issues to Look For

- Ambiguous language ("user-friendly", "fast", "efficient")
- Unverifiable requirements ("shall be intuitive")
- Missing verification methods
- Conflicting requirements
- Duplicate requirements (same thing stated twice)
- Missing derived requirements
- Incomplete traceability
- Wrong priority (critical things marked low)

---

## Files in This Directory

```
Requirements_Reviews/
├── README.md                              # This file
├── SRS_Review_Checklist.md               # Template for SRS reviews
├── Review_Status_Tracker.md              # Track review completion
└── [Completed reviews...]                 # Your completed reviews
    ├── SRS_Review_2025-11-16_YourName.md
    └── SRS_Review_2025-12-01_YourName.md (if SRS updated)
```

---

## Questions?

**Q: How long should SRS review take?**
A: 3-4 hours for 167 requirements. Don't rush!

**Q: Should I check every requirement?**
A: Sample deeply across subsystems. Check ALL critical requirements. Verify patterns.

**Q: Can I review my own requirements?**
A: Yes, for solo development. DO-178C prefers independent review, but solo is acceptable for DAL D.

**Q: What if I find critical issues?**
A: Mark as CONDITIONAL or REJECTED. Fix issues, update SRS, increment version, re-review.

**Q: How do I know if my review is good enough?**
A: If an auditor could read your checklist and understand what you checked, what you found, and why you approved/rejected, it's good enough.

---

**Last Updated:** 2025-11-16
**For:** Solo development
**DO-178C Compliance:** Satisfies Section 5.1 requirements review objectives
