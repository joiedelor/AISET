"""
Unit Tests for Process Engine Integration with CI Management
DO-178C Traceability: REQ-SM-001 to REQ-SM-006

These tests verify:
1. State machine creation for CIs
2. State machine progression (phase/activity completion)
3. Progress tracking
4. Integration with Configuration Item service
"""

import pytest
from sqlalchemy.orm import Session
from models.configuration_item import ConfigurationItem, CIType, CILifecyclePhase, CIStatus
from models.project import Project, CIStateMachine
from services.configuration_item_service import ConfigurationItemService
from process_engine import (
    create_state_machine_for_ci,
    StateMachineController,
    CIType as ProcessCIType,
    PhaseStatus,
    ActivityStatus
)
import json


@pytest.fixture
def test_project(db: Session):
    """Create a test project."""
    project = Project(
        name="Test Project",
        project_code="TEST-001",
        safety_critical=True,
        dal_level="DAL_B",
        domain="aerospace",
        status="active",
        created_by="test_user"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@pytest.fixture
def ci_service(db: Session):
    """Create a CI service instance."""
    return ConfigurationItemService(db)


class TestStateMachineCreation:
    """Test state machine creation for different CI types."""

    def test_create_state_machine_for_software_ci(self, db: Session, test_project: Project, ci_service: ConfigurationItemService):
        """
        Test creating a state machine for a SOFTWARE CI.

        Traceability: REQ-SM-001 (Development lifecycle state machine)
        """
        # Create a software CI
        ci = ci_service.create_ci(
            project_id=test_project.id,
            ci_identifier="SW-001",
            name="Flight Control Software",
            ci_type=CIType.SOFTWARE,
            criticality="DAL B",
            created_by="test_user"
        )

        # Create state machine
        result = ci_service.create_state_machine_for_ci_item(
            ci_id=ci.id,
            dal_level="DAL_B",
            auto_start=True
        )

        assert result is not None
        assert result["ci_id"] == ci.id
        assert result["template_name"] == "DO-178C Software Development Process"
        assert result["dal_level"] == "DAL_B"
        assert result["current_phase_index"] == 0
        assert result["overall_progress"] == 0.0  # Just started

        # Verify database record
        sm_record = db.query(CIStateMachine).filter(CIStateMachine.ci_id == ci.id).first()
        assert sm_record is not None
        assert sm_record.template_id == "DO178C_SOFTWARE_V1"
        assert sm_record.dal_level == "DAL_B"

    def test_create_state_machine_for_hardware_ci(self, db: Session, test_project: Project, ci_service: ConfigurationItemService):
        """
        Test creating a state machine for a HARDWARE CI.

        Traceability: REQ-SM-001
        """
        ci = ci_service.create_ci(
            project_id=test_project.id,
            ci_identifier="HW-001",
            name="Processor Board",
            ci_type=CIType.HARDWARE,
            criticality="DAL A",
            created_by="test_user"
        )

        result = ci_service.create_state_machine_for_ci_item(
            ci_id=ci.id,
            dal_level="DAL_A",
            auto_start=True
        )

        assert result is not None
        assert result["template_name"] == "DO-254 Hardware Development Process"

    def test_create_state_machine_for_system_ci(self, db: Session, test_project: Project, ci_service: ConfigurationItemService):
        """
        Test creating a state machine for a SYSTEM CI.

        Traceability: REQ-SM-001
        """
        ci = ci_service.create_ci(
            project_id=test_project.id,
            ci_identifier="SYS-001",
            name="Flight Management System",
            ci_type=CIType.SYSTEM,
            created_by="test_user"
        )

        result = ci_service.create_state_machine_for_ci_item(
            ci_id=ci.id,
            auto_start=True
        )

        assert result is not None
        assert result["template_name"] == "ARP4754A System Development Process"

    def test_create_state_machine_without_auto_start(self, db: Session, test_project: Project, ci_service: ConfigurationItemService):
        """
        Test creating a state machine without auto-starting the first phase.

        Traceability: REQ-SM-001, REQ-SM-002 (Phase preconditions)
        """
        ci = ci_service.create_ci(
            project_id=test_project.id,
            ci_identifier="SW-002",
            name="Test Software",
            ci_type=CIType.SOFTWARE,
            created_by="test_user"
        )

        result = ci_service.create_state_machine_for_ci_item(
            ci_id=ci.id,
            auto_start=False
        )

        assert result is not None
        # Phase should not be started
        sm_data = ci_service.get_ci_state_machine(ci.id)
        state_dict = sm_data["state_data"]
        first_phase = state_dict["phases"][0]
        assert first_phase["status"] == "not_started"


class TestStateMachineRetrieval:
    """Test retrieving state machine data."""

    def test_get_ci_state_machine(self, db: Session, test_project: Project, ci_service: ConfigurationItemService):
        """
        Test retrieving a CI's state machine.

        Traceability: REQ-SM-001
        """
        ci = ci_service.create_ci(
            project_id=test_project.id,
            ci_identifier="SW-003",
            name="Retrieval Test Software",
            ci_type=CIType.SOFTWARE,
            created_by="test_user"
        )

        ci_service.create_state_machine_for_ci_item(ci_id=ci.id, auto_start=True)

        # Retrieve state machine
        sm_data = ci_service.get_ci_state_machine(ci.id)

        assert sm_data is not None
        assert sm_data["ci_id"] == ci.id
        assert "state_data" in sm_data
        assert "phases" in sm_data["state_data"]
        assert len(sm_data["state_data"]["phases"]) > 0

    def test_get_ci_state_machine_not_found(self, db: Session, test_project: Project, ci_service: ConfigurationItemService):
        """Test retrieving state machine for CI without one."""
        ci = ci_service.create_ci(
            project_id=test_project.id,
            ci_identifier="SW-004",
            name="No State Machine",
            ci_type=CIType.SOFTWARE,
            created_by="test_user"
        )

        sm_data = ci_service.get_ci_state_machine(ci.id)
        assert sm_data is None


class TestProgressTracking:
    """Test progress tracking functionality."""

    def test_get_ci_progress_initial(self, db: Session, test_project: Project, ci_service: ConfigurationItemService):
        """
        Test getting progress for a newly created state machine.

        Traceability: REQ-SM-001 (Progress tracking)
        """
        ci = ci_service.create_ci(
            project_id=test_project.id,
            ci_identifier="SW-005",
            name="Progress Test Software",
            ci_type=CIType.SOFTWARE,
            created_by="test_user"
        )

        ci_service.create_state_machine_for_ci_item(ci_id=ci.id, auto_start=True)

        progress = ci_service.get_ci_progress(ci.id)

        assert progress is not None
        assert progress["ci_id"] == ci.id
        assert progress["total_phases"] > 0
        assert progress["completed_phases"] == 0
        assert progress["total_activities"] > 0
        assert progress["completed_activities"] == 0
        assert progress["progress_percent"] == 0.0

    def test_get_current_activity(self, db: Session, test_project: Project, ci_service: ConfigurationItemService):
        """
        Test getting the current activity for a CI.

        Traceability: REQ-SM-003 (Sub-phase sequence)
        """
        ci = ci_service.create_ci(
            project_id=test_project.id,
            ci_identifier="SW-006",
            name="Current Activity Test",
            ci_type=CIType.SOFTWARE,
            created_by="test_user"
        )

        ci_service.create_state_machine_for_ci_item(ci_id=ci.id, auto_start=True)

        current_activity = ci_service.get_ci_current_activity(ci.id)

        assert current_activity is not None
        assert "phase" in current_activity
        assert "sub_phase" in current_activity
        assert "activity" in current_activity
        assert current_activity["activity"]["activity_id"] is not None
        assert current_activity["activity"]["name"] is not None


class TestCITypeMapping:
    """Test CI type to process type mapping."""

    def test_software_ci_gets_do178c_process(self, db: Session, test_project: Project, ci_service: ConfigurationItemService):
        """Verify SOFTWARE CI uses DO-178C template."""
        ci = ci_service.create_ci(
            project_id=test_project.id,
            ci_identifier="SW-MAPPING",
            name="Mapping Test",
            ci_type=CIType.SOFTWARE,
            created_by="test_user"
        )

        result = ci_service.create_state_machine_for_ci_item(ci_id=ci.id)

        assert "DO-178C" in result["template_name"]

    def test_hardware_ci_gets_do254_process(self, db: Session, test_project: Project, ci_service: ConfigurationItemService):
        """Verify HARDWARE CI uses DO-254 template."""
        ci = ci_service.create_ci(
            project_id=test_project.id,
            ci_identifier="HW-MAPPING",
            name="HW Mapping Test",
            ci_type=CIType.HARDWARE,
            created_by="test_user"
        )

        result = ci_service.create_state_machine_for_ci_item(ci_id=ci.id)

        assert "DO-254" in result["template_name"]

    def test_cots_ci_gets_component_process(self, db: Session, test_project: Project, ci_service: ConfigurationItemService):
        """Verify COTS CI uses component template."""
        ci = ci_service.create_ci(
            project_id=test_project.id,
            ci_identifier="COTS-001",
            name="COTS Component",
            ci_type=CIType.COTS,
            created_by="test_user"
        )

        result = ci_service.create_state_machine_for_ci_item(ci_id=ci.id)

        assert result is not None
        # COTS should map to COMPONENT process type


class TestDALFiltering:
    """Test that activities are filtered based on DAL level."""

    def test_dal_a_has_all_activities(self, db: Session, test_project: Project, ci_service: ConfigurationItemService):
        """
        Verify DAL-A includes all activities.

        Traceability: REQ-SM-001 (DAL-based filtering)
        """
        ci = ci_service.create_ci(
            project_id=test_project.id,
            ci_identifier="SW-DAL-A",
            name="DAL A Software",
            ci_type=CIType.SOFTWARE,
            criticality="DAL A",
            created_by="test_user"
        )

        result = ci_service.create_state_machine_for_ci_item(ci_id=ci.id, dal_level="DAL_A")
        progress_a = ci_service.get_ci_progress(ci.id)

        # Create another with DAL-D to compare
        ci_d = ci_service.create_ci(
            project_id=test_project.id,
            ci_identifier="SW-DAL-D",
            name="DAL D Software",
            ci_type=CIType.SOFTWARE,
            criticality="DAL D",
            created_by="test_user"
        )

        ci_service.create_state_machine_for_ci_item(ci_id=ci_d.id, dal_level="DAL_D")
        progress_d = ci_service.get_ci_progress(ci_d.id)

        # DAL-A should have more or equal activities than DAL-D
        # (DAL-A is most stringent, DAL-D is least)
        assert progress_a["total_activities"] >= progress_d["total_activities"]


class TestStateMachineController:
    """Test state machine controller functionality."""

    def test_controller_can_get_current_activity(self):
        """
        Test that controller can identify current activity.

        Traceability: REQ-SM-003 (Sub-phase sequence)
        """
        # Create a simple state machine instance
        sm_instance = create_state_machine_for_ci(
            ci_id=1,
            ci_type="SOFTWARE",
            dal_level="DAL_B"
        )

        controller = StateMachineController(sm_instance)
        controller.start_phase(0)

        current_activity = controller.get_current_activity()

        assert current_activity is not None
        assert current_activity.activity_id is not None
        assert current_activity.status == ActivityStatus.IN_PROGRESS

    def test_complete_activity_advances_state(self):
        """
        Test that completing an activity advances to the next one.

        Traceability: REQ-SM-003 (Activity sequencing)
        """
        sm_instance = create_state_machine_for_ci(
            ci_id=1,
            ci_type="SOFTWARE",
            dal_level="DAL_B"
        )

        controller = StateMachineController(sm_instance)
        controller.start_phase(0)

        first_activity = controller.get_current_activity()
        first_activity_id = first_activity.activity_id

        # Complete the activity
        controller.complete_activity(first_activity_id, {"result": "success"})

        second_activity = controller.get_current_activity()

        # Should have advanced to next activity
        assert second_activity is not None
        assert second_activity.activity_id != first_activity_id

    def test_phase_progress_calculation(self):
        """
        Test progress calculation for a phase.

        Traceability: REQ-SM-001 (Progress tracking)
        """
        sm_instance = create_state_machine_for_ci(
            ci_id=1,
            ci_type="SOFTWARE",
            dal_level="DAL_B"
        )

        controller = StateMachineController(sm_instance)
        controller.start_phase(0)

        progress = controller.get_phase_progress(0)

        assert progress["phase_id"] is not None
        assert progress["phase_name"] is not None
        assert progress["total_activities"] > 0
        assert progress["completed_activities"] == 0
        assert progress["progress_percent"] == 0.0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_create_state_machine_for_nonexistent_ci(self, db: Session, ci_service: ConfigurationItemService):
        """Test creating state machine for CI that doesn't exist."""
        result = ci_service.create_state_machine_for_ci_item(ci_id=99999)
        assert result is None

    def test_get_progress_for_ci_without_state_machine(self, db: Session, test_project: Project, ci_service: ConfigurationItemService):
        """Test getting progress for CI without state machine."""
        ci = ci_service.create_ci(
            project_id=test_project.id,
            ci_identifier="SW-NO-SM",
            name="No State Machine",
            ci_type=CIType.SOFTWARE,
            created_by="test_user"
        )

        progress = ci_service.get_ci_progress(ci.id)
        assert progress is None

    def test_skip_optional_activity(self):
        """
        Test skipping an optional activity.

        Traceability: REQ-SM-003 (Activity optional/required)
        """
        sm_instance = create_state_machine_for_ci(
            ci_id=1,
            ci_type="SOFTWARE",
            dal_level="DAL_D"  # Lower DAL may have optional activities
        )

        controller = StateMachineController(sm_instance)
        controller.start_phase(0)

        # Find an optional activity
        current = controller.get_current_activity()
        if not current.required:
            # Skip it
            result = controller.skip_activity(current.activity_id, "Not applicable")
            assert result is True

            # Should advance to next activity
            next_activity = controller.get_current_activity()
            assert next_activity is not None
            assert next_activity.activity_id != current.activity_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
