"""
Data Capture Service for AISET Process Engine

This module handles validation, transformation, and storage of captured data
from interview activities. It is part of the "Codification of the Systems Engineer".

Key Features:
- Rule-based validation (no AI interpretation)
- Deterministic data transformation
- Database storage with audit trail
- Traceability link creation

Traceability: REQ-DC-001 to REQ-DC-006
"""

import re
import uuid
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ValidationRule:
    """A single validation rule definition"""
    rule_type: str  # required, min_length, max_length, pattern, allowed_values, etc.
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of a validation operation"""
    valid: bool
    error: Optional[str] = None
    field: Optional[str] = None


@dataclass
class StorageTarget:
    """Target for storing data"""
    table: str
    column: str
    value: Any
    transformation: Optional[str] = None
    json_path: Optional[str] = None  # For JSON column updates


@dataclass
class StorageResult:
    """Result of a storage operation"""
    success: bool
    record_id: Optional[int] = None
    error: Optional[str] = None


@dataclass
class CaptureResult:
    """Complete result of a data capture operation"""
    valid: bool
    stored: bool
    validation_errors: List[ValidationResult] = field(default_factory=list)
    storage_result: Optional[StorageResult] = None
    transformed_value: Any = None
    context_updates: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# DATA CAPTURE SERVICE
# =============================================================================

class DataCaptureService:
    """
    Handles validation, transformation, and storage of captured data.

    This is a deterministic service - no AI interpretation.
    All rules are explicit and verifiable.
    """

    # Built-in transformations
    TRANSFORMATIONS = {
        "boolean_from_yes_no": lambda x: str(x).lower() in ["yes", "true", "1"],
        "uppercase": lambda x: str(x).upper(),
        "lowercase": lambda x: str(x).lower(),
        "strip": lambda x: str(x).strip(),
        "to_int": lambda x: int(x) if x else None,
        "to_float": lambda x: float(x) if x else None,
        "array_from_csv": lambda x: [i.strip() for i in str(x).split(",") if i.strip()],
        "array_to_csv": lambda x: ",".join(x) if isinstance(x, list) else str(x),
        "json_merge": lambda x: x,  # Special handling in store method
    }

    def __init__(self, db_session=None):
        """
        Initialize the Data Capture Service.

        Args:
            db_session: SQLAlchemy database session (optional, for storage)
        """
        self.db_session = db_session

    # =========================================================================
    # VALIDATION
    # =========================================================================

    def validate(self, value: Any, rules: List[Dict]) -> List[ValidationResult]:
        """
        Validate input against all defined rules.

        Args:
            value: The value to validate
            rules: List of rule definitions from question JSON

        Returns:
            List of ValidationResult (empty if all valid)
        """
        errors = []

        for rule_def in rules:
            rule = ValidationRule(
                rule_type=rule_def.get("type"),
                params=rule_def.get("params", {})
            )
            result = self._apply_validation_rule(value, rule)
            if not result.valid:
                errors.append(result)

        return errors

    def _apply_validation_rule(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """
        Apply a single validation rule.

        Args:
            value: The value to validate
            rule: The validation rule to apply

        Returns:
            ValidationResult
        """
        str_value = str(value) if value is not None else ""

        if rule.rule_type == "required":
            if not value or not str_value.strip():
                return ValidationResult(
                    valid=False,
                    error=rule.params.get("error", "This field is required")
                )

        elif rule.rule_type == "min_length":
            min_len = rule.params.get("min", 0)
            if len(str_value) < min_len:
                return ValidationResult(
                    valid=False,
                    error=rule.params.get("error", f"Must be at least {min_len} characters")
                )

        elif rule.rule_type == "max_length":
            max_len = rule.params.get("max", float('inf'))
            if len(str_value) > max_len:
                return ValidationResult(
                    valid=False,
                    error=rule.params.get("error", f"Must be no more than {max_len} characters")
                )

        elif rule.rule_type == "pattern":
            pattern = rule.params.get("pattern", ".*")
            if not re.match(pattern, str_value):
                return ValidationResult(
                    valid=False,
                    error=rule.params.get("error", f"Must match pattern: {pattern}")
                )

        elif rule.rule_type == "allowed_values":
            allowed = rule.params.get("values", [])
            if str_value not in allowed and value not in allowed:
                return ValidationResult(
                    valid=False,
                    error=rule.params.get("error", f"Must be one of: {', '.join(allowed)}")
                )

        elif rule.rule_type == "min_selections":
            min_sel = rule.params.get("min", 1)
            if isinstance(value, list):
                if len(value) < min_sel:
                    return ValidationResult(
                        valid=False,
                        error=rule.params.get("error", f"Must select at least {min_sel} option(s)")
                    )
            elif not value:
                return ValidationResult(
                    valid=False,
                    error=rule.params.get("error", f"Must select at least {min_sel} option(s)")
                )

        elif rule.rule_type == "shall_statement":
            # DO-178C requirement format validation
            lower_value = str_value.lower()
            if "shall" not in lower_value:
                return ValidationResult(
                    valid=False,
                    error="Requirement must contain 'shall' statement"
                )
            # Check for compound requirements
            if " and " in lower_value and lower_value.count("shall") > 1:
                return ValidationResult(
                    valid=False,
                    error="Split compound requirements: only one 'shall' per requirement"
                )

        elif rule.rule_type == "numeric_range":
            try:
                num_value = float(value) if value else 0
                min_val = rule.params.get("min")
                max_val = rule.params.get("max")
                if min_val is not None and num_value < min_val:
                    return ValidationResult(
                        valid=False,
                        error=rule.params.get("error", f"Must be at least {min_val}")
                    )
                if max_val is not None and num_value > max_val:
                    return ValidationResult(
                        valid=False,
                        error=rule.params.get("error", f"Must be at most {max_val}")
                    )
            except (ValueError, TypeError):
                return ValidationResult(
                    valid=False,
                    error="Must be a valid number"
                )

        return ValidationResult(valid=True)

    # =========================================================================
    # TRANSFORMATION
    # =========================================================================

    def transform(self, value: Any, transformation: Optional[str]) -> Any:
        """
        Transform input value according to transformation rule.

        Args:
            value: The value to transform
            transformation: Name of transformation to apply

        Returns:
            Transformed value
        """
        if not transformation:
            return value

        if transformation in self.TRANSFORMATIONS:
            try:
                return self.TRANSFORMATIONS[transformation](value)
            except (ValueError, TypeError, AttributeError):
                return value

        return value

    # =========================================================================
    # STORAGE
    # =========================================================================

    def store(
        self,
        target: StorageTarget,
        project_id: int,
        record_id: Optional[int] = None
    ) -> StorageResult:
        """
        Store value in database.

        Args:
            target: StorageTarget with table, column, value
            project_id: Project ID for context
            record_id: Optional existing record ID for updates

        Returns:
            StorageResult
        """
        if not self.db_session:
            return StorageResult(
                success=False,
                error="No database session available"
            )

        try:
            # Transform value if needed
            transformed_value = self.transform(target.value, target.transformation)

            # Handle JSON merge specially
            if target.transformation == "json_merge" and target.json_path:
                return self._merge_json_field(
                    target.table,
                    target.column,
                    target.json_path,
                    transformed_value,
                    project_id,
                    record_id
                )

            # Regular column update
            return self._update_column(
                target.table,
                target.column,
                transformed_value,
                project_id,
                record_id
            )

        except Exception as e:
            return StorageResult(
                success=False,
                error=str(e)
            )

    def _update_column(
        self,
        table: str,
        column: str,
        value: Any,
        project_id: int,
        record_id: Optional[int] = None
    ) -> StorageResult:
        """Update a regular column value."""
        # This is a simplified implementation
        # In production, use SQLAlchemy ORM models

        if table == "projects":
            from models.project import Project
            project = self.db_session.query(Project).filter_by(id=project_id).first()
            if project:
                setattr(project, column, value)
                self.db_session.commit()
                return StorageResult(success=True, record_id=project.id)

        return StorageResult(
            success=False,
            error=f"Table '{table}' not supported for direct updates"
        )

    def _merge_json_field(
        self,
        table: str,
        column: str,
        json_path: str,
        value: Any,
        project_id: int,
        record_id: Optional[int] = None
    ) -> StorageResult:
        """Merge value into a JSON column at specified path."""

        if table == "projects":
            from models.project import Project
            project = self.db_session.query(Project).filter_by(id=project_id).first()
            if project:
                # Get existing JSON or create empty dict
                existing = getattr(project, column) or {}
                if isinstance(existing, str):
                    existing = json.loads(existing)

                # Merge new value at path
                existing[json_path] = value
                setattr(project, column, existing)
                self.db_session.commit()
                return StorageResult(success=True, record_id=project.id)

        return StorageResult(
            success=False,
            error=f"Table '{table}' not supported for JSON merge"
        )

    # =========================================================================
    # COMPLETE CAPTURE FLOW
    # =========================================================================

    def capture(
        self,
        value: Any,
        question_def: Dict,
        project_id: int,
        context: Dict[str, Any] = None
    ) -> CaptureResult:
        """
        Complete data capture flow: validate, transform, store.

        Args:
            value: The user's answer
            question_def: Question definition from JSON
            project_id: Project ID
            context: Current interview context

        Returns:
            CaptureResult with all outcomes
        """
        context = context or {}
        result = CaptureResult(valid=True, stored=False)

        # 1. Validate
        validation_rules = question_def.get("validation", {}).get("rules", [])
        errors = self.validate(value, validation_rules)

        if errors:
            result.valid = False
            result.validation_errors = errors
            return result

        # 2. Transform
        target_def = question_def.get("target", {})
        transformation = target_def.get("transformation")
        result.transformed_value = self.transform(value, transformation)

        # 3. Determine context updates from on_answer
        on_answer = question_def.get("on_answer", {})
        answer_action = on_answer.get(str(value)) or on_answer.get("default", {})
        result.context_updates = answer_action.get("set_context", {})

        # Replace $value placeholder with actual value
        for key, val in result.context_updates.items():
            if val == "$value":
                result.context_updates[key] = result.transformed_value

        # 4. Store (if database session available)
        if self.db_session and target_def.get("table"):
            target = StorageTarget(
                table=target_def["table"],
                column=target_def["column"],
                value=result.transformed_value,
                transformation=transformation,
                json_path=target_def.get("json_path")
            )

            storage_result = self.store(target, project_id)
            result.stored = storage_result.success
            result.storage_result = storage_result

        return result


# =============================================================================
# AUTO-POPULATION SERVICE
# =============================================================================

class AutoPopulationService:
    """
    Automatically populate fields based on rules.

    Used for generating IDs, default values, timestamps, etc.
    """

    def __init__(self, db_session=None):
        self.db_session = db_session
        self._sequence_cache = {}

    def populate_defaults(self, table: str, data: Dict) -> Dict:
        """
        Add auto-populated fields to data before insert.

        Args:
            table: Target table name
            data: Existing data dictionary

        Returns:
            Data with auto-populated fields added
        """
        # Common audit fields
        now = datetime.utcnow()
        data.setdefault("created_at", now)
        data.setdefault("updated_at", now)
        data.setdefault("version", 1)

        # GUID for hybrid ID system
        if "guid" not in data:
            data["guid"] = str(uuid.uuid4())

        # Table-specific auto-population
        if table == "requirements":
            data = self._populate_requirement_fields(data)
        elif table == "configuration_items":
            data = self._populate_ci_fields(data)
        elif table == "design_components":
            data = self._populate_design_fields(data)
        elif table == "projects":
            data = self._populate_project_fields(data)

        return data

    def _populate_requirement_fields(self, data: Dict) -> Dict:
        """Auto-populate requirement-specific fields."""
        # Generate requirement ID
        if "requirement_id" not in data or not data["requirement_id"]:
            req_type = data.get("type", "FN")[:2].upper()
            next_num = self._get_next_sequence("requirement", req_type)
            data["requirement_id"] = f"REQ-{req_type}-{next_num:03d}"

        # Default status
        data.setdefault("status", "draft")

        # Default display ID same as requirement_id
        data.setdefault("display_id", data.get("requirement_id"))

        return data

    def _populate_ci_fields(self, data: Dict) -> Dict:
        """Auto-populate CI-specific fields."""
        # Generate display ID
        if "display_id" not in data or not data["display_id"]:
            ci_type = data.get("ci_type", "").upper()[:2] or "CI"
            next_num = self._get_next_sequence("ci", ci_type)
            data["display_id"] = f"CI-{ci_type}-{next_num:04d}"

        # Default lifecycle phase
        data.setdefault("lifecycle_phase", "development")

        # Default baseline status
        data.setdefault("baseline_status", "none")

        return data

    def _populate_design_fields(self, data: Dict) -> Dict:
        """Auto-populate design component fields."""
        if "component_id" not in data or not data["component_id"]:
            comp_type = data.get("type", "CMP")[:3].upper()
            next_num = self._get_next_sequence("design", comp_type)
            data["component_id"] = f"DSN-{comp_type}-{next_num:03d}"

        data.setdefault("status", "draft")
        return data

    def _populate_project_fields(self, data: Dict) -> Dict:
        """Auto-populate project-specific fields."""
        if "project_code" not in data or not data["project_code"]:
            domain = data.get("domain", "PROJ")[:4].upper()
            year = datetime.now().year
            next_num = self._get_next_sequence("project", domain)
            data["project_code"] = f"{domain}-{year}-{next_num:03d}"

        data.setdefault("status", "active")
        return data

    def _get_next_sequence(self, entity_type: str, prefix: str) -> int:
        """Get next sequence number for an entity type and prefix."""
        key = f"{entity_type}_{prefix}"

        if key not in self._sequence_cache:
            # In production, query database for max existing value
            self._sequence_cache[key] = 0

        self._sequence_cache[key] += 1
        return self._sequence_cache[key]


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def validate_answer(value: Any, question_def: Dict) -> List[ValidationResult]:
    """
    Convenience function to validate an answer.

    Args:
        value: The answer value
        question_def: Question definition with validation rules

    Returns:
        List of validation errors (empty if valid)
    """
    service = DataCaptureService()
    rules = question_def.get("validation", {}).get("rules", [])
    return service.validate(value, rules)


def transform_answer(value: Any, question_def: Dict) -> Any:
    """
    Convenience function to transform an answer.

    Args:
        value: The answer value
        question_def: Question definition with transformation

    Returns:
        Transformed value
    """
    service = DataCaptureService()
    target = question_def.get("target", {})
    transformation = target.get("transformation")
    return service.transform(value, transformation)
