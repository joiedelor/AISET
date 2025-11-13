"""
Requirements Service
DO-178C Traceability: REQ-SERVICE-002
Purpose: Business logic for requirements management

This service provides all operations for managing requirements,
including validation, hierarchical decomposition, and version control.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

from models.requirement import Requirement, RequirementStatus, RequirementType, RequirementPriority
from models.audit import VersionHistory, ChangeType
from config.settings import settings

logger = logging.getLogger(__name__)


class RequirementsService:
    """
    Service for requirements management operations.

    Traceability:
    - REQ-REQ-002: Requirements business logic
    - REQ-VALID-004: Requirements validation
    """

    def __init__(self, db: Session):
        self.db = db

    def create_requirement(
        self,
        project_id: int,
        requirement_id: str,
        title: str,
        description: str,
        req_type: RequirementType,
        priority: RequirementPriority = RequirementPriority.MEDIUM,
        parent_id: Optional[int] = None,
        created_by: str = "system",
        **kwargs
    ) -> Requirement:
        """
        Create a new requirement.

        Traceability: REQ-REQ-003 - Requirement creation

        Args:
            project_id: Project ID
            requirement_id: Unique requirement identifier
            title: Requirement title
            description: Detailed description
            req_type: Requirement type
            priority: Priority level
            parent_id: Parent requirement for hierarchical decomposition
            created_by: User creating the requirement
            **kwargs: Additional fields

        Returns:
            Created Requirement instance
        """
        requirement = Requirement(
            project_id=project_id,
            requirement_id=requirement_id,
            title=title,
            description=description,
            type=req_type,
            priority=priority,
            parent_id=parent_id,
            created_by=created_by,
            status=RequirementStatus.DRAFT,
            **kwargs
        )

        self.db.add(requirement)
        self.db.commit()
        self.db.refresh(requirement)

        # Create version history
        if settings.enable_audit_trail:
            self._create_version_history(requirement, ChangeType.CREATE, created_by)

        logger.info(f"Created requirement: {requirement_id}")
        return requirement

    def update_requirement(
        self,
        requirement_id: int,
        updated_by: str,
        **updates
    ) -> Requirement:
        """
        Update an existing requirement.

        Traceability:
        - REQ-REQ-004: Requirement updates
        - REQ-AUDIT-010: Update tracking

        Args:
            requirement_id: Requirement database ID
            updated_by: User making the update
            **updates: Fields to update

        Returns:
            Updated Requirement instance
        """
        requirement = self.db.query(Requirement).filter(Requirement.id == requirement_id).first()

        if not requirement:
            raise ValueError(f"Requirement {requirement_id} not found")

        # Store previous state for audit trail
        previous_data = self._serialize_requirement(requirement)

        # Apply updates
        for key, value in updates.items():
            if hasattr(requirement, key):
                setattr(requirement, key, value)

        self.db.commit()
        self.db.refresh(requirement)

        # Create version history
        if settings.enable_audit_trail:
            new_data = self._serialize_requirement(requirement)
            self._create_version_history(
                requirement,
                ChangeType.UPDATE,
                updated_by,
                previous_data=previous_data,
                new_data=new_data
            )

        logger.info(f"Updated requirement: {requirement.requirement_id}")
        return requirement

    def approve_requirement(
        self,
        requirement_id: int,
        approved_by: str,
        rationale: Optional[str] = None
    ) -> Requirement:
        """
        Approve a requirement for implementation.

        Traceability:
        - REQ-APPROVAL-002: Requirement approval
        - REQ-WORKFLOW-001: Approval workflow

        Args:
            requirement_id: Requirement database ID
            approved_by: User approving the requirement
            rationale: Approval rationale

        Returns:
            Approved Requirement instance
        """
        requirement = self.db.query(Requirement).filter(Requirement.id == requirement_id).first()

        if not requirement:
            raise ValueError(f"Requirement {requirement_id} not found")

        requirement.status = RequirementStatus.APPROVED
        requirement.approved_by = approved_by
        from datetime import datetime
        requirement.approved_at = datetime.utcnow()

        if rationale:
            requirement.rationale = rationale

        self.db.commit()
        self.db.refresh(requirement)

        # Create version history
        if settings.enable_audit_trail:
            self._create_version_history(requirement, ChangeType.APPROVE, approved_by)

        logger.info(f"Approved requirement: {requirement.requirement_id}")
        return requirement

    def get_requirement(self, requirement_id: int) -> Optional[Requirement]:
        """Get a requirement by ID."""
        return self.db.query(Requirement).filter(Requirement.id == requirement_id).first()

    def get_requirements_by_project(
        self,
        project_id: int,
        status: Optional[RequirementStatus] = None,
        req_type: Optional[RequirementType] = None,
        priority: Optional[RequirementPriority] = None
    ) -> List[Requirement]:
        """
        Get all requirements for a project with optional filtering.

        Traceability: REQ-REQ-005 - Requirements querying

        Args:
            project_id: Project ID
            status: Filter by status
            req_type: Filter by type
            priority: Filter by priority

        Returns:
            List of matching requirements
        """
        query = self.db.query(Requirement).filter(Requirement.project_id == project_id)

        if status:
            query = query.filter(Requirement.status == status)
        if req_type:
            query = query.filter(Requirement.type == req_type)
        if priority:
            query = query.filter(Requirement.priority == priority)

        return query.all()

    def get_child_requirements(self, parent_id: int) -> List[Requirement]:
        """
        Get all child requirements for hierarchical decomposition.

        Traceability: REQ-HIER-001 - Hierarchical requirements
        """
        return self.db.query(Requirement).filter(Requirement.parent_id == parent_id).all()

    def validate_requirement(self, requirement: Requirement) -> Dict[str, Any]:
        """
        Validate requirement quality per DO-178C.

        Traceability: REQ-VALID-005 - Quality validation

        Returns:
            Dict with validation results and issues
        """
        issues = []
        warnings = []

        # Check title length
        if len(requirement.title) < 10:
            issues.append("Title too short (minimum 10 characters)")
        if len(requirement.title) > 500:
            issues.append("Title too long (maximum 500 characters)")

        # Check description
        if len(requirement.description) < 20:
            issues.append("Description too short (minimum 20 characters)")

        # Check for ambiguous words (DO-178C guideline)
        ambiguous_words = ["should", "might", "could", "may", "possibly"]
        for word in ambiguous_words:
            if word in requirement.description.lower():
                warnings.append(f"Ambiguous word '{word}' detected - use 'shall' for mandatory requirements")

        # Check acceptance criteria
        if not requirement.acceptance_criteria:
            warnings.append("Missing acceptance criteria - makes verification difficult")

        # Check rationale
        if not requirement.rationale:
            warnings.append("Missing rationale - documenting why helps with understanding")

        is_valid = len(issues) == 0

        return {
            "is_valid": is_valid,
            "issues": issues,
            "warnings": warnings,
            "quality_score": self._calculate_quality_score(requirement, issues, warnings)
        }

    def _calculate_quality_score(
        self,
        requirement: Requirement,
        issues: List[str],
        warnings: List[str]
    ) -> float:
        """Calculate requirement quality score (0.0 to 1.0)."""
        score = 1.0

        # Deduct for issues
        score -= len(issues) * 0.2

        # Deduct for warnings
        score -= len(warnings) * 0.05

        # Bonus for complete information
        if requirement.acceptance_criteria:
            score += 0.05
        if requirement.rationale:
            score += 0.05

        return max(0.0, min(1.0, score))

    def _serialize_requirement(self, requirement: Requirement) -> Dict[str, Any]:
        """Serialize requirement for audit trail."""
        return {
            "requirement_id": requirement.requirement_id,
            "title": requirement.title,
            "description": requirement.description,
            "type": requirement.type.value if requirement.type else None,
            "priority": requirement.priority.value if requirement.priority else None,
            "status": requirement.status.value if requirement.status else None,
            "rationale": requirement.rationale,
            "acceptance_criteria": requirement.acceptance_criteria
        }

    def _create_version_history(
        self,
        requirement: Requirement,
        change_type: ChangeType,
        changed_by: str,
        previous_data: Optional[Dict] = None,
        new_data: Optional[Dict] = None
    ):
        """Create version history entry."""
        # Get current version number
        last_version = (
            self.db.query(VersionHistory)
            .filter(VersionHistory.requirement_id == requirement.id)
            .order_by(VersionHistory.version_number.desc())
            .first()
        )

        version_number = (last_version.version_number + 1) if last_version else 1

        history = VersionHistory(
            requirement_id=requirement.id,
            change_type=change_type,
            entity_type="requirement",
            version_number=version_number,
            previous_data=previous_data,
            new_data=new_data if new_data else self._serialize_requirement(requirement),
            change_summary=f"{change_type.value.capitalize()} requirement {requirement.requirement_id}",
            changed_by=changed_by
        )

        self.db.add(history)
        self.db.commit()
