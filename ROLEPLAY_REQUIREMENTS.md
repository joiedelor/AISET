# AISET Tool Requirements Specification

**Document Type:** [Level 4] Specification Roleplay - Working File
**Document Version:** 0.8.0
**Last Updated:** 2025-11-16
**Status:** Draft - Specification Complete
**Note:** This is the working source file. Official SRS is in 02_REQUIREMENTS/SRS_Software_Requirements_Specification.md

## Document Purpose
This document captures all requirements for the AISET (AI Systems Engineering Tool) identified through specification roleplay and analysis.

## Requirements Organization
Requirements are categorized by subsystem:
- **AI**: AI behavior and intelligence requirements
- **FE**: Frontend (React/TypeScript) requirements
- **BE**: Backend (FastAPI/Python) requirements
- **DB**: Database (PostgreSQL) requirements
- **DOC**: Documentation requirements

---

## AI Requirements

### AI Behavior

**REQ-AI-001: Single Question Interaction**
The AI shall ask only ONE question at a time. The AI shall NOT ask multiple questions simultaneously or present multiple tasks at once.

**Priority:** CRITICAL
**Rationale:** Non-technical users can be overwhelmed by multiple questions. Single-question interaction improves user experience and reduces cognitive load.

---

**REQ-AI-002: Simple Language by Default**
The AI shall use simple, non-technical language by default when interacting with users.

**Priority:** HIGH
**Rationale:** Target users might not be systems engineers and might not understand systems engineering terminology.

---

**REQ-AI-003: Technical Document Processing**
The AI shall be able to process and parse pre-written technical specifications when provided by users.

**Priority:** HIGH
**Rationale:** Users may provide already-written specifications, and the AI must handle both conversational and document-based inputs.

---

**REQ-AI-004: Adaptive Communication Style**
The AI shall adapt communication style based on user input (simple conversational OR technical).

**Priority:** MEDIUM
**Rationale:** Support both technical and non-technical user workflows.

---

**REQ-AI-005: Systems Engineer Role**
The AI shall act as a systems engineer facilitator (requirements elicitation, analysis, structuring).

**Priority:** CRITICAL
**Rationale:** Core function of AISET is to support systems engineering workflows.

---

**REQ-AI-006: Database Schema Access**
The AI shall have access to database schema documentation (AI_INSTRUCTION.md).

**Priority:** CRITICAL
**Rationale:** AI must know database structure to correctly store extracted information.

---

**REQ-AI-007: Data Formatting Knowledge**
The AI shall know HOW to write to database (data formatting, structure, validation rules).

**Priority:** CRITICAL
**Rationale:** Ensures data consistency and integrity.

---

**REQ-AI-008: Database Mapping Knowledge**
The AI shall know WHERE to write in database (which tables, which columns for each entity type).

**Priority:** CRITICAL
**Rationale:** Correct data routing is essential for system functionality.

---

**REQ-AI-009: Initial Open-Ended Question**
The AI's FIRST question shall be: "Can you describe the project as precisely as you can? If you want, you can provide me a list of requirements or any design information."

This is followed by a structured project initialization interview (REQ-AI-032).

**Priority:** HIGH
**Rationale:** Provides maximum flexibility for user input (description, requirements list, or design documents). Followed by structured context gathering.

---

### AI Role Definition

**REQ-AI-010: No Design Decisions**
The AI shall NOT make design decisions or engineering choices.

**Priority:** CRITICAL
**Rationale:** The USER is the designer/engineer. AI only provides administrative support.

---

**REQ-AI-011: Task Assignment to User**
The AI shall assign engineering TASKS to the USER (the USER performs the actual engineering work).

**Priority:** CRITICAL
**Rationale:** AI supports workflow but doesn't replace human engineering judgment.

---

**REQ-AI-012: Request Specific Deliverables**
The AI shall request specific deliverables from USER's work (e.g., "define a concept and provide: length, width, height").

**Priority:** HIGH
**Rationale:** Guides user to provide structured, complete information.

---

**REQ-AI-013: Administrative Support Role**
The AI's role is LIMITED to administrative support and data structuring for systems engineering.

**Priority:** CRITICAL
**Rationale:** Clear role definition prevents scope creep and maintains focus.

---

**REQ-AI-014: User as Engineer**
USER performs the actual engineering work; AI manages the workflow and documentation.

**Priority:** CRITICAL
**Rationale:** Human remains responsible for engineering decisions and design quality.

---

### AI Document Processing

**REQ-AI-015: File Upload Acceptance**
The AI shall accept and parse file uploads (docx, txt, pdf, etc.) as responses to assigned tasks.

**Priority:** HIGH
**Rationale:** Users may prefer to provide information in document format rather than chat.

---

**REQ-AI-016: Document Information Extraction**
The AI shall extract structured information from uploaded documents.

**Priority:** HIGH
**Rationale:** Automates data entry and reduces manual work.

---

**REQ-AI-017: Internal Open Questions List**
The AI shall maintain an internal list of open questions/clarifications (not visible to user).

**Priority:** MEDIUM
**Rationale:** Maintains single-question-at-a-time rule while tracking all needed information.

---

**REQ-AI-018: Gap Storage**
The AI shall store identified gaps, inconsistencies, or missing information without immediately asking the user.

**Priority:** MEDIUM
**Rationale:** Allows prioritization of questions and prevents overwhelming user.

---

### AI Design Review

**REQ-AI-019: No Subjective Assessments**
The AI shall NOT make design judgments or subjective assessments (e.g., "that seems too small").

**Priority:** CRITICAL
**Rationale:** Subjective judgments are engineering decisions reserved for human engineers.

---

**REQ-AI-020: Requirements-Based Design Review**
The AI shall facilitate design review by comparing design specifications against requirements.

**Priority:** HIGH
**Rationale:** Core systems engineering practice - objective verification against requirements.

---

**REQ-AI-021: Gap Highlighting**
The AI shall highlight GAPS where design does not address stated requirements.

**Priority:** HIGH
**Rationale:** Ensures traceability and completeness.

---

**REQ-AI-022: Verification Request**
The AI shall request verification/analysis when design claims need substantiation (e.g., "how does this design achieve stability?").

**Priority:** HIGH
**Rationale:** Ensures claims are backed by analysis, not assumptions.

---

**REQ-AI-023: Document Reference Acceptance**
The AI shall accept documents with reference numbers and titles as evidence/verification.

**Priority:** MEDIUM
**Rationale:** Supports formal documentation and traceability requirements.

---

**REQ-AI-024: Reference Storage and Linking**
The AI shall store and link document references to related requirements/design elements.

**Priority:** MEDIUM
**Rationale:** Maintains traceability and enables audit trail.

---

### AI Modification Behavior

**REQ-AI-025: Automatic Content Modification**
The AI shall modify document content automatically WITHOUT asking user permission.

**Priority:** HIGH
**Rationale:** Reduces interaction overhead; user reviews changes in batch rather than approving each one.

---

**REQ-AI-026: Modification Flagging**
When the AI modifies content, the system shall automatically mark the document as "needs review".

**Priority:** HIGH
**Rationale:** User must be aware of AI changes and validate them.

---

**REQ-AI-027: Protected Field Restrictions**
The AI shall NOT modify protected fields:
- "Reviewed by USER" tags
- Database structure
- User approval status
- Other designated protected fields

**Priority:** CRITICAL
**Rationale:** Prevents AI from overriding human decisions or corrupting system integrity.

---

### Session Management

**REQ-AI-028: Session Context Recovery**
The AI shall be able to recover conversation context and resume from where the user left off when returning to a project.

**Priority:** HIGH
**Rationale:** Users need to stop and resume work across multiple sessions. AI must restore full context without losing progress.

---

**REQ-AI-029: Context Restoration on Resume**
When a user returns to a project, AI shall ask ONE question:

**"Would you like a summary of where we left off, or should we continue?"**

- If user chooses summary → AI provides brief summary, then asks what to work on next
- If user chooses continue → AI proceeds with next question from internal open questions list

**Priority:** MEDIUM
**Rationale:** Minimal approach respecting one-question-at-a-time principle. Gives user control over session resumption flow.
**Constraint:** Must comply with REQ-AI-001 (single question only)

---

**REQ-AI-030: Conditional Response Paths**
The AI shall support conditional response flows based on user choices (e.g., "summary" vs "continue").

**Priority:** MEDIUM
**Rationale:** Enables flexible, user-controlled workflows while maintaining simplicity.

---

**REQ-AI-031: Product Development Context Awareness**
The AI shall consult `docs/PROJECT_PLAN.md` to understand:
- Current phase of the AISET product development lifecycle (Phase 1-10)
- Appropriate activities for the current phase
- Expected outputs and deliverables
- Context for requirements and design decisions

**Priority:** MEDIUM
**Rationale:** Ensures AI understands the broader product development context and can guide users appropriately based on the current development phase.
**Reference:** docs/PROJECT_PLAN.md - 10-phase ARP4754A-aligned development process

---

### Project Initialization

**REQ-AI-032: Project Initialization Interview**
The AI shall conduct a structured project initialization interview when a new project is created.

The AI shall gather critical project context before proceeding with detailed requirements elicitation.

**Priority:** CRITICAL
**Rationale:** Project context (safety criticality, regulatory requirements, development rigor level) determines which standards apply, what processes must be followed, and what documentation is required. This information is foundational for all subsequent work.

---

**REQ-AI-033: Safety & Regulatory Context Determination**
The AI shall determine the following during project initialization:
1. Whether the product is safety-critical (can failures cause harm to people, property, or environment?)
2. Worst-case failure scenario
3. Applicable safety standards (DO-178C, ISO 26262, IEC 62304, IEC 61508, etc.)
4. Applicable regulatory requirements (e.g., FAA, EASA, FDA, MDR, CE marking, FCC)
5. Whether certification/approval is required before market release

**Priority:** CRITICAL
**Rationale:** Safety criticality and regulatory context are the PRIMARY drivers of development process rigor, documentation requirements, and verification/validation activities.

---

**REQ-AI-034: Development Assurance Level Determination**
The AI shall determine the required Development Assurance Level (DAL) or Safety Integrity Level (SIL) based on failure severity:
- Catastrophic
- Hazardous
- Major
- Minor
- No Effect

The DAL/SIL drives process rigor, independence requirements, and documentation depth.

**Priority:** CRITICAL
**Rationale:** DAL/SIL is the single most important factor determining what processes, reviews, and documentation are required for the project.

---

**REQ-AI-035: Product Scope & Boundaries Definition**
The AI shall identify during project initialization:
1. What problem the product solves
2. Who the users/customers are and their pain points
3. What value the solution provides
4. Product boundaries (what's included vs. excluded)
5. Interfaces to external systems
6. Where the development responsibility ends

**Priority:** HIGH
**Rationale:** Clear scope definition prevents scope creep and ensures all stakeholders have shared understanding of what is being developed.

---

**REQ-AI-036: Prioritized Questioning Workflow**
The AI shall follow this priority order for project initialization questions:

**FOUNDATION (Ask FIRST):**
1. Safety criticality & regulatory requirements → Determines process rigor
2. Product scope & boundaries → Defines what is being built
3. Development assurance level (DAL/SIL) → Drives standards, reviews, independence

**PLANNING (Ask SECOND):**
4. Architecture & make-vs-buy decisions → Structures work breakdown
5. Resources & timeline → Feasibility assessment
6. Requirements baseline → Defines "done"

**EXECUTION DETAILS (Ask THIRD, as needed):**
7. Verification strategy → How to prove it works
8. Supply chain approach → How to manage externals
9. Lifecycle expectations → Support planning
10. Risk mitigation → Contingencies

The AI shall still follow one-question-at-a-time principle (REQ-AI-001) throughout.

**Priority:** HIGH
**Rationale:** Foundation questions must be answered before Planning questions, as they determine which processes and standards apply. Asking in wrong order leads to rework.

---

**REQ-AI-037: Context-Aware Process Selection**
The AI shall adapt the development process, standards, and templates based on project initialization answers:
- Select appropriate standards (DO-178C, ISO 26262, etc.) based on domain and safety level
- Select appropriate rigor level based on DAL/SIL
- Consult the relevant sections of PROJECT_PLAN.md (REQ-AI-031) based on project type
- Configure documentation templates based on regulatory requirements
- Adjust verification/validation requirements based on criticality

**Priority:** HIGH
**Rationale:** One-size-fits-all processes don't work. A DAL A aerospace product requires very different processes than a non-safety-critical consumer product. The AI must tailor its guidance to the specific project context.

---

### Product Structure & Configuration Item Management

**REQ-AI-038: Product Structure Extraction**
The AI shall extract product structure information from user inputs and documents:
- Identify assemblies, sub-assemblies, components, and parts from descriptions
- Parse Bill of Materials (BOM) from uploaded documents (Excel, PDF, CAD exports)
- Structure information into hierarchical product breakdown
- Identify parent-child relationships
- Suggest item categorization (mechanical, electrical, software, etc.)
- Extract quantities and reference designators

**Priority:** HIGH
**Rationale:** Manual entry of product structure is time-consuming and error-prone. AI automation accelerates project setup and reduces errors.

---

**REQ-AI-039: Item Data Extraction**
The AI shall extract item/part information from engineering documents:
- Part numbers (internal, manufacturer, supplier) from drawings and specifications
- Part descriptions and specifications
- Supplier information from procurement documents
- Material specifications and properties
- BOM data from spreadsheets or formatted documents
- Serial numbers and lot information from manufacturing records
- Map extracted data to database schema

**Priority:** HIGH
**Rationale:** Engineering documents contain structured item data that can be automatically extracted, reducing manual data entry and improving accuracy.

---

**REQ-AI-040: Configuration Item Classification and Suggestion**
The AI shall automatically classify Configuration Items (CIs) and suggest metadata:
- Determine CI type (software, hardware, firmware, mechanical, documentation, data, tools, models)
- Suggest appropriate Configuration Control Level (1-5) based on criticality and context
- Recommend baseline status based on lifecycle phase
- Identify applicable standards for the CI type
- Suggest verification requirements based on DAL/SIL and CI type
- Flag safety-critical or security-critical CIs based on requirements traceability

**Priority:** MEDIUM
**Rationale:** Proper CI classification is essential for compliance but requires expertise. AI suggestions help users apply correct configuration management rigor.
**Reference:** docs/Level_2_User_Framework/CONFIGURATION_ITEM_MANAGEMENT.md

---

### Collaborative & Distributed Work

**REQ-AI-041: AI-Assisted Merge Conflict Resolution**
The AI shall assist in resolving merge conflicts when integrating data from multiple AISET instances:
- Analyze conflicting CI data from different sources
- Identify conflict type (ID collision, duplicate item, conflicting data, broken reference)
- Suggest resolution based on:
  - Data recency (which is newer?)
  - Data completeness (which has more information?)
  - Control level (higher control level takes precedence)
  - Certification status (certified version takes precedence)
  - Baseline status (released > under review > draft)
- Provide confidence level for each suggestion
- Explain rationale for suggested resolution
- Allow human to override AI suggestion
- Learn from human override decisions to improve future suggestions

**Priority:** HIGH
**Rationale:** Merge conflicts are complex and time-consuming to resolve manually. AI can analyze data and suggest resolutions, but human must approve for safety-critical items. Semi-automatic approach balances automation with human oversight.
**User Answer:** Q4 - Semi-automatic merge preferred

---

**REQ-AI-042: Duplicate Configuration Item Detection**
The AI shall detect potential duplicate CIs when merging data or during data entry:
- Identify same physical item with different CI IDs (e.g., same part number, different CI ID)
- Compare across multiple attributes:
  - Part numbers (internal, MPN, SPN)
  - Name and description (fuzzy matching)
  - Physical properties (dimensions, weight, material)
  - Supplier information
- Calculate similarity score (0-100%)
- Flag high-confidence duplicates (>90% similarity) for review
- Suggest which CI to keep as master and which to deprecate
- Propose merging traceability links from both CIs to master

**Priority:** HIGH
**Rationale:** Duplicate CIs cause confusion, procurement errors, and traceability gaps. AI can detect duplicates that humans miss, especially when names/IDs differ but items are identical.

---

**REQ-AI-043: Change Impact Notification Intelligence**
The AI shall intelligently determine who should be notified when a CI changes:
- Identify users who should be notified based on:
  - Direct assignment (owner, responsible party)
  - Traceability (users responsible for linked requirements/tests)
  - Parent/child relationships (users responsible for parent assembly or child components)
  - Interface relationships (users responsible for interfacing CIs)
  - Subscriptions (users watching this CI)
  - Safety criticality (safety reviewers for safety-critical CIs)
- Prioritize notifications (critical, high, medium, low)
- Suppress redundant notifications (don't notify same user multiple times)
- Batch notifications for multiple changes
- Suggest who should review the change based on change type

**Priority:** MEDIUM
**Rationale:** In large distributed teams, manual notification is impractical. AI can intelligently determine stakeholders affected by changes and route notifications appropriately.

---

**REQ-AI-044: Access Control and Permission Recommendations**
The AI shall recommend access control settings for CIs:
- Suggest appropriate access level based on:
  - CI control level (Level 1 = restricted access)
  - Safety/security classification
  - Lifecycle phase (released items = read-only for most users)
  - Team assignments (only assigned team can edit)
- Recommend user roles based on responsibilities:
  - Identify who should be owner, reviewer, approver
  - Suggest read-only access for external stakeholders (suppliers, customers, authorities)
- Flag access control violations:
  - Junior engineer assigned to Level 1 CI (requires senior engineer)
  - External user has edit access to proprietary CI (security risk)
- Recommend permission changes when CI status changes (e.g., when CI is released, convert all users to read-only except Change Control Board)

**Priority:** MEDIUM
**Rationale:** Access control is complex in distributed environments with multiple stakeholders. AI can suggest appropriate permissions based on best practices and prevent security violations.

---

## Frontend Requirements

### Document Management Interface

**REQ-FE-002: Document List Display**
The frontend shall display a list of project "documents" (aggregated from database).

**Priority:** HIGH
**Rationale:** Primary interface for user to access and manage project artifacts.

---

**REQ-FE-003: Review Status Display**
The frontend shall show review status for each document (reviewed/needs review/modified).

**Priority:** HIGH
**Rationale:** User needs to know which documents require attention.

---

**REQ-FE-004: Modification Indicators**
Documents modified by AISET-AI shall be visually indicated (e.g., flag, color, badge).

**Priority:** MEDIUM
**Rationale:** Quick visual identification of changed documents.

---

**REQ-FE-005: Document Review Capability**
User shall be able to click on a document to open and review it.

**Priority:** HIGH
**Rationale:** Access to document content for review and approval.

---

**REQ-FE-006: Document Type Display**
The frontend shall display document types including:
- Project Specification
- Component Specifications (e.g., leg specification)
- Design Documents (e.g., table design)
- Design Verification Reports
- Traceability Matrix
- Test Plans
- Other certification artifacts

**Priority:** HIGH
**Rationale:** Support full systems engineering documentation suite.

---

**REQ-FE-007: Project Status Dashboard**
Frontend shall display overall project status to help user understand "where am I in this project":
- Current phase indicator (requirements gathering, design, verification, etc.)
- Progress summary
- Open questions count
- Documents needing review count
- Recent activity
- Suggested next steps

**Priority:** HIGH
**Rationale:** User needs quick orientation when returning to a project. Supports session resumption (REQ-AI-028, REQ-AI-029).

---

**REQ-FE-008: Dual Interface Layout**
Frontend shall have TWO distinct fields:

1. **AI Proposal Field** - Displays AI's suggested next step (passive, informational, can be ignored by user)
2. **Dialogue Field** - Active conversation/chat between USER and AI (one-question-at-a-time interaction)

**Priority:** HIGH
**Rationale:** Separates guidance/suggestions from active conversation. Allows AI to provide next-step recommendations without violating one-question-at-a-time rule (REQ-AI-001).

**Layout concept:**
```
┌─────────────────────────────────────┐
│ 📋 Next Step Suggestion:            │
│ "Define table top specifications"   │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ 💬 Conversation                     │
│ AISET-AI: [question/response]       │
│ USER: [input field]                 │
└─────────────────────────────────────┘
```

---

**REQ-FE-009: Project Context Display**
Frontend shall display project context summary on the project dashboard including:
- Safety criticality level (safety-critical / non-safety-critical)
- Development Assurance Level (DAL) or Safety Integrity Level (SIL)
- Applicable standards (DO-178C, ISO 26262, IEC 62304, etc.)
- Regulatory requirements (FAA, EASA, FDA, etc.)
- Certification requirements (if applicable)
- Product domain/industry

This information shall be visible from the project dashboard (REQ-FE-007).

**Priority:** HIGH
**Rationale:** Project context drives all development activities. Users and reviewers need immediate visibility into what standards and processes apply to the project. Critical for orientation and compliance verification.

---

### Product Structure & Configuration Item Management

**REQ-FE-010: Product Structure Visualization**
Frontend shall display product structure as an interactive hierarchical tree:
- Expandable/collapsible tree view of product breakdown (system → subsystem → assembly → component → part)
- Visual indication of item type (software, hardware, mechanical, documentation, etc.)
- Display key item information in tree (part number, name, revision, status)
- Click item to view detailed information
- Search and filter capabilities across product structure
- Visual indication of CI criticality (DAL/SIL, safety-critical flagging)
- Multi-level expand/collapse controls
- Export product structure to common formats (CSV, PDF)

**Priority:** HIGH
**Rationale:** Product structure is fundamental to systems engineering. Visual representation helps users understand system architecture and navigate complex hierarchies.

---

**REQ-FE-011: Bill of Materials (BOM) Editor**
Frontend shall provide BOM editing and viewing interface:
- Add/remove parts from assembly
- Specify quantities per assembly
- Specify reference designators (for electrical items) and find numbers (for mechanical drawings)
- View multi-level BOM (indented BOM showing all levels)
- View single-level BOM (only direct children)
- BOM comparison between versions (what changed?)
- Where-used view (which assemblies use this part?)
- Export BOM to common formats (CSV, Excel, PDF)
- BOM effectivity management (which BOM applies to which product serial numbers)

**Priority:** HIGH
**Rationale:** BOM is critical for manufacturing, procurement, and configuration management. Users need comprehensive BOM tools for effective product development.

---

**REQ-FE-012: Item Management Interface**
Frontend shall provide comprehensive item/part management features:
- Create new items with automatic part number assignment (based on project numbering scheme)
- Edit item master data (name, description, type, revision, etc.)
- View and edit supplier information
- View where-used information (which assemblies contain this item)
- View requirements traceability for item (which requirements does this item satisfy?)
- View change history for item
- Manage item lifecycle status (concept, development, production, obsolete)
- Manage alternate/substitute parts
- Track serial numbers and lot numbers (for serialized/lot-tracked items)

**Priority:** HIGH
**Rationale:** Item master data management is essential for configuration control, procurement, and manufacturing. Comprehensive interface reduces errors and improves efficiency.

---

**REQ-FE-013: Configuration Item (CI) Table View**
Frontend shall provide comprehensive Configuration Item table/list view with all CI fields:
- Tabular view of all CIs with sortable/filterable columns
- Display all CI metadata fields (34+ fields per CONFIGURATION_ITEM_MANAGEMENT.md)
- Grouping by CI type, status, owner, DAL, lifecycle phase
- Bulk operations (change status, assign owner, update baseline)
- Custom column selection (show/hide fields based on user preference)
- Export CI table to Excel/CSV
- CI status dashboard (counts by status, verification status, certification status)
- Quick filters for common views (my CIs, pending approval, needs verification, safety-critical CIs)

**Priority:** MEDIUM
**Rationale:** CI table is the primary interface for configuration management. Users need comprehensive view and manipulation capabilities for effective CM.
**Reference:** docs/Level_2_User_Framework/CONFIGURATION_ITEM_MANAGEMENT.md

---

### Collaborative & Distributed Work

**REQ-FE-014: CI Check-Out/Check-In Interface**
Frontend shall provide check-out/check-in workflow for editing CIs:
- Visual indication of CI lock status:
  - 🔓 Unlocked (available for editing)
  - 🔒 Locked by me (I'm editing)
  - 🔒 Locked by [User Name] (someone else editing)
- "Check Out" button to lock CI for editing (pessimistic locking)
- "Check In" button to save changes and release lock
- "Cancel Check-Out" to release lock without saving
- Automatic lock timeout (configurable, e.g., 2 hours)
- Lock override capability for administrators (with justification required)
- Notification when trying to edit locked CI: "CI-SW-001 is being edited by John Smith since 14:30"
- "Request Edit Access" button to notify current lock holder

**Priority:** HIGH
**Rationale:** Prevents simultaneous editing conflicts. PLM-style check-out/check-in is industry standard for configuration management.
**User Answer:** Q1C - Concurrent access is priority

---

**REQ-FE-015: Merge Review Interface**
Frontend shall provide comprehensive merge review and approval interface:
- Merge summary dashboard:
  - Total items to merge
  - Automatic merges (no conflicts): count
  - Conflicts requiring resolution: count
  - Duplicates detected: count
  - Broken references: count
- Three-panel merge comparison view:
  - Left panel: Source data (from external AISET instance)
  - Center panel: Conflicts/differences highlighted
  - Right panel: Target data (current AISET instance) + proposed resolution
- Conflict resolution controls:
  - "Keep Source" button
  - "Keep Target" button
  - "Keep Both" button (creates two separate CIs)
  - "Merge Fields" button (pick fields from each)
  - "AI Suggestion" badge showing AI-recommended resolution
- Batch approval: "Approve all AI suggestions" for non-critical items
- Individual approval for safety-critical CIs (must review manually)
- Merge preview before committing
- Rollback capability if merge creates problems

**Priority:** HIGH
**Rationale:** Merge is complex and error-prone. Visual comparison and guided resolution prevent mistakes. Semi-automatic with human approval balances efficiency and safety.
**User Answer:** Q4 - Semi-automatic merge, Q3 - Milestone-based merges

---

**REQ-FE-016: Conflict Resolution UI**
Frontend shall provide intuitive conflict resolution interface:
- Clear conflict explanation: "Team A says Status=Released, Team B says Status=In Development. Which is correct?"
- Side-by-side field comparison for conflicting CI
- Metadata comparison:
  - Last modified date/time for each version
  - Modified by (user name)
  - Source instance name
  - Certification status
  - Control level
- AI suggestion with confidence % and rationale
- History view: show change history from both sources
- Comments/notes field for documenting resolution decision
- "Defer Decision" option to come back to conflict later
- Conflict resolution audit trail (who resolved, when, what decision)

**Priority:** HIGH
**Rationale:** Conflicts are inevitable in distributed development. Clear UI helps users make informed decisions quickly and documents rationale for audit.

---

**REQ-FE-017: Work Assignment View**
Frontend shall provide work assignment and partitioning interface:
- "My Assigned CIs" view:
  - Filter to show only CIs assigned to me
  - Group by status (to do, in progress, done)
  - Priority indication
  - Due dates
- "Team's CIs" view:
  - See CIs assigned to my team
  - Workload balancing view (who has how many assignments)
  - Unassigned CIs list (available work)
- Assignment management (for managers):
  - Drag-and-drop CI assignment to users
  - Bulk assignment (assign 50 CIs to Team A)
  - Assignment templates (auto-assign software CIs to software team)
- Assignment notifications:
  - Notify user when CI is assigned to them
  - Notify user when assignment is removed
  - Notify user when assigned CI is modified by someone else

**Priority:** HIGH
**Rationale:** Work partitioning prevents conflicts and clarifies responsibilities. Essential for multi-user concurrent access.
**User Answer:** Q1C, Q2 - All scenarios including multi-site teams

---

**REQ-FE-018: Notifications Center**
Frontend shall provide comprehensive notifications interface:
- Notification inbox with categories:
  - Assignments (new CI assigned to me)
  - Changes (CI I'm watching was modified)
  - Approvals (CI needs my approval)
  - Mentions (someone mentioned me in comment)
  - System (merge completed, conflicts detected)
- Notification priority levels (critical, high, medium, low)
- Real-time notifications (toast/banner for critical items)
- Email integration (configurable: send email for critical notifications)
- Mark as read/unread
- Notification preferences (configure which events trigger notifications)
- "Watch" and "Unwatch" CIs to subscribe/unsubscribe from change notifications
- Batch actions (mark all as read, dismiss all low-priority)

**Priority:** MEDIUM
**Rationale:** In distributed teams, staying informed of relevant changes is critical. Notification center provides visibility without overwhelming users.

---

**REQ-FE-019: Comments and Discussions**
Frontend shall provide discussion/comment capability on CIs:
- Comment thread on each CI
- Rich text comments (formatting, links, embedded images)
- @mention functionality to notify specific users
- Reply threading (nested comments)
- Comment categories/tags:
  - Question
  - Issue
  - Suggestion
  - Decision
  - Review comment
- Resolve/close discussion threads
- Filter comments by category, user, date
- Export discussion thread to PDF for documentation
- Link comments to change requests (comment becomes part of CR justification)

**Priority:** MEDIUM
**Rationale:** Distributed teams need asynchronous communication on CIs. Comments provide context for decisions and enable remote collaboration.

---

**REQ-FE-020: Access Control Management Interface**
Frontend shall provide role-based access control (RBAC) management:
- User management:
  - User list with roles
  - Add/remove users
  - Assign roles (Admin, Engineer, Reviewer, Approver, Viewer)
  - Set team membership
- Team management:
  - Create/edit teams
  - Assign users to teams
  - Set team permissions
- CI-level permission management:
  - Set who can view/edit specific CIs
  - Set permissions by CI control level (Level 1 CIs restricted to senior engineers)
  - Set permissions by lifecycle phase (released CIs read-only except for CCB)
  - Inheritance (child CIs inherit parent CI permissions by default)
- Permission templates (apply standard permission sets)
- External stakeholder access:
  - Grant read-only access to customer, supplier, certification authority
  - Time-limited access (expires after 90 days)
  - Scope-limited access (only specific CIs visible)
- Permission audit log (who granted what permission to whom, when)

**Priority:** HIGH
**Rationale:** Complex access control is essential for multi-company, multi-site development. Prevents unauthorized changes and protects IP.
**User Answer:** Q6 - Complex access control required

---

**REQ-FE-021: Merge Preview and Comparison**
Frontend shall provide merge preview before committing:
- "What will change" summary:
  - New CIs to be added: count and list
  - Existing CIs to be updated: count and list
  - CIs with conflicts: count and list
  - Traceability links to be added/modified: count
- Impact analysis:
  - Which projects/teams are affected
  - Which safety-critical CIs are modified
  - Verification impact (how many tests need re-run)
- Simulation mode: "Show me what the database will look like after merge"
- Diff view: side-by-side comparison of before/after state
- Export merge plan to PDF for approval/documentation
- "Approve Merge" button (with confirmation: "This will modify 247 CIs. Proceed?")
- Scheduled merge: "Perform this merge at [date/time]" for off-hours execution

**Priority:** MEDIUM
**Rationale:** Milestone-based merges are high-risk operations. Preview prevents surprises and builds confidence.
**User Answer:** Q3 - Milestone-based merge

---

**REQ-FE-022: Activity Feed and Change History**
Frontend shall provide real-time activity feed:
- Project activity feed showing recent changes:
  - CI created/modified/deleted
  - Baseline created
  - Approval granted
  - Merge completed
  - Comment added
- Personal activity feed: "Changes to items I care about"
- Filter by:
  - Activity type (edits, approvals, merges, comments)
  - Date range
  - User (show all John's activities)
  - CI or CI type
  - Team
- "Replay" feature: show state of project at any point in time
- Export activity log to Excel/CSV
- Visual timeline view of project evolution

**Priority:** LOW
**Rationale:** Provides transparency and auditability. Helps users understand what happened during their absence.

---

**REQ-FE-023: Lock Status and Concurrent Edit Indicators**
Frontend shall provide real-time indicators of concurrent editing:
- Lock badge on CI card/row:
  - 🔒 "Locked by John Smith (editing since 14:30)"
  - ⏱️ "Lock expires in 45 minutes"
- Color coding:
  - Green = available
  - Yellow = locked by me
  - Red = locked by someone else
- Hover tooltip shows lock details (who, when, how long)
- Real-time updates (if John checks out CI while I'm viewing list, badge appears immediately via WebSocket)
- "Who's online" indicator (show which users are currently active)
- Concurrent viewer count: "3 people viewing this CI"

**Priority:** MEDIUM
**Rationale:** Real-time awareness prevents editing conflicts and improves collaboration. Users can see who's working on what.

---

### User Input

**REQ-FE-001: File Upload Capability**
The frontend shall provide file upload capability for USER responses to AI requests.

**Priority:** HIGH
**Rationale:** Users need to provide documents as input to AI.

---

## Backend Requirements

### Project Structuring

**REQ-BE-001: Internal Project Structure**
The backend shall internally structure user's project even when not displayed to user.

**Priority:** HIGH
**Rationale:** AI needs organized data model to function effectively.

---

**REQ-BE-002: Next Steps Guidance**
The backend shall provide "what should I do now" guidance (next steps planning).

**Priority:** MEDIUM
**Rationale:** Helps user navigate systems engineering workflow.

---

**REQ-BE-003: Database Write Operations**
The backend shall handle database write operations triggered by AI interactions.

**Priority:** CRITICAL
**Rationale:** Core functionality for data persistence.

---

**REQ-BE-004: File Format Parsing**
The backend shall support parsing multiple file formats (docx, txt, pdf, etc.).

**Priority:** HIGH
**Rationale:** Users work with various document formats.

---

### Review and Modification Management

**REQ-BE-005: Open Questions Storage**
The backend shall provide storage for open questions queue.

**Priority:** MEDIUM
**Rationale:** Supports AI's internal question management.

---

**REQ-BE-006: Design Review Workflow**
The backend shall support design review workflow (requirements vs design traceability).

**Priority:** HIGH
**Rationale:** Core systems engineering process.

---

**REQ-BE-007: Document Storage and Linking**
The backend shall manage document storage and traceability linking.

**Priority:** HIGH
**Rationale:** Foundation for document management system.

---

**REQ-BE-008: Modification Tracking**
The backend shall track modification status of all documents/artifacts.

**Priority:** HIGH
**Rationale:** Required for review workflow.

---

**REQ-BE-009: Automatic Flagging**
The backend shall automatically flag documents as "modified/needs review" when AI makes changes.

**Priority:** HIGH
**Rationale:** User awareness of AI modifications.

---

**REQ-BE-010: Document Aggregation**
The backend shall aggregate database content into logical "documents".

**Priority:** HIGH
**Rationale:** Documents are views of database content, not physical files.

---

**REQ-BE-011: Session State Management**
The backend shall manage and persist session state to enable users to pause and resume work, including:
- Conversation context
- Current workflow phase
- Open questions queue
- Last activity timestamp
- User's position in the workflow

**Priority:** HIGH
**Rationale:** Session continuity is critical for usability. Supports REQ-AI-028 and REQ-AI-029.

---

**REQ-BE-012: Project Initialization Workflow**
The backend shall support project initialization workflow including:
- Triggering project initialization interview when new project is created
- Storing initialization context (safety level, DAL/SIL, regulatory requirements, etc.) before proceeding to requirements gathering
- Selecting and configuring appropriate process templates based on initialization answers
- Linking project to applicable standards and regulatory frameworks
- Setting up project-specific verification/validation requirements based on criticality

**Priority:** HIGH
**Rationale:** Project initialization determines the entire structure and rigor of the development process. Backend must orchestrate this workflow and configure the project appropriately. Supports REQ-AI-032 through REQ-AI-037.

---

### Product Structure & Configuration Item Management

**REQ-BE-013: Bill of Materials (BOM) Management**
The backend shall support comprehensive BOM operations:
- Create, read, update, delete BOMs
- BOM versioning and release management
- BOM comparison (delta/diff between versions)
- BOM explosion (flatten multi-level BOM to show all components)
- Where-used analysis (which assemblies use this part?)
- BOM effectivity management (which BOM versions apply to which product serial numbers)
- BOM validation (check for circular references, missing parts, quantity errors)
- BOM import from external formats (Excel, CSV, PLM exports)
- BOM export to manufacturing/procurement formats

**Priority:** HIGH
**Rationale:** BOM is critical business logic that requires sophisticated backend processing. Manual BOM management is error-prone; automated validation and analysis improve quality.

---

**REQ-BE-014: Item Lifecycle Management**
The backend shall manage item/CI lifecycle including:
- Item status workflow (concept → prototype → qualification → production → obsolete)
- Change management for items (Engineering Change Order/ECN process)
- Approval workflow for new items and item changes
- Obsolescence management (track obsolete items, suggest replacements)
- Item maturity assessment (readiness for next phase)
- Automatic notifications for lifecycle transitions
- Audit trail of all item changes

**Priority:** HIGH
**Rationale:** Item lifecycle management ensures controlled progression through development phases. Backend orchestrates workflows and enforces business rules.

---

**REQ-BE-015: Configuration Item Change Impact Analysis**
The backend shall provide CI change impact analysis:
- Identify all CIs affected by a proposed change (direct and indirect)
- Analyze parent/child relationships (changing child affects parent assemblies)
- Analyze interface relationships (changing one CI may affect interfacing CIs)
- Analyze requirements traceability (which requirements are affected?)
- Analyze verification impact (which tests need to be re-run?)
- Generate impact assessment report for change review
- Estimate effort and risk based on scope of impact

**Priority:** MEDIUM
**Rationale:** Change impact analysis is critical for risk management and resource planning. Automated analysis reduces errors and provides comprehensive impact visibility.
**Reference:** docs/Level_2_User_Framework/CONFIGURATION_ITEM_MANAGEMENT.md

---

### Collaborative & Distributed Work

**REQ-BE-016: Concurrent Access Control and Locking**
The backend shall implement pessimistic locking for concurrent access:
- Lock acquisition: User requests lock on CI before editing
- Lock types:
  - Exclusive lock (only one user can edit)
  - Shared lock (multiple users can view, none can edit during review)
- Lock timeout: Automatic release after configurable period (default: 2 hours)
- Lock heartbeat: Extend lock while user is actively editing
- Lock override: Administrator can break lock with justification (logged in audit trail)
- Lock queue: If CI is locked, user can request notification when unlocked
- Deadlock prevention: System detects and prevents circular lock dependencies
- Lock cleanup: Release all locks when user session ends

**Priority:** CRITICAL
**Rationale:** Prevents simultaneous editing conflicts. Essential for multi-user concurrent access to same database.
**User Answer:** Q1C - Concurrent access is equal priority

---

**REQ-BE-017: Optimistic Conflict Detection**
The backend shall implement optimistic concurrency control as fallback:
- Version stamping: Every CI save increments version number
- Conflict detection on save:
  - Compare current version in database with version user started editing
  - If versions differ, another user modified CI while this user was editing
  - Reject save and show conflict notification
- Three-way merge support:
  - Base version (what user started with)
  - Their changes (what user wants to save)
  - Current version (what's in database now)
  - Attempt automatic merge of non-conflicting fields
- Manual conflict resolution: If auto-merge fails, present conflict to user
- Retry mechanism: Allow user to review current version and re-apply their changes

**Priority:** HIGH
**Rationale:** Backup mechanism when locks are not used or expire. Prevents lost updates.

---

**REQ-BE-018: Work Assignment and Partitioning**
The backend shall support work assignment to users and teams:
- Assignment operations:
  - Assign CI to user or team
  - Bulk assignment (assign 100 CIs at once)
  - Assignment templates (auto-assign based on CI type, category, or other criteria)
- Assignment rules:
  - Only assigned user/team can edit CI (configurable)
  - Others can view but not modify
  - Administrator can override
- Assignment delegation: User can delegate assigned CIs to another user
- Assignment notifications:
  - Notify user when CI is assigned
  - Notify user when assigned CI is modified by someone else (e.g., admin override)
  - Notify manager when assigned CI is completed
- Workload analytics: Report on user/team workload (number of assigned CIs, completion rate)

**Priority:** HIGH
**Rationale:** Work partitioning prevents conflicts and enables parallel work by multiple users.
**User Answer:** Q2 - All scenarios including multiple teams

---

**REQ-BE-019: Data Export for Federation**
The backend shall export project data for transfer to other AISET instances:
- Export formats:
  - AISET native format (complete fidelity, all data)
  - Milestone export (snapshot at baseline)
  - Partial export (selected CIs only, for supplier data sharing)
- Export packaging:
  - Single file (ZIP archive containing all data + metadata)
  - Include schema version for compatibility checking
  - Include source instance ID and export timestamp
- Export options:
  - Full export (entire project)
  - Incremental export (only changes since last export)
  - Filtered export (by CI type, team, status, etc.)
- Export validation: Verify export integrity before packaging
- Export audit trail: Log what was exported, when, by whom, to where

**Priority:** HIGH
**Rationale:** Enables distributed development with periodic data exchange between AISET instances.
**User Answer:** Q1C - Distributed mode is equal priority, Q3 - Milestone-based merges

---

**REQ-BE-020: Data Import from External AISET Instances**
The backend shall import project data from other AISET instances:
- Import validation:
  - Verify export file integrity (checksum)
  - Check schema compatibility (can current AISET version read this export?)
  - Detect source instance ID (prevent importing from same instance)
  - Preview import (show what will be imported before committing)
- Import modes:
  - New project import (create new project from export)
  - Merge import (integrate into existing project - see REQ-BE-021)
  - Reference import (link to external data without merging)
- Import options:
  - Map source IDs to target IDs (for ID collision avoidance)
  - Filter what to import (import only specific CI types or teams)
  - Preserve source metadata (track which instance data came from)
- Import rollback: Ability to undo import if problems detected

**Priority:** HIGH
**Rationale:** Counterpart to export. Enables receiving data from suppliers, partners, or other sites.

---

**REQ-BE-021: Intelligent Merge Engine with Conflict Detection**
The backend shall provide sophisticated merge capability for combining data from multiple AISET instances:
- Conflict detection algorithms:
  - **ID collision:** Same CI ID, different data (e.g., CI-SW-001 exists in both source and target with different content)
  - **Duplicate items:** Different CI IDs, same physical item (detected by part number, description similarity)
  - **Conflicting field values:** Same CI ID, different field values (e.g., source says Status=Released, target says Status=Draft)
  - **Broken references:** Source CI references requirement that doesn't exist in target database
  - **Circular dependencies:** Merge would create circular parent-child relationships
- Automatic merge rules (no conflicts):
  - New CIs (ID doesn't exist in target): auto-add
  - Identical CIs (exact match): skip
  - Non-overlapping field updates (source updated field A, target updated field B): merge both
  - Newer version precedence (if configured): keep newer version based on timestamp
- Conflict resolution strategies:
  - **AI-assisted:** Invoke REQ-AI-041 to suggest resolution
  - **Rule-based:** Apply configured rules (e.g., "certified version always wins")
  - **Manual:** Present conflict to user for decision (REQ-FE-016)
- Merge transaction: Entire merge is atomic (all succeed or all rollback)
- Merge audit trail: Complete record of what was merged, conflicts, resolutions

**Priority:** CRITICAL
**Rationale:** Core capability for distributed development. Merge is complex and error-prone; sophisticated engine prevents data corruption.
**User Answer:** Q4 - Semi-automatic merge with human approval

---

**REQ-BE-022: Merge Preview Generation**
The backend shall generate detailed merge preview before executing merge:
- Analysis phase (read-only, no changes):
  - Scan all source data
  - Compare against target database
  - Identify all conflicts, duplicates, broken references
  - Calculate merge statistics
  - Invoke AI suggestions for conflict resolution (REQ-AI-041)
- Preview report generation:
  - Summary: total items, auto-merge count, conflict count, duplicate count
  - Detailed list of conflicts with AI suggestions
  - Impact analysis: affected projects, teams, requirements, tests
  - Risk assessment: safety-critical CIs affected, certification impact
- Preview formats:
  - Interactive web UI (REQ-FE-021)
  - PDF export for documentation/approval
  - JSON export for programmatic processing
- Preview expiration: Preview is valid for X hours (data may change)

**Priority:** HIGH
**Rationale:** Milestone merges are high-risk. Preview allows review and approval before committing changes.
**User Answer:** Q3 - Milestone-based merges require careful review

---

**REQ-BE-023: Merge Rollback and Recovery**
The backend shall support rollback of failed or problematic merges:
- Pre-merge backup: Create snapshot before merge execution
- Rollback scenarios:
  - Merge failed (error during execution)
  - Merge created unexpected problems (user requests rollback)
  - Partial rollback (undo specific merged CIs, keep others)
- Rollback operation:
  - Restore database to pre-merge snapshot
  - Invalidate all changes made during merge
  - Notify affected users of rollback
  - Preserve merge attempt in audit log (for forensics)
- Rollback constraints:
  - Time limit: Can only rollback within X hours of merge (configurable)
  - User activity: Cannot rollback if users have modified merged CIs
  - Cascading protection: Prevent rollback if would break other data

**Priority:** MEDIUM
**Rationale:** Safety net for high-risk merge operations. Allows recovery from mistakes.

---

**REQ-BE-024: Notification and Alert Engine**
The backend shall generate intelligent notifications for relevant events:
- Event detection:
  - CI created/modified/deleted
  - CI assigned to user/team
  - CI requires approval
  - Lock status changed
  - Comment added with @mention
  - Merge completed
  - Conflict detected
- Recipient determination:
  - Use REQ-AI-043 to intelligently determine who should be notified
  - Respect user notification preferences
  - Suppress redundant notifications
- Notification delivery:
  - In-app notification (stored in database, displayed in REQ-FE-018)
  - Email notification (for critical events or user preference)
  - WebSocket push (real-time notification to active users)
- Notification batching: Group related notifications (e.g., "5 CIs assigned to you" instead of 5 separate notifications)
- Notification priority: Critical, High, Medium, Low (affects delivery method and UI prominence)

**Priority:** MEDIUM
**Rationale:** Keeps distributed teams informed of relevant changes without overwhelming them.

---

**REQ-BE-025: Role-Based Access Control (RBAC) Enforcement**
The backend shall enforce complex access control policies:
- Role definitions:
  - **Administrator:** Full access to everything
  - **Manager:** Assign work, approve changes, override locks
  - **Senior Engineer:** Edit any CI, approve Level 2-3 changes
  - **Engineer:** Edit assigned CIs, create draft CIs
  - **Reviewer:** Read access, comment capability, no edit
  - **Viewer:** Read-only access to permitted CIs
  - **External Stakeholder:** Limited read-only access (time/scope restricted)
- Permission checking on every operation:
  - Before allowing edit: check user role, CI assignment, CI control level, lifecycle status
  - Before allowing view: check user permissions, team membership, external access grants
  - Before allowing delete: check user role, CI status (cannot delete released CIs)
- Inheritance rules:
  - Team members inherit team permissions
  - Child CIs inherit parent CI permissions (by default)
  - Lower control level CIs inherit restrictions from higher level parents
- Permission caching: Cache permission decisions for performance (invalidate on permission change)

**Priority:** CRITICAL
**Rationale:** Essential for multi-company, multi-site development. Prevents unauthorized access and protects IP.
**User Answer:** Q6 - Complex access control required

---

**REQ-BE-026: Multi-User Session Management**
The backend shall manage concurrent user sessions:
- Session tracking:
  - Active sessions list (who's logged in)
  - Session timeout (logout after inactivity period)
  - Concurrent session limit (prevent one user from having 10 sessions)
- Session state management:
  - Track which CIs user is currently viewing/editing
  - Track user's locks
  - Track user's current filters/views
- Session cleanup:
  - Release all locks when session ends
  - Clean up temporary data
  - Log session end in audit trail
- Session security:
  - Session token rotation
  - Session hijacking detection
  - Force logout capability (administrator can end user's session)

**Priority:** HIGH
**Rationale:** Foundation for concurrent access. Proper session management prevents resource leaks and security issues.

---

**REQ-BE-027: ID Mapping and Translation for Merged Data**
The backend shall manage ID mapping when merging data from external instances:
- ID collision resolution:
  - Detect when source CI ID already exists in target
  - Generate new unique ID for imported CI
  - Create mapping: source_ID → target_ID
- ID translation:
  - Update all references to use target IDs (parent-child relationships, requirements traceability, etc.)
  - Preserve source ID in metadata for traceability
- Mapping persistence:
  - Store ID mappings in database (REQ-DB-063)
  - Support reverse lookup: given target ID, find source ID
- Mapping strategies:
  - **Renaming:** CI-SW-001 becomes CI-SUPPLIER_A-SW-001
  - **Remapping:** CI-SW-001 becomes CI-SW-237 (next available ID)
  - **Hybrid:** Use GUID internally, preserve source display ID

**Priority:** HIGH
**Rationale:** ID collisions are inevitable when merging independent AISET instances. Proper mapping prevents data corruption.
**User Answer:** Q5 - Hybrid identifier strategy (GUID + human-readable)

---

**REQ-BE-028: Duplicate Detection and Deduplication**
The backend shall detect and help resolve duplicate CIs:
- Duplicate detection algorithms:
  - Part number match (exact: same internal P/N, MPN, or SPN)
  - Fuzzy name matching (Levenshtein distance, phonetic similarity)
  - Attribute similarity scoring (combine multiple attributes: name, description, properties, supplier)
- Detection triggers:
  - During merge import (before committing)
  - On demand (user runs duplicate detection scan)
  - Continuous monitoring (flag new duplicates as they're created)
- Deduplication workflow:
  - Present duplicate pairs with similarity score
  - Show side-by-side comparison
  - Allow user to:
    - Confirm duplicate (merge into one CI)
    - Mark as not duplicate (suppress future warnings)
    - Defer decision
- Merge duplicates:
  - Select master CI (which one to keep)
  - Migrate traceability links from deprecated CI to master
  - Mark deprecated CI as obsolete
  - Create alias (deprecated ID redirects to master)

**Priority:** MEDIUM
**Rationale:** Duplicates cause procurement errors, traceability confusion, and certification issues. Automated detection finds duplicates humans miss.

---

**REQ-BE-029: Instance Identification and Source Tracking**
The backend shall track which AISET instance created each piece of data:
- Instance identification:
  - Each AISET instance has unique instance ID (GUID or configured name)
  - Instance metadata: name, organization, location, URL, contact
- Source tracking for all entities:
  - Created_by_instance: which instance created this CI
  - Modified_by_instance: which instance last modified this CI
  - Import_source_instance: if imported, which instance did it come from
- Multi-source support:
  - CI can have contributions from multiple instances (after multiple merges)
  - Track contribution history (instance A created, instance B modified field X, instance C modified field Y)
- Source visibility:
  - Display source instance in UI (e.g., "CI-SW-001 [created by Supplier A]")
  - Filter by source instance ("show me all CIs from Supplier B")
  - Audit trail includes source instance for all operations

**Priority:** HIGH
**Rationale:** In distributed development with multiple instances, knowing data origin is essential for trust, IP tracking, and troubleshooting.
**User Answer:** Q2 - All scenarios including prime contractor + suppliers

---

## Database Requirements

### Schema Structure

**REQ-DB-001: Conversation Storage**
Database schema shall support storage of AI conversations (ai_conversations, ai_messages tables).

**Priority:** CRITICAL
**Rationale:** Already implemented; captures full interaction history.

---

**REQ-DB-002: Open Questions Storage**
Database shall have a table/structure for storing open questions/clarifications linked to projects.

**Priority:** MEDIUM
**Rationale:** Supports AI question management workflow.

---

**REQ-DB-003: Design Review Storage**
Database shall store design review results and requirement-design traceability links.

**Priority:** HIGH
**Rationale:** Core systems engineering artifact.

---

**REQ-DB-004: Document Metadata Storage**
Database shall store document metadata (reference number, title, link to requirement/design).

**Priority:** HIGH
**Rationale:** Supports formal documentation and traceability.

---

**REQ-DB-005: Review Status Storage**
Database shall store review status for each document/artifact.

**Priority:** HIGH
**Rationale:** Tracks user validation of AI changes.

---

**REQ-DB-006: Protected Fields**
Database shall have protected fields that AI cannot modify.

**Priority:** CRITICAL
**Rationale:** Preserves data integrity and human decisions.

---

**REQ-DB-007: Modification History**
Database shall track modification history (what changed, when, by whom/what).

**Priority:** HIGH
**Rationale:** Audit trail for certification compliance.

---

**REQ-DB-008: Document Association**
Database shall be structured so that every element (table/entity) can be associated with one or more documents.

**Priority:** CRITICAL
**Rationale:** Enables document aggregation and frontend document list functionality. Foundation for document management system.

**Details:**
- Many-to-many relationships between entities and documents
- One entity can belong to multiple documents
- Supports document type definitions
- Enables frontend to display aggregated document views

**Examples:**
- A requirement → "Project Specification" + "Traceability Matrix"
- A design component → "Design Document" + "Traceability Matrix"
- A test case → "Test Plan" + "Verification Report" + "Traceability Matrix"

---

### Standards Compliance

**REQ-DB-009: System/Software/Hardware Requirements Storage**
Database shall store all requirements from a project including system requirements, software requirements, and hardware requirements.

**Priority:** CRITICAL
**Rationale:** Core requirement from SQL_requirement.md - supports full lifecycle management.
**Source:** SQL_requirement.md lines 4-5

---

**REQ-DB-010: Physical System Requirements Storage**
Database shall store all requirements for physical parts of the system (structure, aerodynamic, EME, etc.).

**Priority:** HIGH
**Rationale:** Comprehensive coverage of all engineering disciplines.
**Source:** SQL_requirement.md line 5

---

**REQ-DB-011: Design Data Storage**
Database shall store all design data from the project by direct text or by reference for data that cannot be stored in text format (3D drawings, models, etc.).

**Priority:** HIGH
**Rationale:** Supports mixed media design artifacts.
**Source:** SQL_requirement.md line 7

---

**REQ-DB-012: S1000D Responsibility Allocation**
Database shall enable allocation of responsibility in accordance with S1000D standard.

**Priority:** HIGH
**Rationale:** Industry standard for technical documentation and responsibility assignment.
**Source:** SQL_requirement.md line 9
**Implementation:** s1000d_resp table, allocation table

---

**REQ-DB-013: MIL-STD-881 Workpage Allocation**
Database shall enable allocation of workpages in accordance with MIL-STD-881 (Work Breakdown Structure).

**Priority:** HIGH
**Rationale:** Industry standard for work breakdown and assignment.
**Source:** SQL_requirement.md line 11
**Implementation:** wbs_node table, allocation table

---

**REQ-DB-014: ARP4754 Design Rules (System)**
For system items, database shall enable following strict design definition rules from ARP4754.

**Priority:** CRITICAL
**Rationale:** Aerospace safety standard compliance for system-level design.
**Source:** SQL_requirement.md line 13

---

**REQ-DB-015: DO-178C Design Rules (Software)**
For software items, database shall enable following strict design definition rules from DO-178C.

**Priority:** CRITICAL
**Rationale:** Aerospace safety standard compliance for software.
**Source:** SQL_requirement.md line 14
**Implementation:** software_item, software_design, software_code tables with DAL and design_level fields

---

**REQ-DB-016: DO-254 Design Rules (Hardware)**
For hardware items, database shall enable following strict design definition rules from DO-254.

**Priority:** CRITICAL
**Rationale:** Aerospace safety standard compliance for hardware.
**Source:** SQL_requirement.md line 15
**Implementation:** hardware_item, hardware_design, hardware_implementation tables with DAL and design_level fields

---

**REQ-DB-017: ARP4754 Validation Rules (System)**
For system items, database shall enable following strict requirement validation rules from ARP4754.

**Priority:** CRITICAL
**Rationale:** Ensures requirements are properly validated per ARP4754.
**Source:** SQL_requirement.md line 18
**Implementation:** validation table with requirement_id and verification_id linkage

---

**REQ-DB-018: DO-178C Validation Rules (Software)**
For software items, database shall enable following strict requirement validation rules from DO-178C.

**Priority:** CRITICAL
**Rationale:** Ensures software requirements are properly validated.
**Source:** SQL_requirement.md line 19

---

**REQ-DB-019: DO-254 Validation Rules (Hardware)**
For hardware items, database shall enable following strict requirement validation rules from DO-254.

**Priority:** CRITICAL
**Rationale:** Ensures hardware requirements are properly validated.
**Source:** SQL_requirement.md line 20

---

**REQ-DB-020: ARP4754 Verification Rules (System)**
For system items, database shall enable following strict requirement verification rules from ARP4754.

**Priority:** CRITICAL
**Rationale:** Ensures requirements are properly verified per ARP4754.
**Source:** SQL_requirement.md line 22
**Implementation:** verification table with method, environment, config_baseline_id

---

**REQ-DB-021: DO-178C Verification Rules (Software)**
For software items, database shall enable following strict requirement verification rules from DO-178C.

**Priority:** CRITICAL
**Rationale:** Ensures software requirements are properly verified.
**Source:** SQL_requirement.md line 23
**Implementation:** coverage table for test coverage tracking

---

**REQ-DB-022: DO-254 Verification Rules (Hardware)**
For hardware items, database shall enable following strict requirement verification rules from DO-254.

**Priority:** CRITICAL
**Rationale:** Ensures hardware requirements are properly verified.
**Source:** SQL_requirement.md line 24

---

**REQ-DB-023: ARP4754 Configuration Rules (System)**
For system items, database shall enable following strict configuration rules from ARP4754.

**Priority:** CRITICAL
**Rationale:** Configuration management per ARP4754 standards.
**Source:** SQL_requirement.md line 27
**Implementation:** baseline, baseline_item, entity_version tables

---

**REQ-DB-024: DO-178C Configuration Rules (Software)**
For software items, database shall enable following strict configuration rules from DO-178C.

**Priority:** CRITICAL
**Rationale:** Software configuration management per DO-178C.
**Source:** SQL_requirement.md line 28

---

**REQ-DB-025: DO-254 Configuration Rules (Hardware)**
For hardware items, database shall enable following strict configuration rules from DO-254.

**Priority:** CRITICAL
**Rationale:** Hardware configuration management per DO-254.
**Source:** SQL_requirement.md line 29

---

### Workflow Support

**REQ-DB-026: AI Job Queue**
Database shall support AI job queueing and tracking.

**Priority:** HIGH
**Rationale:** Manages AI work queue for asynchronous processing.
**Source:** SQL_requirement.md - AI_JOB table
**Implementation:** ai_job table with job_type, payload, status, executed_by

---

**REQ-DB-027: Audit Trail**
Database shall maintain complete audit log of all actions by humans and AI agents.

**Priority:** CRITICAL
**Rationale:** Required for certification compliance and traceability.
**Source:** SQL_requirement.md - AUDIT_LOG table
**Implementation:** audit_log table with actor_id, actor_type, action, target_type, target_id, payload

---

**REQ-DB-028: Approval Workflow**
Database shall support approval workflow for entities requiring human validation.

**Priority:** CRITICAL
**Rationale:** Human-in-the-loop validation for safety-critical changes.
**Source:** SQL_requirement.md - APPROVAL table
**Implementation:** approval table with entity_type, entity_id, approved_by, verdict

---

**REQ-DB-029: Change Request Management**
Database shall support change request tracking and management.

**Priority:** HIGH
**Rationale:** Formal change management process.
**Source:** SQL_requirement.md - CHANGE_REQUEST table
**Implementation:** change_request table linked to project

---

**REQ-DB-030: Review Management**
Database shall support formal review processes with review items and findings.

**Priority:** HIGH
**Rationale:** Supports design reviews, code reviews, and certification audits.
**Source:** SQL_requirement.md - REVIEW and REVIEW_ITEM tables
**Implementation:** review and review_item tables

---

**REQ-DB-031: Traceability Links**
Database shall support generic traceability links between any entity types.

**Priority:** CRITICAL
**Rationale:** Bidirectional traceability required for certification.
**Source:** SQL_requirement.md - TRACELINK table
**Implementation:** tracelink table with src_type, src_id, dst_type, dst_id, link_type

---

**REQ-DB-032: Requirement Derivation Tracking**
Database shall track parent-child relationships between derived requirements.

**Priority:** HIGH
**Rationale:** Supports requirement decomposition and traceability.
**Source:** SQL_requirement.md - REQUIREMENT_DERIVATION table
**Implementation:** requirement_derivation table with parent_req_id, child_req_id, rationale

---

**REQ-DB-033: Lifecycle Deliverables**
Database shall track lifecycle deliverables (manuals, schematics, software packages, etc.).

**Priority:** MEDIUM
**Rationale:** Complete project artifact management.
**Source:** SQL_requirement.md - LIFECYCLE_DELIVERABLE table
**Implementation:** lifecycle_deliverable table

---

**REQ-DB-034: Project Status Storage**
Database shall store overall project status beyond just open questions, including:
- Current project phase (requirements gathering, design, verification, etc.)
- Completed tasks/milestones
- Pending tasks
- Current focus area
- Last activity summary
- Workflow position

**Priority:** HIGH
**Rationale:** Enables session resumption (REQ-AI-028, REQ-AI-029) and provides user with project overview (REQ-FE-007).
**Supports:** Session continuity and user orientation

---

**REQ-DB-035: Project Context Storage**
Database shall store project initialization answers including:
- Safety criticality flag (boolean: is product safety-critical?)
- Worst-case failure scenario description
- Development Assurance Level (DAL) or Safety Integrity Level (SIL)
- Product domain/industry (aerospace, medical, automotive, industrial, etc.)
- Product scope and boundaries definition
- Target users/customers
- Problem statement and value proposition
- Make-vs-buy strategy
- Resources and timeline constraints
- Expected product lifecycle duration
- Production volume expectations

**Priority:** CRITICAL
**Rationale:** Project context is foundational data that determines all subsequent development activities. This information must be stored and accessible throughout the project lifecycle. Required by REQ-AI-032, REQ-AI-033, REQ-AI-034, REQ-AI-035.

---

**REQ-DB-036: Standards and Regulatory Requirements Mapping**
Database shall support linking projects to applicable standards and regulatory requirements:
- Many-to-many relationship between projects and standards (one project may comply with multiple standards)
- Standard reference table including:
  - Standard name (e.g., "DO-178C", "ISO 26262", "IEC 62304")
  - Standard version/revision
  - Applicable sections/clauses
  - Required compliance level (if applicable)
- Regulatory authority table including:
  - Authority name (e.g., "FAA", "EASA", "FDA", "CE")
  - Regulation reference
  - Certification requirements
  - Approval needed flag
- Traceability from requirements/design/tests to standard clauses

**Priority:** CRITICAL
**Rationale:** Different projects require compliance with different standards. The database must support flexible mapping so AISET can adapt to aerospace (DO-178C), medical (IEC 62304), automotive (ISO 26262), or other domains. Required by REQ-AI-033, REQ-AI-037, and REQ-FE-009.

---

### Product Structure & Configuration Item Management

**REQ-DB-037: Product Breakdown Structure**
Database shall support hierarchical product decomposition:
- Multi-level hierarchical structure (system → subsystem → assembly → subassembly → component → part)
- Parent-child relationships with position/instance information
- Quantity per assembly (how many of each child in parent)
- Support for multiple product structures (as-designed, as-built, as-maintained)
- Integration with Work Breakdown Structure (WBS) from REQ-DB-013
- Support for product variants (different configurations of same base product)
- Recursive queries for full hierarchy traversal

**Priority:** CRITICAL
**Rationale:** Product breakdown structure is fundamental to systems engineering. All other information (requirements, design, tests, CIs) relates to product structure elements.

---

**REQ-DB-038: Item Master Data**
Database shall store comprehensive item master data:
- Unique item identifier (internal part number)
- Item name and description
- Item type (purchased, manufactured, COTS, assembly, etc.)
- Item category (mechanical, electrical, electronic, software, firmware, documentation, data, tools, models)
- Revision/version with version history
- Unit of measure
- Physical properties (weight, dimensions, materials)
- Lifecycle status (concept, prototype, qualification, production, obsolete, archived)
- Created date, modified date, created by, modified by
- Metadata/custom fields (JSONB for extensibility)

**Priority:** CRITICAL
**Rationale:** Item master data is the foundation for configuration management, procurement, manufacturing, and support. Complete and accurate item data is essential.

---

**REQ-DB-039: Supplier Management**
Database shall store supplier information:
- Supplier unique identifier and name
- Supplier contact information (address, phone, email, website)
- Approved Vendor List (AVL) status (approved, qualified, conditional, not approved)
- Supplier qualification level and certification status
- Supplier certifications (ISO 9001, AS9100, IATF 16949, etc.)
- Supplier performance metrics (on-time delivery, quality ratings, responsiveness)
- Supplier notes and history
- Many-to-many relationship: items ↔ suppliers (one item may have multiple approved suppliers)

**Priority:** HIGH
**Rationale:** Supplier management is critical for procurement and supply chain risk management. Tracking approved vendors ensures quality and compliance.

---

**REQ-DB-040: Part Number Management**
Database shall manage multiple part number types and cross-references:
- Internal part number (company P/N) - primary identifier
- Manufacturer part number (MPN)
- Supplier part number (SPN) - may differ from MPN
- Customer part number (CPN) - for customer-specific variants
- Legacy part numbers (for replacement/obsolescence tracking)
- Cross-reference table linking all part number types for same item
- Alternate/substitute parts (form-fit-function equivalents)
- Part number format validation based on project numbering scheme

**Priority:** HIGH
**Rationale:** Multiple part numbering systems exist in complex supply chains. Cross-referencing ensures correct parts are procured and used.

---

**REQ-DB-041: Serial Number and Lot Tracking**
Database shall support serial number and lot/batch tracking:
- Serial number for serialized items (unique per individual unit)
- Lot/batch number for lot-tracked items (group of units from same production run)
- Manufacturing date and location
- Expiration date (for time-limited items)
- Traceability to manufacturing records and raw materials
- As-built configuration (which specific S/N parts are in which S/N assembly)
- Many-to-many relationship: serial numbers ↔ assemblies (for tracking)
- Serial number effectivity (which serial numbers have which configuration)

**Priority:** HIGH
**Rationale:** Serial/lot tracking is required for aerospace, medical, and automotive products. Enables product recalls, failure investigations, and configuration audits.
**Compliance:** Required for DO-178C, IEC 62304, ISO 26262, 21 CFR Part 820

---

**REQ-DB-042: Bill of Materials (BOM)**
Database shall store Bill of Materials information:
- BOM type (engineering BOM, manufacturing BOM, service BOM, as-built BOM)
- Parent item (assembly) and child items (components)
- Quantity per assembly
- Reference designators (for electrical items: R1, C5, U12, etc.)
- Find numbers (drawing callout numbers for mechanical items)
- BOM position/sequence (ordering of items in BOM)
- BOM versioning (track changes to BOM over time)
- BOM effectivity (which BOM version applies to which product serial numbers or date ranges)
- Optional/alternative items (items used in some configurations but not others)
- BOM status (draft, released, obsolete)

**Priority:** CRITICAL
**Rationale:** BOM defines product structure for manufacturing and procurement. Accurate BOM is essential for producibility and cost management.

---

**REQ-DB-043: Procurement and Supply Chain Data**
Database shall store procurement-related information per item:
- Lead time (standard procurement time)
- Minimum order quantity (MOQ)
- Unit cost and pricing tiers (volume pricing)
- Source strategy (single source, dual source, multiple sources, COTS)
- Criticality flag (critical item, long-lead item, strategic item)
- Obsolescence status (active, at risk, obsolete, replacement available)
- Last-time-buy information
- Inventory information (on-hand quantity, reorder point)
- Preferred supplier designation

**Priority:** MEDIUM
**Rationale:** Procurement data supports make-vs-buy decisions, cost estimation, and supply chain risk management.

---

**REQ-DB-044: Item Configuration and Interchangeability**
Database shall support item configuration management:
- Approved configurations for each item (which variants are allowed)
- Interchangeability rules:
  - Form-Fit-Function (F3) interchangeable: full drop-in replacement
  - Form-Fit (F2) interchangeable: physical fit but functional differences
  - Not interchangeable: requires design review
- Configuration effectivity (which items apply to which product serial numbers/lots/dates)
- Deviation and waiver tracking (approved non-standard configurations)
- Retrofit applicability (which older units can be upgraded to new configuration)

**Priority:** HIGH
**Rationale:** Configuration management ensures product integrity. Interchangeability rules prevent incorrect substitutions that could cause failures.
**Compliance:** Required for aerospace configuration audits

---

**REQ-DB-045: Item-to-Requirement Traceability**
Database shall link items/CIs to requirements:
- Many-to-many relationship: items ↔ requirements
- Bidirectional traceability: item → requirements satisfied, requirement → items that implement it
- Traceability type (satisfies, verifies, derives from)
- Traceability at multiple levels (system requirement → system CI, software requirement → software CI)
- Gap analysis support (requirements without items, items without requirements)
- Impact analysis (changing requirement affects which items?)

**Priority:** CRITICAL
**Rationale:** Requirements-to-item traceability is mandatory for certification (DO-178C, IEC 62304, ISO 26262). Proves that all requirements are implemented.

---

**REQ-DB-046: Configuration Item Extended Types and Categories**
Database shall support comprehensive CI type classification:
- CI type categories:
  - Software (source code, executables, libraries, databases, scripts)
  - Hardware (PCBAs, ASICs, FPGAs, electronic assemblies)
  - Firmware (embedded software in hardware devices)
  - Mechanical (parts, assemblies, drawings, 3D models)
  - Documentation (requirements, design docs, test procedures, manuals, certif ication artifacts)
  - Data (configuration files, calibration data, databases, parameter sets)
  - Tools (compilers, linkers, test equipment, development tools - require DO-330 qualification)
  - Models (simulation models, AI/ML models, digital twins, mathematical models)
- CI subtype within each category (customizable taxonomy)
- Multiple categorization (CI can belong to multiple categories)

**Priority:** HIGH
**Rationale:** Different CI types require different processes, standards, and verification methods. Proper categorization ensures correct treatment.
**Reference:** docs/Level_2_User_Framework/CONFIGURATION_ITEM_MANAGEMENT.md

---

**REQ-DB-047: Configuration Item Baseline and Control Management**
Database shall store CI configuration control information:
- Baseline status (draft, under review, baselined, released, obsolete, archived)
- Configuration control level:
  - Level 1: Customer/Authority approval required
  - Level 2: CCB (Configuration Control Board) approval
  - Level 3: Engineering Manager approval
  - Level 4: Controlled, no formal approval
  - Level 5: Uncontrolled
- Change control status (open for change, change controlled, frozen)
- Baseline membership (which baseline(s) include this CI version)
- Baseline types (functional, allocated, product baselines per IEEE 828)
- Release date and release approval information
- Access control (who can view/modify based on control level)

**Priority:** CRITICAL
**Rationale:** Configuration control prevents unauthorized changes and ensures proper approval. Higher control levels require more rigorous review for safety-critical items.
**Compliance:** Required by DO-178C, ISO 26262, IEC 62304

---

**REQ-DB-048: Configuration Item Verification and Certification Status**
Database shall track CI verification and certification:
- Verification status (not started, in progress, verified, verification failed, accepted)
- Verification method (test, analysis, inspection, demonstration)
- Verification coverage percentage (% of requirements verified)
- Links to test cases and test results
- Certification status (not applicable, required, in progress, qualified, certified, certification failed)
- Certification authority (FAA, EASA, FDA, etc.)
- Certification date and certification reference
- Qualification status (for tools per DO-330, for COTS per DO-254)

**Priority:** HIGH
**Rationale:** Verification and certification status tracking is essential for compliance and project visibility. Identifies items blocking certification.

---

**REQ-DB-049: Configuration Item Change History and Deviation Tracking**
Database shall maintain complete CI change history:
- Version-by-version change log with descriptions
- Change request reference (ECR/ECO/ECN number) for each change
- Change date, changed by, reviewed by, approved by
- Change rationale and impact summary
- Deviation/waiver tracking:
  - Deviation ID and description
  - Deviation status (active, closed, expired)
  - Deviation justification
  - Deviation approval authority and date
  - Deviation expiration date (for temporary deviations)
  - Items affected by deviation

**Priority:** HIGH
**Rationale:** Complete change history provides audit trail for certification. Deviation tracking ensures non-conformances are controlled and approved.
**Compliance:** Required by DO-178C, ISO 26262, 21 CFR Part 820

---

**REQ-DB-050: Configuration Item Safety and Security Classification**
Database shall store CI safety and security classification:
- Safety classification (safety-critical, safety-related, non-safety)
- Safety impact level (catastrophic, hazardous, major, minor, no effect - from FHA)
- Development Assurance Level (DAL A-E) or SIL (1-4) or ASIL (A-D)
- Links to safety assessments (FTA, FMEA, FHA, hazard analysis)
- Failure mode impact description
- Security classification (security-critical, security-relevant, non-security)
- Security level (per DO-326A/ED-202A if applicable)
- Links to threat modeling and security assessments
- Cybersecurity controls required

**Priority:** HIGH
**Rationale:** Safety and security classification drives development rigor, verification requirements, and certification activities. Critical for risk management.
**Compliance:** Required by DO-178C/DO-254, ISO 26262, IEC 62304, DO-326A

---

**REQ-DB-051: Configuration Item Data Rights and Export Control**
Database shall store CI intellectual property and export control information:
- Data rights classification:
  - Proprietary
  - Limited rights
  - Government purpose rights
  - Unlimited rights
  - Open source (with license type: GPL, MIT, Apache, etc.)
- IP ownership (company, supplier, customer, joint, licensed)
- License information and restrictions
- Export control classification:
  - EAR99 (Export Administration Regulations)
  - ITAR (International Traffic in Arms Regulations)
  - Dual-use
  - ECCN (Export Control Classification Number)
- Export license requirements
- Country restrictions
- Handling and distribution restrictions

**Priority:** MEDIUM
**Rationale:** Data rights and export control compliance is legally required. Violations can result in severe penalties. Tracking ensures proper handling.
**Compliance:** ITAR, EAR, DFARS requirements

---

### Collaborative & Distributed Work

**REQ-DB-052: Hybrid Identifier System (GUID + Display ID)**
Database shall implement hybrid identifier system for all entities:
- **GUID (Global Unique Identifier):**
  - 128-bit UUID for internal database use
  - Guaranteed globally unique (no collisions even across AISET instances)
  - Used as primary key in database
  - Never reused, never changes
- **Display ID (Human-Readable):**
  - Human-readable identifier for user interface (e.g., "CI-SW-001", "REQ-SYS-045")
  - May include instance prefix for merged items (e.g., "SUPPLIER_A-SW-001")
  - Configurable format per project (numbering scheme, prefix rules)
  - Stored as separate field, indexed for fast lookup
- **Legacy/Source ID:**
  - Original ID from source AISET instance (if imported)
  - Preserved for traceability and cross-reference
- **ID mapping table:** Maps source IDs to target IDs after merge (REQ-DB-063)

**Priority:** CRITICAL
**Rationale:** Hybrid approach provides collision-free merging (GUID) while maintaining human readability (Display ID). Essential for distributed development.
**User Answer:** Q5 - Hybrid identifier strategy

---

**REQ-DB-053: User Session Management**
Database shall store user session information for concurrent access:
- **Session table:**
  - Session ID (GUID)
  - User ID
  - Session start time
  - Last activity time
  - Session expiration time
  - IP address
  - User agent (browser/device)
  - Session state (JSON: current filters, views, context)
- **Active sessions index:** Fast lookup of active sessions per user
- **Session cleanup:** Automatic deletion of expired sessions
- **Concurrent session limit:** Enforce maximum sessions per user

**Priority:** HIGH
**Rationale:** Foundation for multi-user concurrent access. Tracks who's logged in and their context.

---

**REQ-DB-054: Lock Management**
Database shall store CI locks for pessimistic concurrency control:
- **Lock table:**
  - Lock ID (GUID)
  - Entity type (CI, requirement, test, etc.)
  - Entity ID (which CI is locked)
  - Lock type (exclusive, shared)
  - Locked by (user ID)
  - Lock acquired time
  - Lock expires time
  - Lock heartbeat time (last activity)
  - Session ID (link to user session)
- **Lock queue:** Users waiting for lock release
- **Deadlock detection:** Track lock dependencies to prevent circular locks
- **Lock history:** Audit trail of locks (who locked what, when, duration)

**Priority:** CRITICAL
**Rationale:** Prevents simultaneous editing conflicts. Core mechanism for concurrent access.
**User Answer:** Q1C - Concurrent access is equal priority

---

**REQ-DB-055: Work Assignment and Partitioning**
Database shall store work assignments for CI ownership:
- **Assignment table:**
  - Assignment ID (GUID)
  - CI ID (which CI is assigned)
  - Assigned to (user ID or team ID)
  - Assignment type (primary owner, reviewer, approver)
  - Assigned by (user ID of assigner)
  - Assignment date
  - Due date (optional)
  - Priority (high, medium, low)
  - Status (to do, in progress, done)
  - Completion date
- **Assignment history:** Track assignment changes over time
- **Workload view:** Aggregate assignments per user/team for load balancing

**Priority:** HIGH
**Rationale:** Work partitioning is essential for parallel work by multiple users without conflicts.

---

**REQ-DB-056: User Roles and Permissions (RBAC)**
Database shall store role-based access control information:
- **User table extensions:**
  - Role (Admin, Manager, Senior Engineer, Engineer, Reviewer, Viewer, External)
  - Team membership (many-to-many: user ↔ teams)
  - Account status (active, disabled, locked)
  - Account expiration date (for temporary/external users)
- **Role definition table:**
  - Role name
  - Role description
  - Permission set (JSON: list of allowed operations)
  - Custom roles support (beyond predefined roles)
- **User permissions override:** Per-user permission exceptions
- **Permission cache table:** Cache permission decisions for performance

**Priority:** CRITICAL
**Rationale:** Foundation for complex access control. Required for multi-company, multi-site development.
**User Answer:** Q6 - Complex access control required

---

**REQ-DB-057: Team-Based Permissions**
Database shall support team-based access control:
- **Team table:**
  - Team ID (GUID)
  - Team name
  - Organization/site
  - Team lead (user ID)
  - Team members (many-to-many: team ↔ users)
- **Team permissions:**
  - Default permissions for team members
  - Team-level CI access grants (team has access to specific CIs or CI categories)
- **Team hierarchy:** Support for parent/child teams (permissions inheritance)

**Priority:** HIGH
**Rationale:** Teams are fundamental unit of organization in distributed development. Team-based permissions simplify management.

---

**REQ-DB-058: CI-Level Permissions**
Database shall support granular permissions per CI:
- **CI access control list (ACL):**
  - CI ID
  - User/Team ID
  - Permission level (view, edit, approve, delete)
  - Granted by (user ID)
  - Grant date
  - Expiration date (for temporary access)
  - Grant rationale/notes
- **Permission inheritance:**
  - Child CIs inherit parent CI permissions by default
  - Override capability (child can have different permissions)
- **Control level enforcement:**
  - Level 1 CIs automatically restricted to senior engineers/managers
  - Released CIs automatically read-only except for CCB members

**Priority:** HIGH
**Rationale:** Granular control needed for IP protection, supplier access, external stakeholder access.

---

**REQ-DB-059: Comments and Discussions**
Database shall store discussion threads on CIs:
- **Comment table:**
  - Comment ID (GUID)
  - Entity type (CI, requirement, test, etc.)
  - Entity ID (which CI this comment is on)
  - Parent comment ID (for reply threading)
  - Author (user ID)
  - Comment text (rich text/markdown)
  - Comment category (question, issue, suggestion, decision, review comment)
  - Created date
  - Modified date
  - Status (open, resolved, closed)
  - Resolved by (user ID)
  - Resolved date
- **Mentions:** @mention tracking (which users were mentioned in comment)
- **Attachments:** Link comments to files/images
- **Comment search:** Full-text search across all comments

**Priority:** MEDIUM
**Rationale:** Asynchronous communication essential for distributed teams. Captures rationale for decisions.

---

**REQ-DB-060: Notifications and Subscriptions**
Database shall store notifications and user subscriptions:
- **Notification table:**
  - Notification ID (GUID)
  - Recipient (user ID)
  - Notification type (assignment, change, approval, mention, system)
  - Priority (critical, high, medium, low)
  - Title
  - Message
  - Link to entity (CI ID, requirement ID, etc.)
  - Created date
  - Read status (read, unread)
  - Read date
  - Delivery status (pending, sent, delivered, failed)
- **Subscription table (watch list):**
  - User ID
  - Entity type
  - Entity ID (which CI user is watching)
  - Subscription date
- **Notification preferences:**
  - Per-user preferences (which events trigger notifications, email vs in-app, frequency)

**Priority:** MEDIUM
**Rationale:** Keeps distributed teams informed without overwhelming them. User control over notification flow.

---

**REQ-DB-061: Merge Metadata and History**
Database shall store comprehensive merge history:
- **Merge session table:**
  - Merge ID (GUID)
  - Source instance ID (which AISET instance exported this data)
  - Target instance ID (this instance)
  - Merge type (full, incremental, filtered)
  - Merge initiated by (user ID)
  - Merge initiated date
  - Merge completed date
  - Merge status (preview, in progress, completed, failed, rolled back)
  - Total items analyzed
  - Auto-merged count
  - Conflict count
  - Duplicate count
  - Merge approval by (user ID)
  - Merge approval date
- **Merge details:** Link to specific CIs merged, conflicts resolved, decisions made

**Priority:** HIGH
**Rationale:** Complete audit trail for milestone-based merges. Essential for troubleshooting and compliance.
**User Answer:** Q3 - Milestone-based merges

---

**REQ-DB-062: Source Instance Tracking**
Database shall track source AISET instance for all entities:
- **AISET instance table:**
  - Instance ID (GUID)
  - Instance name
  - Organization name
  - Location/site
  - URL (if accessible)
  - Contact information
  - Instance type (prime contractor, supplier, internal site, customer, authority)
  - Trust level (trusted, restricted, external)
- **Entity source tracking:** Add to all entity tables:
  - Created_by_instance (which instance created this entity)
  - Modified_by_instance (which instance last modified)
  - Import_source_instance (if imported, from which instance)
  - Import_merge_ID (which merge operation brought this in)
- **Multi-contributor tracking:**
  - Track multiple instances that contributed to entity
  - Instance A created, Instance B modified field X, Instance C modified field Y

**Priority:** HIGH
**Rationale:** Know data origin for trust, IP tracking, troubleshooting. Critical for multi-company development.
**User Answer:** Q2 - All scenarios including prime + suppliers

---

**REQ-DB-063: ID Mapping Table**
Database shall maintain ID mappings for merged entities:
- **ID mapping table:**
  - Mapping ID (GUID)
  - Source instance ID
  - Source entity type (CI, requirement, etc.)
  - Source entity ID (original ID in source instance)
  - Target entity GUID (mapped to this entity in target database)
  - Target entity display ID
  - Merge ID (which merge created this mapping)
  - Mapping type (rename, remap, alias)
  - Created date
- **Bidirectional lookup:**
  - Given source (instance + ID) → find target GUID
  - Given target GUID → find all source IDs (may have been imported multiple times)
- **Alias support:** Old ID redirects to new ID for continuity

**Priority:** HIGH
**Rationale:** Essential for resolving ID collisions during merge. Maintains traceability across instances.
**User Answer:** Q5 - Hybrid identifiers with mapping

---

**REQ-DB-064: Merge Conflicts**
Database shall store merge conflicts and their resolutions:
- **Conflict table:**
  - Conflict ID (GUID)
  - Merge ID (which merge session)
  - Conflict type (ID collision, duplicate item, field conflict, broken reference)
  - Source entity (from source instance)
  - Target entity (from target instance, if exists)
  - Conflicting fields (which fields differ)
  - Source value
  - Target value
  - AI suggested resolution (from REQ-AI-041)
  - AI confidence score
  - Actual resolution (what was chosen)
  - Resolved by (user ID)
  - Resolved date
  - Resolution rationale/notes
  - Conflict status (pending, resolved, deferred)
- **Conflict search:** Find all conflicts by type, status, entity

**Priority:** HIGH
**Rationale:** Documents merge decisions for audit. Enables learning from past conflict resolutions.

---

**REQ-DB-065: Merge Rollback Support**
Database shall support merge rollback capability:
- **Pre-merge snapshot:**
  - Snapshot ID (GUID)
  - Merge ID (which merge this is for)
  - Snapshot timestamp
  - Snapshot storage (database dump, diff, or reference)
  - Snapshot validity period
- **Rollback log:**
  - Rollback ID (GUID)
  - Merge ID (which merge was rolled back)
  - Rollback initiated by (user ID)
  - Rollback date
  - Rollback reason
  - Entities affected by rollback
  - Rollback status (in progress, completed, failed)
- **Rollback constraints tracking:** Track user modifications post-merge to prevent unsafe rollback

**Priority:** MEDIUM
**Rationale:** Safety net for high-risk milestone merges. Enables recovery from mistakes.

---

**REQ-DB-066: Enhanced Audit Trail for Multi-Instance**
Database shall enhance audit trail (REQ-DB-027) for distributed work:
- **Audit log enhancements:**
  - Source instance ID (which instance performed action)
  - Session ID (link to user session)
  - Lock ID (if action required lock)
  - Merge ID (if action was part of merge)
  - Original entity values (for conflict analysis)
  - Permission check result (was action authorized)
- **Cross-instance audit trail:**
  - Track entity lifecycle across multiple instances
  - "CI-SW-001 created by Supplier A on 2025-01-15, imported to Prime Contractor on 2025-03-20, modified by Prime on 2025-03-22"
- **Audit trail federation:** Export audit log with data export for complete traceability

**Priority:** HIGH
**Rationale:** Comprehensive audit trail required for certification of distributed-development products. Proves compliance across organizational boundaries.

---

**REQ-DB-067: External References (Supplier/Customer IDs)**
Database shall track external identifier cross-references:
- **External reference table:**
  - Reference ID (GUID)
  - Internal entity GUID (AISET entity)
  - Internal display ID
  - External system type (supplier PLM, customer system, authority database)
  - External system ID/URL
  - External entity ID (ID in external system)
  - Reference type (supplier P/N, customer designation, authority certification ID)
  - Reference notes
  - Verified date (last verified this reference is still valid)
- **Multiple external references per entity:**
  - One CI may have supplier ID, customer ID, and authority ID
  - Track all for traceability

**Priority:** MEDIUM
**Rationale:** Real-world products have IDs in multiple systems (supplier, prime, customer, certification authority). Cross-reference essential for communication.

---

**REQ-DB-068: Data Sharing Agreements**
Database shall track data sharing policies for multi-party projects:
- **Sharing agreement table:**
  - Agreement ID (GUID)
  - Project ID
  - Partner instance ID (supplier, customer, etc.)
  - Agreement type (NDA, data use agreement, limited rights)
  - What data is shared (all CIs, only specific CI types, only public data)
  - What data is restricted (proprietary CIs, internal notes, cost data)
  - Sharing frequency (real-time, weekly, milestone-based)
  - Agreement start date
  - Agreement end date
  - Agreement status (active, expired, terminated)
- **Entity-level sharing flags:**
  - Each CI marked: shareable with partner X (yes/no)
  - Automatic filtering on export based on sharing agreements

**Priority:** LOW
**Rationale:** IP protection in multi-company projects. Ensures only authorized data is shared with each partner.

---

**REQ-DB-069: Activity Log for Transparency**
Database shall maintain detailed activity log for user awareness:
- **Activity log table:**
  - Activity ID (GUID)
  - Activity type (CI created, modified, deleted, approved, commented, locked, unlocked, merged)
  - Entity type
  - Entity ID
  - Actor (user ID or "system" for automated actions)
  - Activity timestamp
  - Activity description (human-readable summary)
  - Changed fields (what changed in this activity)
  - Old values → new values
  - Related entities (if this activity affects other entities)
- **Activity feed generation:**
  - Personal feed: activities on CIs I'm assigned to or watching
  - Team feed: activities by my team
  - Project feed: all project activities
- **Activity retention:** Configurable retention period (e.g., keep 1 year, archive older)

**Priority:** LOW
**Rationale:** Provides transparency and helps users understand what happened while they were offline. Supports collaboration awareness.

---

**REQ-DB-070: Duplicate Detection Metadata**
Database shall store duplicate detection results:
- **Duplicate candidate table:**
  - Candidate ID (GUID)
  - Entity 1 GUID
  - Entity 2 GUID
  - Similarity score (0-100%)
  - Similarity factors (which attributes match: part number, name, properties)
  - Detection method (exact match, fuzzy match, AI detection)
  - Detection date
  - Reviewed by (user ID)
  - Review decision (confirmed duplicate, not duplicate, deferred)
  - Review date
  - Deduplication action (if merged: which became master, what happened to deprecated)
- **Suppression list:** User-confirmed "not duplicates" to suppress future warnings

**Priority:** MEDIUM
**Rationale:** Prevents duplicate CIs from causing procurement errors and traceability confusion. Tracks duplicate detection decisions.

---

## Documentation Requirements

**REQ-DOC-001: AI Instruction File**
Create AI_INSTRUCTION.md file to guide AI on systems engineering workflow and database mapping.

**Priority:** CRITICAL
**Rationale:** AI needs reference documentation to function correctly.

**Content Requirements:**
- Database schema (tables, columns, types, constraints)
- Entity-to-document mapping rules
- Systems engineering workflow guidance
- Data formatting and validation rules
- Business logic for data insertion
- Traceability rules

---

## Requirements Traceability

### Coverage Summary
- **AI Requirements:** 44 (REQ-AI-001 through REQ-AI-044)
  - AI Behavior: REQ-AI-001 through REQ-AI-009
  - AI Role Definition: REQ-AI-010 through REQ-AI-014
  - AI Document Processing: REQ-AI-015 through REQ-AI-018
  - AI Design Review: REQ-AI-019 through REQ-AI-024
  - AI Modification Behavior: REQ-AI-025 through REQ-AI-027
  - Session Management: REQ-AI-028 through REQ-AI-030
  - Context Awareness: REQ-AI-031
  - Project Initialization: REQ-AI-032 through REQ-AI-037
  - Product Structure & CI Management: REQ-AI-038 through REQ-AI-040
  - Collaborative & Distributed Work: REQ-AI-041 through REQ-AI-044
- **Frontend Requirements:** 23 (REQ-FE-001 through REQ-FE-023)
  - Document Management Interface: REQ-FE-002 through REQ-FE-007
  - User Interface Layout: REQ-FE-008
  - Project Context Display: REQ-FE-009
  - Product Structure & CI Management: REQ-FE-010 through REQ-FE-013
  - Collaborative & Distributed Work: REQ-FE-014 through REQ-FE-023
  - User Input: REQ-FE-001
- **Backend Requirements:** 29 (REQ-BE-001 through REQ-BE-029)
  - Project Structuring: REQ-BE-001 through REQ-BE-004
  - Review and Modification Management: REQ-BE-005 through REQ-BE-011
  - Project Initialization: REQ-BE-012
  - Product Structure & CI Management: REQ-BE-013 through REQ-BE-015
  - Collaborative & Distributed Work: REQ-BE-016 through REQ-BE-029
- **Database Requirements:** 70 (REQ-DB-001 through REQ-DB-070)
  - Schema Structure: REQ-DB-001 through REQ-DB-008
  - Standards Compliance: REQ-DB-009 through REQ-DB-025
  - Workflow Support: REQ-DB-026 through REQ-DB-034
  - Project Context & Standards Mapping: REQ-DB-035 through REQ-DB-036
  - Product Structure & CI Management: REQ-DB-037 through REQ-DB-051
  - Collaborative & Distributed Work: REQ-DB-052 through REQ-DB-070
- **Documentation Requirements:** 1 (REQ-DOC-001)

**Total Requirements:** 167

### Requirements by Source
- **Specification Roleplay (2025-11-15):** 60 requirements
  - Initial session: REQ-AI-001 to REQ-AI-027, REQ-FE-001 to REQ-FE-006, REQ-BE-001 to REQ-BE-010, REQ-DB-001 to REQ-DB-008, REQ-DOC-001
  - Session resumption discussion: REQ-AI-028 to REQ-AI-030, REQ-FE-007, REQ-BE-011, REQ-DB-034
  - UI layout discussion: REQ-FE-008
  - Product development context: REQ-AI-031
- **SQL_requirement.md:** 25 requirements (REQ-DB-009 through REQ-DB-033)
- **Project Initialization Discussion (2025-11-16):** 10 requirements
  - Project initialization workflow: REQ-AI-032 to REQ-AI-037 (6 AI requirements)
  - Frontend context display: REQ-FE-009
  - Backend initialization support: REQ-BE-012
  - Database context storage: REQ-DB-035, REQ-DB-036
- **Product Structure & Configuration Item Management (2025-11-16):** 25 requirements
  - AI capabilities: REQ-AI-038 to REQ-AI-040 (product structure extraction, item data extraction, CI classification)
  - Frontend interfaces: REQ-FE-010 to REQ-FE-013 (product structure tree, BOM editor, item management, CI table)
  - Backend operations: REQ-BE-013 to REQ-BE-015 (BOM management, item lifecycle, change impact analysis)
  - Database schema: REQ-DB-037 to REQ-DB-051 (product breakdown, item master, supplier, part numbers, serial/lot tracking, BOM, procurement, configuration, traceability, CI types, baseline/control, verification/certification, change history, safety/security, data rights/export control)
  - Reference: docs/Level_2_User_Framework/CONFIGURATION_ITEM_MANAGEMENT.md
- **Collaborative & Distributed Work (2025-11-16):** 47 requirements
  - AI capabilities: REQ-AI-041 to REQ-AI-044 (AI-assisted merge conflict resolution, duplicate detection, change impact notifications, access control recommendations)
  - Frontend interfaces: REQ-FE-014 to REQ-FE-023 (check-out/check-in, merge review, conflict resolution UI, work assignment view, notifications center, comments/discussions, access control management, merge preview, activity feed, lock status indicators)
  - Backend operations: REQ-BE-016 to REQ-BE-029 (concurrent access control/locking, optimistic conflict detection, work assignment, data export/import, intelligent merge engine, merge preview/rollback, notifications, RBAC enforcement, session management, ID mapping, duplicate detection, instance tracking)
  - Database schema: REQ-DB-052 to REQ-DB-070 (hybrid identifier system, session management, lock management, work assignment, RBAC, team permissions, CI-level permissions, comments, notifications, merge metadata, source instance tracking, ID mapping, merge conflicts, merge rollback, enhanced audit trail, external references, data sharing agreements, activity log, duplicate detection)
  - User Requirements: Q1=C (both concurrent & distributed), Q2=All scenarios, Q3=Milestone-based, Q4=Semi-automatic, Q5=Hybrid IDs, Q6=Complex access control

---

## Next Steps

1. Continue specification roleplay to identify additional requirements
2. Create AI_INSTRUCTION.md based on REQ-DOC-001
3. Validate requirements against existing database schema (42 tables)
4. Identify database schema gaps based on new requirements
5. Design frontend mockups for document management interface
6. Create detailed design for backend document aggregation logic
7. Define protected field list for REQ-AI-027 and REQ-DB-006

---

## Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-16 | 0.8.0 | **CRITICAL ARCHITECTURE UPDATE:** Added 47 Collaborative & Distributed Work requirements to support multi-user concurrent access AND multi-instance distributed development with milestone-based merges. **AI:** Semi-automatic merge conflict resolution with human approval, duplicate CI detection, intelligent change notifications, access control recommendations (REQ-AI-041 to REQ-AI-044). **Frontend:** Check-out/check-in workflow, comprehensive merge review interface with 3-panel comparison, conflict resolution UI, work assignment views, notifications center, comments/discussions, RBAC management interface, merge preview with impact analysis, activity feeds, real-time lock indicators (REQ-FE-014 to REQ-FE-023). **Backend:** Pessimistic locking with timeout, optimistic conflict detection, work assignment/partitioning, data export/import for federation, intelligent merge engine with 5 conflict types, merge preview/rollback, notification engine, RBAC enforcement with 7 role types, multi-user session management, ID mapping for collision resolution, duplicate detection algorithms, instance tracking (REQ-BE-016 to REQ-BE-029). **Database:** Hybrid identifier system (GUID + display ID), session management, lock management with deadlock prevention, work assignment, RBAC with team-based permissions, CI-level ACL, comments/discussions, notifications/subscriptions, comprehensive merge metadata, source instance tracking, ID mapping table, merge conflict storage, rollback support, enhanced multi-instance audit trail, external references, data sharing agreements, activity log, duplicate detection metadata (REQ-DB-052 to REQ-DB-070). Supports: Q1-C (both concurrent & distributed), Q2-All scenarios, Q3-Milestone merges, Q4-Semi-automatic, Q5-Hybrid IDs, Q6-Complex access control. Total requirements: 167. |
| 2025-11-16 | 0.7.0 | **MAJOR UPDATE:** Added 25 Product Structure & Configuration Item (CI) Management requirements. Database shall support comprehensive CI management with 34+ fields including product breakdown structure, item master data, supplier management, part numbers, serial/lot tracking, BOM, procurement data, configuration control (5 levels), baseline management, verification/certification status, change history, deviation tracking, safety/security classification, and data rights/export control (REQ-DB-037 to REQ-DB-051). Frontend shall provide product structure tree, BOM editor, item management interface, and CI table view (REQ-FE-010 to REQ-FE-013). Backend shall support BOM operations, item lifecycle, and change impact analysis (REQ-BE-013 to REQ-BE-015). AI shall extract product structure and item data from documents and suggest CI classifications (REQ-AI-038 to REQ-AI-040). Created CONFIGURATION_ITEM_MANAGEMENT.md reference document. Total requirements: 120. |
| 2025-11-16 | 0.6.0 | **MAJOR UPDATE:** Added 10 project initialization requirements. AI shall conduct structured project initialization interview to determine safety criticality, DAL/SIL, regulatory requirements, and applicable standards (REQ-AI-032 to REQ-AI-037). Frontend shall display project context (REQ-FE-009). Backend shall support initialization workflow (REQ-BE-012). Database shall store project context and standards mapping (REQ-DB-035, REQ-DB-036). Updated REQ-AI-009 to clarify initial question followed by structured interview. Total requirements: 95. |
| 2025-11-15 | 0.5.0 | Added REQ-AI-031 (Product Development Context Awareness - AI shall consult PROJECT_PLAN.md for development phase context). Total requirements: 85. |
| 2025-11-15 | 0.4.0 | Added REQ-FE-008 (Dual Interface Layout with AI Proposal Field + Dialogue Field). Total requirements: 84. Roleplay session completed. |
| 2025-11-15 | 0.3.0 | Added 6 session management requirements from roleplay discussion: REQ-AI-028 to REQ-AI-030 (session context recovery, resume patterns, conditional flows), REQ-FE-007 (project status dashboard), REQ-BE-011 (session state management), REQ-DB-034 (project status storage). Total requirements: 83. |
| 2025-11-15 | 0.2.0 | Integrated 25 database requirements from SQL_requirement.md (REQ-DB-009 through REQ-DB-033). Total requirements: 77. Added standards compliance (ARP4754/DO-178C/DO-254) and workflow support requirements. |
| 2025-11-15 | 0.1.0 | Initial requirements capture from specification roleplay (52 requirements) |

---

## Approval

**Status:** Draft - Pending Review
**Next Review:** After next roleplay session
**Approved By:** TBD
