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

from models.configuration_item import (
    ConfigurationItem,
    BillOfMaterials,
    CIType,
    CILifecyclePhase,
    CIControlLevel,
    CIStatus,
    BOMType
)

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
