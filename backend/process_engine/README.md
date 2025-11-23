# AISET Process Engine

**Version:** 1.0.0
**Date:** 2025-11-23

## Overview

The Process Engine is the core of AISET's **"Codification of the Systems Engineer"**. It provides deterministic, executable development processes based on industry standards.

### Key Insight

> **AISET-AI is NOT an intelligent decision-maker. It is a rigorous process executor.**

The "intelligence" consists of:
1. Asking the RIGHT question at the RIGHT time (following predefined scripts)
2. Listening and capturing what the human says
3. Structuring/organizing captured data according to standards
4. Maintaining configuration - IDs, versions, traceability links
5. Never forgetting - persistent, complete, consistent records

**The HUMAN does:**
- All creative work (design decisions, architecture choices)
- All technical judgment (safety analysis, trade-offs)
- All approvals (nothing auto-committed)

## Directory Structure

```
backend/process_engine/
├── __init__.py                  # Package exports
├── README.md                    # This file
├── schemas/
│   ├── process_template_schema.json  # JSON Schema for templates
│   └── process_engine_ddl.sql        # Database schema
├── services/
│   └── state_machine_generator.py    # Core state machine logic
└── templates/
    ├── arp4754a_system_process.json  # ARP4754A (10 phases)
    ├── do178c_software_process.json  # DO-178C Software
    ├── do254_hardware_process.json   # DO-254 Hardware
    ├── product_development_process.json  # Physical products
    └── component_part_process.json   # Components/Parts
```

## Process Templates

### Available Templates

| Template | Standard | CI Types | Phases |
|----------|----------|----------|--------|
| ARP4754A_SYSTEM_V1 | ARP4754A | System, Subsystem, Equipment | 10 |
| DO178C_SOFTWARE_V1 | DO-178C | Software | 9 |
| DO254_HARDWARE_V1 | DO-254 | Hardware | 8 |
| PRODUCT_DEV_V1 | Generic | Physical Product, Assembly | 7 |
| COMPONENT_PART_V1 | Generic | Component, Part | 5 |

### Template Structure

Each template defines:
- **Phases**: Major development stages
- **Sub-Phases**: Activities within phases
- **Activities**: Individual work items
- **Deliverables**: Required outputs
- **Reviews**: Required gates/reviews
- **Entry/Exit Criteria**: Phase transition conditions

### Mapping CI Type to Process

```
PRODUCT
├── PHYSICAL_PART → product_development_process.json
│   ├── Component → component_part_process.json
│   │   ├── Part → component_part_process.json
│   │   └── Part → component_part_process.json
│   └── Component → component_part_process.json
│
└── SYSTEMS → arp4754a_system_process.json
    ├── System → arp4754a_system_process.json
    │   ├── Equipment → arp4754a_system_process.json
    │   │   ├── Hardware → do254_hardware_process.json
    │   │   └── Software → do178c_software_process.json
    │   └── Application SW → do178c_software_process.json
    └── System → arp4754a_system_process.json
```

## Usage

### Create a State Machine for a CI

```python
from backend.process_engine import create_state_machine_for_ci, StateMachineController

# Generate state machine for software at DAL-B
sm = create_state_machine_for_ci(
    ci_id=123,
    ci_type="SOFTWARE",
    dal_level="DAL_B"
)

# Create controller
controller = StateMachineController(sm)

# Start first phase
controller.start_phase(0)

# Get current activity
activity = controller.get_current_activity()
print(f"Current: {activity.name} ({activity.activity_type})")

# Complete activity
controller.complete_activity(activity.activity_id, {"result": "done"})

# Check progress
progress = controller.get_overall_progress()
print(f"Progress: {progress['overall_progress']:.1f}%")
```

### List Available Templates

```python
from backend.process_engine import list_available_processes

for template in list_available_processes():
    print(f"{template['template_id']}: {template['name']}")
    print(f"  Standard: {template['standard']}")
    print(f"  Phases: {template['phase_count']}")
```

### Generate for Product Structure

```python
from backend.process_engine import StateMachineGenerator

generator = StateMachineGenerator()

# Define product structure
product_structure = [
    {"id": 1, "type": "SYSTEM", "dal_level": "DAL_B"},
    {"id": 2, "type": "SOFTWARE", "dal_level": "DAL_B"},
    {"id": 3, "type": "HARDWARE", "dal_level": "DAL_C"},
    {"id": 4, "type": "ASSEMBLY", "dal_level": None},
]

# Generate state machines for all CIs
instances = generator.generate_for_product_structure(product_structure)

for ci_id, sm in instances.items():
    print(f"CI {ci_id}: {sm.template_name} ({len(sm.phases)} phases)")
```

## Database Schema

The process engine uses these tables:

| Table | Purpose |
|-------|---------|
| `process_templates` | Store template definitions |
| `ci_state_machines` | State machine instances per CI |
| `ci_phase_instances` | Phase tracking |
| `ci_activity_instances` | Activity tracking |
| `interview_answers` | Captured interview data |
| `generated_documents` | Generated documents |
| `phase_deliverables` | Deliverable tracking |
| `phase_reviews` | Review/gate tracking |
| `state_machine_history` | Audit trail |

### Apply Schema

```bash
cd backend
PGPASSWORD="your_password" psql -h localhost -U aiset_user -d aiset_db \
    -f process_engine/schemas/process_engine_ddl.sql
```

## DAL/SIL Level Filtering

Activities and deliverables can be filtered by DAL level:

```json
{
  "activity_id": "ACT_MCDC_COV",
  "name": "MC/DC Coverage Analysis",
  "type": "ANALYSIS",
  "required": true,
  "dal_required": ["DAL_A"]  // Only required for DAL-A
}
```

When generating a state machine with `dal_level="DAL_B"`, activities marked as `dal_required: ["DAL_A"]` will be excluded.

## Testing Without AI

The Process Engine works **completely without AI**:

1. Questions come from hardcoded interview scripts
2. State transitions are deterministic
3. Data validation is rule-based
4. Document generation uses templates

AI is OPTIONAL - only used for:
- Rephrasing questions naturally
- Interpreting free-text answers
- Generating user-friendly error messages

To test without AI, simply don't configure an AI provider. The system will use script questions directly.

## Related Documents

- **Requirements:** `02_REQUIREMENTS/SRS_Process_Engine_Requirements.md`
- **Design:** `03_DESIGN/HLD_Process_Engine_Architecture.md`
- **Main SRS:** `02_REQUIREMENTS/SRS_Software_Requirements_Specification.md` (v1.3.0)
- **Main HLD:** `03_DESIGN/HLD_High_Level_Design.md` (v1.3.0)

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2025-11-23 | Initial creation |
