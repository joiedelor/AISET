"""
State Machine Generator for AISET Process Engine

This module instantiates state machines for Configuration Items (CIs) based on
process templates. Each CI gets a state machine instance appropriate for its type.

The key insight: AISET-AI is a rigorous process executor, not an intelligent
decision-maker. This generator creates deterministic state machines from templates.
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel


# =============================================================================
# ENUMS
# =============================================================================

class CIType(str, Enum):
    """Configuration Item types with associated process templates"""
    SYSTEM = "SYSTEM"
    SUBSYSTEM = "SUBSYSTEM"
    EQUIPMENT = "EQUIPMENT"
    SOFTWARE = "SOFTWARE"
    HARDWARE = "HARDWARE"
    ASSEMBLY = "ASSEMBLY"
    COMPONENT = "COMPONENT"
    PART = "PART"
    DOCUMENT = "DOCUMENT"
    PHYSICAL_PRODUCT = "PHYSICAL_PRODUCT"


class PhaseStatus(str, Enum):
    """Status of a phase in a state machine instance"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class SubPhaseStatus(str, Enum):
    """Status of a sub-phase"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class ActivityStatus(str, Enum):
    """Status of an activity"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class ActivityInstance:
    """Runtime instance of an activity"""
    activity_id: str
    name: str
    activity_type: str
    status: ActivityStatus = ActivityStatus.NOT_STARTED
    required: bool = True
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output_artifacts: List[str] = field(default_factory=list)
    completion_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubPhaseInstance:
    """Runtime instance of a sub-phase"""
    sub_phase_id: str
    name: str
    order: int
    status: SubPhaseStatus = SubPhaseStatus.NOT_STARTED
    activities: List[ActivityInstance] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_activity_index: int = 0


@dataclass
class PhaseInstance:
    """Runtime instance of a phase"""
    phase_id: str
    name: str
    order: int
    status: PhaseStatus = PhaseStatus.NOT_STARTED
    sub_phases: List[SubPhaseInstance] = field(default_factory=list)
    deliverables: List[Dict] = field(default_factory=list)
    reviews: List[Dict] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_sub_phase_index: int = 0
    entry_criteria_met: bool = False
    exit_criteria_met: bool = False


@dataclass
class StateMachineInstance:
    """
    A complete state machine instance for a Configuration Item.
    This is the runtime representation of a process template.
    """
    instance_id: str
    ci_id: int
    ci_type: CIType
    template_id: str
    template_name: str
    dal_level: Optional[str] = None

    # Phases
    phases: List[PhaseInstance] = field(default_factory=list)
    current_phase_index: int = 0

    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Context for conditional logic
    context: Dict[str, Any] = field(default_factory=dict)

    @property
    def current_phase(self) -> Optional[PhaseInstance]:
        if 0 <= self.current_phase_index < len(self.phases):
            return self.phases[self.current_phase_index]
        return None

    @property
    def overall_progress(self) -> float:
        """Calculate overall progress percentage"""
        if not self.phases:
            return 0.0
        completed = sum(1 for p in self.phases if p.status == PhaseStatus.COMPLETED)
        return (completed / len(self.phases)) * 100

    def to_dict(self) -> Dict:
        """Serialize to dictionary for database storage"""
        return {
            "instance_id": self.instance_id,
            "ci_id": self.ci_id,
            "ci_type": self.ci_type.value,
            "template_id": self.template_id,
            "template_name": self.template_name,
            "dal_level": self.dal_level,
            "current_phase_index": self.current_phase_index,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "context": self.context,
            "phases": [self._phase_to_dict(p) for p in self.phases]
        }

    def _phase_to_dict(self, phase: PhaseInstance) -> Dict:
        return {
            "phase_id": phase.phase_id,
            "name": phase.name,
            "order": phase.order,
            "status": phase.status.value,
            "current_sub_phase_index": phase.current_sub_phase_index,
            "entry_criteria_met": phase.entry_criteria_met,
            "exit_criteria_met": phase.exit_criteria_met,
            "started_at": phase.started_at.isoformat() if phase.started_at else None,
            "completed_at": phase.completed_at.isoformat() if phase.completed_at else None,
            "sub_phases": [self._sub_phase_to_dict(sp) for sp in phase.sub_phases],
            "deliverables": phase.deliverables,
            "reviews": phase.reviews
        }

    def _sub_phase_to_dict(self, sub_phase: SubPhaseInstance) -> Dict:
        return {
            "sub_phase_id": sub_phase.sub_phase_id,
            "name": sub_phase.name,
            "order": sub_phase.order,
            "status": sub_phase.status.value,
            "current_activity_index": sub_phase.current_activity_index,
            "started_at": sub_phase.started_at.isoformat() if sub_phase.started_at else None,
            "completed_at": sub_phase.completed_at.isoformat() if sub_phase.completed_at else None,
            "activities": [self._activity_to_dict(a) for a in sub_phase.activities]
        }

    def _activity_to_dict(self, activity: ActivityInstance) -> Dict:
        return {
            "activity_id": activity.activity_id,
            "name": activity.name,
            "activity_type": activity.activity_type,
            "status": activity.status.value,
            "required": activity.required,
            "started_at": activity.started_at.isoformat() if activity.started_at else None,
            "completed_at": activity.completed_at.isoformat() if activity.completed_at else None,
            "output_artifacts": activity.output_artifacts,
            "completion_data": activity.completion_data
        }


# =============================================================================
# TEMPLATE LOADER
# =============================================================================

class ProcessTemplateLoader:
    """
    Loads process templates from JSON files.
    """

    TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

    # Mapping from CI type to template file
    CI_TYPE_TO_TEMPLATE = {
        CIType.SYSTEM: "arp4754a_system_process.json",
        CIType.SUBSYSTEM: "arp4754a_system_process.json",
        CIType.EQUIPMENT: "arp4754a_system_process.json",
        CIType.SOFTWARE: "do178c_software_process.json",
        CIType.HARDWARE: "do254_hardware_process.json",
        CIType.ASSEMBLY: "product_development_process.json",
        CIType.PHYSICAL_PRODUCT: "product_development_process.json",
        CIType.COMPONENT: "component_part_process.json",
        CIType.PART: "component_part_process.json",
    }

    _template_cache: Dict[str, Dict] = {}

    @classmethod
    def load_template(cls, template_id: str) -> Dict:
        """Load a template by its ID"""
        if template_id in cls._template_cache:
            return cls._template_cache[template_id]

        # Search all template files
        for template_file in cls.TEMPLATES_DIR.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    template = json.load(f)
                    if template.get("template_id") == template_id:
                        cls._template_cache[template_id] = template
                        return template
            except json.JSONDecodeError:
                continue

        raise ValueError(f"Template '{template_id}' not found")

    @classmethod
    def load_template_for_ci_type(cls, ci_type: CIType) -> Dict:
        """Load the appropriate template for a CI type"""
        template_file = cls.CI_TYPE_TO_TEMPLATE.get(ci_type)
        if not template_file:
            raise ValueError(f"No template defined for CI type '{ci_type}'")

        template_path = cls.TEMPLATES_DIR / template_file
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        with open(template_path, 'r') as f:
            template = json.load(f)

        cls._template_cache[template["template_id"]] = template
        return template

    @classmethod
    def list_available_templates(cls) -> List[Dict]:
        """List all available templates with summary info"""
        templates = []
        for template_file in cls.TEMPLATES_DIR.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    template = json.load(f)
                    templates.append({
                        "template_id": template.get("template_id"),
                        "name": template.get("name"),
                        "standard": template.get("standard"),
                        "applicable_ci_types": template.get("applicable_ci_types", []),
                        "phase_count": len(template.get("phases", []))
                    })
            except (json.JSONDecodeError, KeyError):
                continue
        return templates


# =============================================================================
# STATE MACHINE GENERATOR
# =============================================================================

class StateMachineGenerator:
    """
    Generates state machine instances from process templates.

    This is the core of the "Codification of the Systems Engineer" -
    it creates deterministic, executable process instances.
    """

    def __init__(self):
        self.loader = ProcessTemplateLoader()

    def generate_for_ci(
        self,
        ci_id: int,
        ci_type: CIType,
        dal_level: Optional[str] = None,
        template_id: Optional[str] = None
    ) -> StateMachineInstance:
        """
        Generate a state machine instance for a Configuration Item.

        Args:
            ci_id: The database ID of the CI
            ci_type: The type of CI (determines which template to use)
            dal_level: Optional DAL/SIL level (affects which activities are required)
            template_id: Optional specific template ID (overrides ci_type default)

        Returns:
            A fully initialized StateMachineInstance
        """
        # Load template
        if template_id:
            template = self.loader.load_template(template_id)
        else:
            template = self.loader.load_template_for_ci_type(ci_type)

        # Create instance
        instance = StateMachineInstance(
            instance_id=str(uuid.uuid4()),
            ci_id=ci_id,
            ci_type=ci_type,
            template_id=template["template_id"],
            template_name=template["name"],
            dal_level=dal_level
        )

        # Generate phases from template
        instance.phases = self._generate_phases(template, dal_level)

        return instance

    def _generate_phases(self, template: Dict, dal_level: Optional[str]) -> List[PhaseInstance]:
        """Generate phase instances from template"""
        phases = []

        for phase_def in template.get("phases", []):
            phase = PhaseInstance(
                phase_id=phase_def["phase_id"],
                name=phase_def["name"],
                order=phase_def["order"],
                deliverables=phase_def.get("deliverables", []),
                reviews=phase_def.get("reviews", [])
            )

            # Generate sub-phases
            phase.sub_phases = self._generate_sub_phases(
                phase_def.get("sub_phases", []),
                dal_level
            )

            # Filter deliverables by DAL if specified
            if dal_level:
                phase.deliverables = [
                    d for d in phase.deliverables
                    if self._is_required_for_dal(d, dal_level)
                ]

            phases.append(phase)

        return phases

    def _generate_sub_phases(
        self,
        sub_phase_defs: List[Dict],
        dal_level: Optional[str]
    ) -> List[SubPhaseInstance]:
        """Generate sub-phase instances"""
        sub_phases = []

        for sp_def in sub_phase_defs:
            sub_phase = SubPhaseInstance(
                sub_phase_id=sp_def["sub_phase_id"],
                name=sp_def["name"],
                order=sp_def["order"]
            )

            # Generate activities
            sub_phase.activities = self._generate_activities(
                sp_def.get("activities", []),
                dal_level
            )

            sub_phases.append(sub_phase)

        return sub_phases

    def _generate_activities(
        self,
        activity_defs: List[Dict],
        dal_level: Optional[str]
    ) -> List[ActivityInstance]:
        """Generate activity instances, filtering by DAL level"""
        activities = []

        for act_def in activity_defs:
            # Check if activity is required for this DAL level
            if not self._is_required_for_dal(act_def, dal_level):
                continue

            activity = ActivityInstance(
                activity_id=act_def["activity_id"],
                name=act_def["name"],
                activity_type=act_def["type"],
                required=act_def.get("required", True),
                output_artifacts=act_def.get("output_artifacts", [])
            )

            activities.append(activity)

        return activities

    def _is_required_for_dal(self, item: Dict, dal_level: Optional[str]) -> bool:
        """Check if an item is required for the given DAL level"""
        dal_required = item.get("dal_required")

        # If no DAL restriction, item is always required
        if not dal_required:
            return True

        # If no DAL level specified, include all items
        if not dal_level:
            return True

        # Check if current DAL is in the required list
        return dal_level in dal_required

    def generate_for_product_structure(
        self,
        product_structure: List[Dict]
    ) -> Dict[int, StateMachineInstance]:
        """
        Generate state machines for an entire product structure.

        Args:
            product_structure: List of CI dictionaries with id, type, dal_level

        Returns:
            Dictionary mapping CI ID to StateMachineInstance
        """
        instances = {}

        for ci in product_structure:
            ci_id = ci["id"]
            ci_type = CIType(ci["type"])
            dal_level = ci.get("dal_level")

            instance = self.generate_for_ci(ci_id, ci_type, dal_level)
            instances[ci_id] = instance

        return instances


# =============================================================================
# STATE MACHINE CONTROLLER
# =============================================================================

class StateMachineController:
    """
    Controls the execution of a state machine instance.

    This is the "process executor" that manages state transitions,
    activity completion, and phase progression.
    """

    def __init__(self, instance: StateMachineInstance):
        self.instance = instance

    def get_current_activity(self) -> Optional[ActivityInstance]:
        """Get the current activity to work on"""
        phase = self.instance.current_phase
        if not phase or phase.status == PhaseStatus.COMPLETED:
            return None

        if phase.current_sub_phase_index >= len(phase.sub_phases):
            return None

        sub_phase = phase.sub_phases[phase.current_sub_phase_index]
        if sub_phase.current_activity_index >= len(sub_phase.activities):
            return None

        return sub_phase.activities[sub_phase.current_activity_index]

    def start_phase(self, phase_index: int = None) -> bool:
        """Start a phase (checks entry criteria)"""
        if phase_index is None:
            phase_index = self.instance.current_phase_index

        if phase_index >= len(self.instance.phases):
            return False

        phase = self.instance.phases[phase_index]

        # Check entry criteria
        if not self._check_entry_criteria(phase):
            phase.status = PhaseStatus.BLOCKED
            return False

        phase.status = PhaseStatus.IN_PROGRESS
        phase.started_at = datetime.utcnow()
        phase.entry_criteria_met = True

        # Start first sub-phase
        if phase.sub_phases:
            self._start_sub_phase(phase.sub_phases[0])

        self.instance.updated_at = datetime.utcnow()
        return True

    def complete_activity(
        self,
        activity_id: str,
        completion_data: Dict = None
    ) -> bool:
        """Mark an activity as complete and advance state"""
        phase = self.instance.current_phase
        if not phase:
            return False

        sub_phase = phase.sub_phases[phase.current_sub_phase_index]
        activity = sub_phase.activities[sub_phase.current_activity_index]

        if activity.activity_id != activity_id:
            return False

        # Complete the activity
        activity.status = ActivityStatus.COMPLETED
        activity.completed_at = datetime.utcnow()
        if completion_data:
            activity.completion_data = completion_data

        # Advance to next activity or sub-phase
        self._advance_state()

        self.instance.updated_at = datetime.utcnow()
        return True

    def skip_activity(self, activity_id: str, reason: str = None) -> bool:
        """Skip an optional activity"""
        phase = self.instance.current_phase
        if not phase:
            return False

        sub_phase = phase.sub_phases[phase.current_sub_phase_index]
        activity = sub_phase.activities[sub_phase.current_activity_index]

        if activity.activity_id != activity_id:
            return False

        if activity.required:
            return False  # Cannot skip required activities

        activity.status = ActivityStatus.SKIPPED
        activity.completion_data = {"skip_reason": reason}

        self._advance_state()
        self.instance.updated_at = datetime.utcnow()
        return True

    def get_phase_progress(self, phase_index: int = None) -> Dict:
        """Get progress information for a phase"""
        if phase_index is None:
            phase_index = self.instance.current_phase_index

        phase = self.instance.phases[phase_index]

        total_activities = 0
        completed_activities = 0

        for sp in phase.sub_phases:
            for act in sp.activities:
                total_activities += 1
                if act.status in [ActivityStatus.COMPLETED, ActivityStatus.SKIPPED]:
                    completed_activities += 1

        return {
            "phase_id": phase.phase_id,
            "phase_name": phase.name,
            "status": phase.status.value,
            "total_activities": total_activities,
            "completed_activities": completed_activities,
            "progress_percent": (completed_activities / total_activities * 100) if total_activities > 0 else 0,
            "current_sub_phase": phase.sub_phases[phase.current_sub_phase_index].name if phase.sub_phases else None
        }

    def get_overall_progress(self) -> Dict:
        """Get overall progress across all phases"""
        phase_progress = [self.get_phase_progress(i) for i in range(len(self.instance.phases))]

        return {
            "instance_id": self.instance.instance_id,
            "ci_id": self.instance.ci_id,
            "template_name": self.instance.template_name,
            "current_phase_index": self.instance.current_phase_index,
            "overall_progress": self.instance.overall_progress,
            "phases": phase_progress
        }

    def _advance_state(self):
        """Advance to the next activity, sub-phase, or phase"""
        phase = self.instance.current_phase
        sub_phase = phase.sub_phases[phase.current_sub_phase_index]

        # Try next activity
        if sub_phase.current_activity_index < len(sub_phase.activities) - 1:
            sub_phase.current_activity_index += 1
            return

        # Sub-phase complete, try next sub-phase
        sub_phase.status = SubPhaseStatus.COMPLETED
        sub_phase.completed_at = datetime.utcnow()

        if phase.current_sub_phase_index < len(phase.sub_phases) - 1:
            phase.current_sub_phase_index += 1
            self._start_sub_phase(phase.sub_phases[phase.current_sub_phase_index])
            return

        # Phase complete, check exit criteria
        if self._check_exit_criteria(phase):
            phase.status = PhaseStatus.COMPLETED
            phase.completed_at = datetime.utcnow()
            phase.exit_criteria_met = True

            # Try next phase
            if self.instance.current_phase_index < len(self.instance.phases) - 1:
                self.instance.current_phase_index += 1
                self.start_phase()

    def _start_sub_phase(self, sub_phase: SubPhaseInstance):
        """Start a sub-phase"""
        sub_phase.status = SubPhaseStatus.IN_PROGRESS
        sub_phase.started_at = datetime.utcnow()
        sub_phase.current_activity_index = 0

        # Start first activity
        if sub_phase.activities:
            sub_phase.activities[0].status = ActivityStatus.IN_PROGRESS
            sub_phase.activities[0].started_at = datetime.utcnow()

    def _check_entry_criteria(self, phase: PhaseInstance) -> bool:
        """Check if entry criteria for a phase are met"""
        # For now, always return True
        # TODO: Implement actual criteria checking
        return True

    def _check_exit_criteria(self, phase: PhaseInstance) -> bool:
        """Check if exit criteria for a phase are met"""
        # Check all required activities are complete
        for sp in phase.sub_phases:
            for act in sp.activities:
                if act.required and act.status not in [ActivityStatus.COMPLETED, ActivityStatus.SKIPPED]:
                    return False
        return True


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_state_machine_for_ci(
    ci_id: int,
    ci_type: str,
    dal_level: str = None
) -> StateMachineInstance:
    """
    Convenience function to create a state machine for a CI.

    Args:
        ci_id: Database ID of the CI
        ci_type: Type of CI as string
        dal_level: Optional DAL/SIL level

    Returns:
        A new StateMachineInstance
    """
    generator = StateMachineGenerator()
    return generator.generate_for_ci(
        ci_id=ci_id,
        ci_type=CIType(ci_type),
        dal_level=dal_level
    )


def list_available_processes() -> List[Dict]:
    """List all available process templates"""
    return ProcessTemplateLoader.list_available_templates()


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Example: Generate state machines for a simple product structure

    print("Available Process Templates:")
    print("-" * 40)
    for template in list_available_processes():
        print(f"  {template['template_id']}: {template['name']}")
        print(f"    Standard: {template['standard']}")
        print(f"    CI Types: {', '.join(template['applicable_ci_types'])}")
        print(f"    Phases: {template['phase_count']}")
        print()

    # Create a state machine for a software component
    print("\nCreating State Machine for Software (DAL-B):")
    print("-" * 40)

    sm = create_state_machine_for_ci(
        ci_id=1,
        ci_type="SOFTWARE",
        dal_level="DAL_B"
    )

    print(f"Instance ID: {sm.instance_id}")
    print(f"Template: {sm.template_name}")
    print(f"Phases: {len(sm.phases)}")

    for phase in sm.phases:
        print(f"  Phase {phase.order}: {phase.name}")
        print(f"    Sub-phases: {len(phase.sub_phases)}")
        activity_count = sum(len(sp.activities) for sp in phase.sub_phases)
        print(f"    Activities: {activity_count}")

    # Test the controller
    print("\nTesting State Machine Controller:")
    print("-" * 40)

    controller = StateMachineController(sm)
    controller.start_phase(0)

    progress = controller.get_overall_progress()
    print(f"Overall Progress: {progress['overall_progress']:.1f}%")
    print(f"Current Phase: {progress['phases'][0]['phase_name']}")

    current = controller.get_current_activity()
    if current:
        print(f"Current Activity: {current.name} ({current.activity_type})")
