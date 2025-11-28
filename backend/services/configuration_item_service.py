"""
Configuration Item Service
DO-178C Traceability: REQ-AI-038, REQ-AI-039, REQ-AI-040, REQ-BE-013
Purpose: Business logic for product structure and BOM management

This service implements:
- REQ-AI-038: Product Structure Extraction
- REQ-AI-039: Configuration Item Data Extraction
- REQ-AI-040: CI Classification
- REQ-BE-013: BOM management CRUD operations
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import uuid
import logging
import json

from models.configuration_item import (
    ConfigurationItem,
    BillOfMaterials,
    CIType,
    CILifecyclePhase,
    CIControlLevel,
    CIStatus,
    BOMType
)
from process_engine import (
    create_state_machine_for_ci,
    StateMachineController,
    StateMachineInstance,
    CIType as ProcessCIType
)
from services.process_event_service import get_event_service

logger = logging.getLogger(__name__)


class ConfigurationItemService:
    """
    Service for managing Configuration Items and BOM.

    Traceability:
    - REQ-AI-038: Product Structure Extraction
    - REQ-AI-039: CI Data Extraction
    - REQ-AI-040: CI Classification
    - REQ-BE-013: BOM management
    """

    def __init__(self, db: Session):
        self.db = db

    # ==================== CI CRUD Operations ====================

    def create_ci(
        self,
        project_id: int,
        ci_identifier: str,
        name: str,
        ci_type: CIType = CIType.COMPONENT,
        parent_id: Optional[int] = None,
        **kwargs
    ) -> ConfigurationItem:
        """
        Create a new Configuration Item.

        Traceability: REQ-AI-039 - CI Data Extraction

        Args:
            project_id: Project ID
            ci_identifier: Unique CI identifier (e.g., "SYS-001")
            name: CI name
            ci_type: Type of CI
            parent_id: Optional parent CI ID for hierarchy
            **kwargs: Additional CI fields

        Returns:
            Created ConfigurationItem
        """
        # Generate GUID
        guid = str(uuid.uuid4())

        # Calculate level and path
        level = 0
        path = ""
        if parent_id:
            parent = self.get_ci_by_id(parent_id)
            if parent:
                level = parent.level + 1
                path = f"{parent.path}.{parent.id}" if parent.path else str(parent.id)

        ci = ConfigurationItem(
            guid=guid,
            project_id=project_id,
            ci_identifier=ci_identifier,
            name=name,
            ci_type=ci_type,
            parent_id=parent_id,
            level=level,
            path=path,
            description=kwargs.get("description"),
            part_number=kwargs.get("part_number"),
            revision=kwargs.get("revision"),
            version=kwargs.get("version"),
            lifecycle_phase=kwargs.get("lifecycle_phase", CILifecyclePhase.DEVELOPMENT),
            control_level=kwargs.get("control_level", CIControlLevel.LEVEL_3),
            status=kwargs.get("status", CIStatus.DRAFT),
            criticality=kwargs.get("criticality"),
            supplier=kwargs.get("supplier"),
            created_by=kwargs.get("created_by", "system"),
            ai_extracted=kwargs.get("ai_extracted", False),
            ai_confidence=kwargs.get("ai_confidence"),
            extraction_source=kwargs.get("extraction_source"),
            notes=kwargs.get("notes")
        )

        self.db.add(ci)
        self.db.commit()
        self.db.refresh(ci)

        logger.info(f"Created CI: {ci_identifier} ({name}) in project {project_id}")
        return ci

    def get_ci_by_id(self, ci_id: int) -> Optional[ConfigurationItem]:
        """Get a CI by ID."""
        return self.db.query(ConfigurationItem).filter(ConfigurationItem.id == ci_id).first()

    def get_ci_by_identifier(self, project_id: int, ci_identifier: str) -> Optional[ConfigurationItem]:
        """Get a CI by identifier within a project."""
        return self.db.query(ConfigurationItem).filter(
            and_(
                ConfigurationItem.project_id == project_id,
                ConfigurationItem.ci_identifier == ci_identifier
            )
        ).first()

    def get_project_cis(
        self,
        project_id: int,
        ci_type: Optional[CIType] = None,
        parent_id: Optional[int] = None
    ) -> List[ConfigurationItem]:
        """
        Get CIs for a project with optional filtering.

        Args:
            project_id: Project ID
            ci_type: Optional filter by CI type
            parent_id: Optional filter by parent (None for root items)

        Returns:
            List of ConfigurationItems
        """
        query = self.db.query(ConfigurationItem).filter(ConfigurationItem.project_id == project_id)

        if ci_type:
            query = query.filter(ConfigurationItem.ci_type == ci_type)

        if parent_id is not None:
            query = query.filter(ConfigurationItem.parent_id == parent_id)
        elif parent_id is None:
            # Get root items (no parent)
            query = query.filter(ConfigurationItem.parent_id.is_(None))

        return query.order_by(ConfigurationItem.ci_identifier).all()

    def update_ci(self, ci_id: int, **kwargs) -> Optional[ConfigurationItem]:
        """Update a CI."""
        ci = self.get_ci_by_id(ci_id)
        if not ci:
            return None

        for key, value in kwargs.items():
            if hasattr(ci, key):
                setattr(ci, key, value)

        ci.updated_by = kwargs.get("updated_by", "system")
        self.db.commit()
        self.db.refresh(ci)

        logger.info(f"Updated CI: {ci.ci_identifier}")
        return ci

    def delete_ci(self, ci_id: int) -> bool:
        """Delete a CI and its children (cascade)."""
        ci = self.get_ci_by_id(ci_id)
        if not ci:
            return False

        self.db.delete(ci)
        self.db.commit()

        logger.info(f"Deleted CI: {ci.ci_identifier}")
        return True

    # ==================== Product Structure Tree ====================

    def get_product_structure_tree(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get full product structure tree for a project.

        Traceability: REQ-AI-038 - Product Structure Extraction

        Returns:
            Hierarchical tree structure
        """
        # Get all root CIs
        root_cis = self.get_project_cis(project_id, parent_id=None)

        def build_tree(ci: ConfigurationItem) -> Dict[str, Any]:
            """Recursively build tree node."""
            children = self.db.query(ConfigurationItem).filter(
                ConfigurationItem.parent_id == ci.id
            ).order_by(ConfigurationItem.ci_identifier).all()

            return {
                **ci.to_dict(),
                "children": [build_tree(child) for child in children]
            }

        return [build_tree(ci) for ci in root_cis]

    # ==================== BOM Operations ====================

    def add_bom_entry(
        self,
        parent_ci_id: int,
        child_ci_id: int,
        quantity: float = 1.0,
        bom_type: BOMType = BOMType.ENGINEERING,
        **kwargs
    ) -> BillOfMaterials:
        """
        Add a BOM relationship between two CIs.

        Traceability: REQ-DB-039 - Store BOM relationships

        Args:
            parent_ci_id: Parent CI ID
            child_ci_id: Child CI ID
            quantity: Quantity of child in parent
            bom_type: Type of BOM
            **kwargs: Additional BOM fields

        Returns:
            Created BillOfMaterials entry
        """
        # Check if entry already exists
        existing = self.db.query(BillOfMaterials).filter(
            and_(
                BillOfMaterials.parent_ci_id == parent_ci_id,
                BillOfMaterials.child_ci_id == child_ci_id,
                BillOfMaterials.bom_type == bom_type
            )
        ).first()

        if existing:
            logger.warning(f"BOM entry already exists: {parent_ci_id} -> {child_ci_id}")
            return existing

        bom = BillOfMaterials(
            parent_ci_id=parent_ci_id,
            child_ci_id=child_ci_id,
            bom_type=bom_type,
            quantity=quantity,
            unit_of_measure=kwargs.get("unit_of_measure", "each"),
            position_reference=kwargs.get("position_reference"),
            find_number=kwargs.get("find_number"),
            is_alternate=kwargs.get("is_alternate", False),
            notes=kwargs.get("notes"),
            created_by=kwargs.get("created_by", "system")
        )

        self.db.add(bom)
        self.db.commit()
        self.db.refresh(bom)

        logger.info(f"Created BOM entry: {parent_ci_id} -> {child_ci_id} (qty: {quantity})")
        return bom

    def get_bom_for_ci(
        self,
        ci_id: int,
        bom_type: Optional[BOMType] = None
    ) -> List[BillOfMaterials]:
        """Get all BOM entries where CI is the parent."""
        query = self.db.query(BillOfMaterials).filter(BillOfMaterials.parent_ci_id == ci_id)

        if bom_type:
            query = query.filter(BillOfMaterials.bom_type == bom_type)

        return query.all()

    def get_where_used(self, ci_id: int) -> List[BillOfMaterials]:
        """Get all BOM entries where CI is used as a child (where-used)."""
        return self.db.query(BillOfMaterials).filter(BillOfMaterials.child_ci_id == ci_id).all()

    def delete_bom_entry(self, bom_id: int) -> bool:
        """Delete a BOM entry."""
        bom = self.db.query(BillOfMaterials).filter(BillOfMaterials.id == bom_id).first()
        if not bom:
            return False

        self.db.delete(bom)
        self.db.commit()
        return True

    # ==================== AI Extraction Support ====================

    def extract_structure_from_text(
        self,
        project_id: int,
        text: str,
        created_by: str = "ai"
    ) -> List[ConfigurationItem]:
        """
        Extract product structure from text description.

        Traceability: REQ-AI-038 - Product Structure Extraction

        This is a placeholder for AI-powered extraction.
        In production, this would call the AI service.

        Args:
            project_id: Project ID
            text: Text to extract from
            created_by: User/system creating the extraction

        Returns:
            List of extracted CIs
        """
        # This would integrate with AI service for actual extraction
        # For now, return empty list - AI service will handle this
        logger.info(f"Structure extraction requested for project {project_id}")
        return []

    def classify_ci(self, ci_id: int) -> Dict[str, Any]:
        """
        Classify a CI based on its properties.

        Traceability: REQ-AI-040 - CI Classification

        Returns:
            Classification results
        """
        ci = self.get_ci_by_id(ci_id)
        if not ci:
            return {"error": "CI not found"}

        # Basic classification logic (would be enhanced by AI)
        classification = {
            "ci_id": ci_id,
            "ci_identifier": ci.ci_identifier,
            "suggested_type": ci.ci_type.value if ci.ci_type else None,
            "suggested_control_level": ci.control_level.value if ci.control_level else None,
            "classification_confidence": 0.8,
            "recommendations": []
        }

        # Add recommendations based on properties
        if ci.criticality and ci.criticality.upper() in ["DAL A", "DAL B", "ASIL D", "ASIL C"]:
            classification["recommendations"].append("High criticality - recommend Level 1 or 2 control")

        if not ci.part_number:
            classification["recommendations"].append("Missing part number - recommend adding for traceability")

        return classification

    # ==================== Statistics ====================

    def get_project_ci_statistics(self, project_id: int) -> Dict[str, Any]:
        """Get CI statistics for a project."""
        all_cis = self.db.query(ConfigurationItem).filter(
            ConfigurationItem.project_id == project_id
        ).all()

        # Count by type
        type_counts = {}
        for ci_type in CIType:
            count = sum(1 for ci in all_cis if ci.ci_type == ci_type)
            if count > 0:
                type_counts[ci_type.value] = count

        # Count by status
        status_counts = {}
        for status in CIStatus:
            count = sum(1 for ci in all_cis if ci.status == status)
            if count > 0:
                status_counts[status.value] = count

        # Count by lifecycle phase
        phase_counts = {}
        for phase in CILifecyclePhase:
            count = sum(1 for ci in all_cis if ci.lifecycle_phase == phase)
            if count > 0:
                phase_counts[phase.value] = count

        # BOM statistics
        bom_count = self.db.query(BillOfMaterials).join(
            ConfigurationItem, BillOfMaterials.parent_ci_id == ConfigurationItem.id
        ).filter(ConfigurationItem.project_id == project_id).count()

        return {
            "total_cis": len(all_cis),
            "by_type": type_counts,
            "by_status": status_counts,
            "by_lifecycle_phase": phase_counts,
            "bom_relationships": bom_count,
            "root_items": sum(1 for ci in all_cis if ci.parent_id is None),
            "max_depth": max((ci.level for ci in all_cis), default=0)
        }

    # ==================== Process Engine Integration ====================

    @staticmethod
    def _map_ci_type_to_process_type(ci_type: CIType) -> str:
        """
        Map ConfigurationItem CIType to Process Engine CIType.

        This mapping determines which process template is used for the CI.
        """
        mapping = {
            CIType.SYSTEM: "SYSTEM",
            CIType.SUBSYSTEM: "SUBSYSTEM",
            CIType.COMPONENT: "COMPONENT",
            CIType.SOFTWARE: "SOFTWARE",
            CIType.HARDWARE: "HARDWARE",
            CIType.DOCUMENT: "DOCUMENT",
            CIType.INTERFACE: "COMPONENT",
            CIType.COTS: "COMPONENT",
            CIType.NDI: "COMPONENT",
            CIType.OTHER: "COMPONENT"
        }
        return mapping.get(ci_type, "COMPONENT")

    def create_state_machine_for_ci_item(
        self,
        ci_id: int,
        dal_level: Optional[str] = None,
        auto_start: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Create and store a state machine instance for a CI.

        Traceability: REQ-SM-001 to REQ-SM-006 (State Machine Requirements)

        Args:
            ci_id: Configuration Item ID
            dal_level: Optional DAL/SIL/ASIL level (e.g., "DAL_B", "ASIL_D")
            auto_start: Whether to automatically start the first phase

        Returns:
            State machine instance as dictionary, or None if CI not found
        """
        ci = self.get_ci_by_id(ci_id)
        if not ci:
            logger.error(f"CI not found: {ci_id}")
            return None

        # Use criticality from CI if dal_level not specified
        if not dal_level and ci.criticality:
            dal_level = ci.criticality.replace(" ", "_").upper()

        # Map CI type to process engine type
        process_ci_type = self._map_ci_type_to_process_type(ci.ci_type)

        try:
            # Create state machine instance
            sm_instance = create_state_machine_for_ci(
                ci_id=ci_id,
                ci_type=process_ci_type,
                dal_level=dal_level
            )

            # Store in database (ci_state_machines table)
            from models.project import CIStateMachine
            sm_record = CIStateMachine(
                guid=str(uuid.uuid4()),
                ci_id=ci_id,
                template_id=sm_instance.template_id,
                template_name=sm_instance.template_name,
                dal_level=sm_instance.dal_level,
                current_phase_index=sm_instance.current_phase_index,
                state_data=json.dumps(sm_instance.to_dict()),
                created_by="system"
            )

            self.db.add(sm_record)
            self.db.commit()
            self.db.refresh(sm_record)

            # Auto-start first phase if requested
            if auto_start:
                controller = StateMachineController(sm_instance)
                if controller.start_phase(0):
                    # Update state in database
                    sm_record.state_data = json.dumps(sm_instance.to_dict())
                    sm_record.current_phase_index = sm_instance.current_phase_index
                    self.db.commit()

            logger.info(f"Created state machine for CI {ci_id}: {sm_instance.template_name}")

            return {
                "state_machine_id": sm_record.id,
                "instance_id": sm_instance.instance_id,
                "ci_id": ci_id,
                "template_name": sm_instance.template_name,
                "dal_level": sm_instance.dal_level,
                "current_phase_index": sm_instance.current_phase_index,
                "overall_progress": sm_instance.overall_progress,
                "created_at": sm_record.created_at.isoformat() if sm_record.created_at else None
            }

        except Exception as e:
            logger.error(f"Failed to create state machine for CI {ci_id}: {str(e)}")
            return None

    def get_ci_state_machine(self, ci_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the state machine instance for a CI.

        Args:
            ci_id: Configuration Item ID

        Returns:
            State machine data or None if not found
        """
        from models.project import CIStateMachine

        sm_record = self.db.query(CIStateMachine).filter(
            CIStateMachine.ci_id == ci_id
        ).order_by(CIStateMachine.created_at.desc()).first()

        if not sm_record:
            return None

        # Parse state data
        try:
            state_data = json.loads(sm_record.state_data)
            return {
                "state_machine_id": sm_record.id,
                "ci_id": ci_id,
                "template_id": sm_record.template_id,
                "template_name": sm_record.template_name,
                "dal_level": sm_record.dal_level,
                "current_phase_index": sm_record.current_phase_index,
                "state_data": state_data,
                "created_at": sm_record.created_at.isoformat() if sm_record.created_at else None,
                "updated_at": sm_record.updated_at.isoformat() if sm_record.updated_at else None
            }
        except json.JSONDecodeError:
            logger.error(f"Invalid state data for CI {ci_id}")
            return None

    def get_ci_current_activity(self, ci_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the current activity that should be worked on for a CI.

        Args:
            ci_id: Configuration Item ID

        Returns:
            Current activity information or None
        """
        sm_data = self.get_ci_state_machine(ci_id)
        if not sm_data:
            return None

        # Reconstruct state machine instance
        from process_engine.services.state_machine_generator import StateMachineInstance
        state_dict = sm_data["state_data"]

        # This is a simplified reconstruction - in production, you'd have a proper deserializer
        current_phase = state_dict.get("phases", [])[state_dict.get("current_phase_index", 0)]
        if not current_phase:
            return None

        current_sub_phase_idx = current_phase.get("current_sub_phase_index", 0)
        sub_phases = current_phase.get("sub_phases", [])

        if current_sub_phase_idx >= len(sub_phases):
            return None

        current_sub_phase = sub_phases[current_sub_phase_idx]
        current_activity_idx = current_sub_phase.get("current_activity_index", 0)
        activities = current_sub_phase.get("activities", [])

        if current_activity_idx >= len(activities):
            return None

        current_activity = activities[current_activity_idx]

        return {
            "ci_id": ci_id,
            "phase": {
                "name": current_phase.get("name"),
                "order": current_phase.get("order"),
                "status": current_phase.get("status")
            },
            "sub_phase": {
                "name": current_sub_phase.get("name"),
                "order": current_sub_phase.get("order"),
                "status": current_sub_phase.get("status")
            },
            "activity": {
                "activity_id": current_activity.get("activity_id"),
                "name": current_activity.get("name"),
                "type": current_activity.get("activity_type"),
                "status": current_activity.get("status"),
                "required": current_activity.get("required", True),
                "output_artifacts": current_activity.get("output_artifacts", [])
            }
        }

    def get_ci_progress(self, ci_id: int) -> Optional[Dict[str, Any]]:
        """
        Get progress information for a CI's development process.

        Args:
            ci_id: Configuration Item ID

        Returns:
            Progress information including percentage completion
        """
        sm_data = self.get_ci_state_machine(ci_id)
        if not sm_data:
            return None

        state_dict = sm_data["state_data"]
        phases = state_dict.get("phases", [])

        total_phases = len(phases)
        completed_phases = sum(1 for p in phases if p.get("status") == "completed")

        # Calculate overall progress from activities
        total_activities = 0
        completed_activities = 0

        for phase in phases:
            for sub_phase in phase.get("sub_phases", []):
                for activity in sub_phase.get("activities", []):
                    total_activities += 1
                    if activity.get("status") in ["completed", "skipped"]:
                        completed_activities += 1

        progress_percent = (completed_activities / total_activities * 100) if total_activities > 0 else 0

        return {
            "ci_id": ci_id,
            "template_name": sm_data["template_name"],
            "dal_level": sm_data.get("dal_level"),
            "total_phases": total_phases,
            "completed_phases": completed_phases,
            "current_phase_index": sm_data["current_phase_index"],
            "total_activities": total_activities,
            "completed_activities": completed_activities,
            "progress_percent": round(progress_percent, 1),
            "current_phase_name": phases[sm_data["current_phase_index"]].get("name") if sm_data["current_phase_index"] < len(phases) else None
        }

    def complete_activity(
        self,
        ci_id: int,
        activity_id: str,
        completion_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Mark an activity as complete and advance the state machine.

        Traceability: REQ-SM-003 (Activity sequencing)

        Args:
            ci_id: Configuration Item ID
            activity_id: Activity ID to complete
            completion_data: Optional data about the completion (artifacts, notes, etc.)

        Returns:
            Updated state machine data or None if failed
        """
        from models.project import CIStateMachine

        # Get the state machine record
        sm_record = self.db.query(CIStateMachine).filter(
            CIStateMachine.ci_id == ci_id
        ).order_by(CIStateMachine.created_at.desc()).first()

        if not sm_record:
            logger.error(f"No state machine found for CI {ci_id}")
            return None

        # Parse state data
        try:
            state_dict = json.loads(sm_record.state_data)
        except json.JSONDecodeError:
            logger.error(f"Invalid state data for CI {ci_id}")
            return None

        # Reconstruct state machine instance
        from process_engine.services.state_machine_generator import (
            StateMachineInstance,
            StateMachineController,
            PhaseInstance,
            SubPhaseInstance,
            ActivityInstance,
            PhaseStatus,
            SubPhaseStatus,
            ActivityStatus
        )
        from datetime import datetime as dt

        # Helper to reconstruct instances from dict
        def dict_to_activity(act_dict: Dict) -> ActivityInstance:
            return ActivityInstance(
                activity_id=act_dict["activity_id"],
                name=act_dict["name"],
                activity_type=act_dict["activity_type"],
                status=ActivityStatus(act_dict["status"]),
                required=act_dict["required"],
                started_at=dt.fromisoformat(act_dict["started_at"]) if act_dict.get("started_at") else None,
                completed_at=dt.fromisoformat(act_dict["completed_at"]) if act_dict.get("completed_at") else None,
                output_artifacts=act_dict.get("output_artifacts", []),
                completion_data=act_dict.get("completion_data", {})
            )

        def dict_to_subphase(sp_dict: Dict) -> SubPhaseInstance:
            return SubPhaseInstance(
                sub_phase_id=sp_dict["sub_phase_id"],
                name=sp_dict["name"],
                order=sp_dict["order"],
                status=SubPhaseStatus(sp_dict["status"]),
                activities=[dict_to_activity(a) for a in sp_dict["activities"]],
                started_at=dt.fromisoformat(sp_dict["started_at"]) if sp_dict.get("started_at") else None,
                completed_at=dt.fromisoformat(sp_dict["completed_at"]) if sp_dict.get("completed_at") else None,
                current_activity_index=sp_dict["current_activity_index"]
            )

        def dict_to_phase(p_dict: Dict) -> PhaseInstance:
            return PhaseInstance(
                phase_id=p_dict["phase_id"],
                name=p_dict["name"],
                order=p_dict["order"],
                status=PhaseStatus(p_dict["status"]),
                sub_phases=[dict_to_subphase(sp) for sp in p_dict["sub_phases"]],
                deliverables=p_dict.get("deliverables", []),
                reviews=p_dict.get("reviews", []),
                started_at=dt.fromisoformat(p_dict["started_at"]) if p_dict.get("started_at") else None,
                completed_at=dt.fromisoformat(p_dict["completed_at"]) if p_dict.get("completed_at") else None,
                current_sub_phase_index=p_dict["current_sub_phase_index"],
                entry_criteria_met=p_dict["entry_criteria_met"],
                exit_criteria_met=p_dict["exit_criteria_met"]
            )

        # Reconstruct full state machine
        from process_engine import CIType as ProcessCIType
        sm_instance = StateMachineInstance(
            instance_id=state_dict["instance_id"],
            ci_id=state_dict["ci_id"],
            ci_type=ProcessCIType(state_dict["ci_type"]),
            template_id=state_dict["template_id"],
            template_name=state_dict["template_name"],
            dal_level=state_dict.get("dal_level"),
            phases=[dict_to_phase(p) for p in state_dict["phases"]],
            current_phase_index=state_dict["current_phase_index"],
            created_at=dt.fromisoformat(state_dict["created_at"]),
            updated_at=dt.fromisoformat(state_dict["updated_at"]),
            context=state_dict.get("context", {})
        )

        # Create controller and complete activity
        controller = StateMachineController(sm_instance)
        success = controller.complete_activity(activity_id, completion_data or {})

        if not success:
            logger.warning(f"Failed to complete activity {activity_id} for CI {ci_id}")
            return None

        # Update database with new state
        sm_record.state_data = json.dumps(sm_instance.to_dict())
        sm_record.current_phase_index = sm_instance.current_phase_index
        self.db.commit()

        logger.info(f"Completed activity {activity_id} for CI {ci_id}")

        # Emit event for real-time updates
        event_service = get_event_service()
        event_service.emit_activity_completed(
            ci_id=ci_id,
            activity_id=activity_id,
            activity_name=activity.name,
            progress_percent=sm_instance.overall_progress
        )

        return {
            "ci_id": ci_id,
            "activity_id": activity_id,
            "success": True,
            "current_phase_index": sm_instance.current_phase_index,
            "overall_progress": sm_instance.overall_progress
        }

    def skip_activity(
        self,
        ci_id: int,
        activity_id: str,
        reason: str
    ) -> Optional[Dict[str, Any]]:
        """
        Skip an optional activity.

        Traceability: REQ-SM-003 (Activity optional/required)

        Args:
            ci_id: Configuration Item ID
            activity_id: Activity ID to skip
            reason: Reason for skipping

        Returns:
            Updated state machine data or None if failed
        """
        from models.project import CIStateMachine

        sm_record = self.db.query(CIStateMachine).filter(
            CIStateMachine.ci_id == ci_id
        ).order_by(CIStateMachine.created_at.desc()).first()

        if not sm_record:
            return None

        try:
            state_dict = json.loads(sm_record.state_data)
        except json.JSONDecodeError:
            return None

        # Similar reconstruction as complete_activity
        # (Using same helper functions)
        from process_engine.services.state_machine_generator import (
            StateMachineInstance,
            StateMachineController,
            PhaseInstance,
            SubPhaseInstance,
            ActivityInstance,
            PhaseStatus,
            SubPhaseStatus,
            ActivityStatus
        )
        from datetime import datetime as dt

        def dict_to_activity(act_dict: Dict) -> ActivityInstance:
            return ActivityInstance(
                activity_id=act_dict["activity_id"],
                name=act_dict["name"],
                activity_type=act_dict["activity_type"],
                status=ActivityStatus(act_dict["status"]),
                required=act_dict["required"],
                started_at=dt.fromisoformat(act_dict["started_at"]) if act_dict.get("started_at") else None,
                completed_at=dt.fromisoformat(act_dict["completed_at"]) if act_dict.get("completed_at") else None,
                output_artifacts=act_dict.get("output_artifacts", []),
                completion_data=act_dict.get("completion_data", {})
            )

        def dict_to_subphase(sp_dict: Dict) -> SubPhaseInstance:
            return SubPhaseInstance(
                sub_phase_id=sp_dict["sub_phase_id"],
                name=sp_dict["name"],
                order=sp_dict["order"],
                status=SubPhaseStatus(sp_dict["status"]),
                activities=[dict_to_activity(a) for a in sp_dict["activities"]],
                started_at=dt.fromisoformat(sp_dict["started_at"]) if sp_dict.get("started_at") else None,
                completed_at=dt.fromisoformat(sp_dict["completed_at"]) if sp_dict.get("completed_at") else None,
                current_activity_index=sp_dict["current_activity_index"]
            )

        def dict_to_phase(p_dict: Dict) -> PhaseInstance:
            return PhaseInstance(
                phase_id=p_dict["phase_id"],
                name=p_dict["name"],
                order=p_dict["order"],
                status=PhaseStatus(p_dict["status"]),
                sub_phases=[dict_to_subphase(sp) for sp in p_dict["sub_phases"]],
                deliverables=p_dict.get("deliverables", []),
                reviews=p_dict.get("reviews", []),
                started_at=dt.fromisoformat(p_dict["started_at"]) if p_dict.get("started_at") else None,
                completed_at=dt.fromisoformat(p_dict["completed_at"]) if p_dict.get("completed_at") else None,
                current_sub_phase_index=p_dict["current_sub_phase_index"],
                entry_criteria_met=p_dict["entry_criteria_met"],
                exit_criteria_met=p_dict["exit_criteria_met"]
            )

        from process_engine import CIType as ProcessCIType
        sm_instance = StateMachineInstance(
            instance_id=state_dict["instance_id"],
            ci_id=state_dict["ci_id"],
            ci_type=ProcessCIType(state_dict["ci_type"]),
            template_id=state_dict["template_id"],
            template_name=state_dict["template_name"],
            dal_level=state_dict.get("dal_level"),
            phases=[dict_to_phase(p) for p in state_dict["phases"]],
            current_phase_index=state_dict["current_phase_index"],
            created_at=dt.fromisoformat(state_dict["created_at"]),
            updated_at=dt.fromisoformat(state_dict["updated_at"]),
            context=state_dict.get("context", {})
        )

        controller = StateMachineController(sm_instance)
        success = controller.skip_activity(activity_id, reason)

        if not success:
            logger.warning(f"Failed to skip activity {activity_id} for CI {ci_id}")
            return None

        # Update database
        sm_record.state_data = json.dumps(sm_instance.to_dict())
        sm_record.current_phase_index = sm_instance.current_phase_index
        self.db.commit()

        logger.info(f"Skipped activity {activity_id} for CI {ci_id}: {reason}")

        return {
            "ci_id": ci_id,
            "activity_id": activity_id,
            "skipped": True,
            "reason": reason,
            "current_phase_index": sm_instance.current_phase_index
        }
