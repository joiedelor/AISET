"""
Traceability Service
DO-178C Traceability: REQ-SERVICE-003
Purpose: Manage traceability links and gap detection

This service manages bidirectional traceability between requirements,
design components, and test cases as required by DO-178C.
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

from models.requirement import Requirement
from models.design_component import DesignComponent
from models.test_case import TestCase
from models.traceability import (
    RequirementDesignTrace,
    RequirementTestTrace,
    DesignTestTrace,
    TraceabilityGap,
    TraceType,
    GapType
)

logger = logging.getLogger(__name__)


class TraceabilityService:
    """
    Service for managing traceability relationships.

    Traceability:
    - REQ-TRACE-008: Traceability management
    - REQ-CERT-005: DO-178C traceability requirements
    """

    def __init__(self, db: Session):
        self.db = db

    def create_requirement_design_trace(
        self,
        requirement_id: int,
        design_component_id: int,
        trace_type: TraceType = TraceType.MANUAL,
        confidence_score: float = 1.0,
        rationale: Optional[str] = None,
        created_by: str = "system"
    ) -> RequirementDesignTrace:
        """
        Create traceability link between requirement and design.

        Traceability: REQ-TRACE-009 - Requirement-design linking

        Args:
            requirement_id: Requirement ID
            design_component_id: Design component ID
            trace_type: How the link was created
            confidence_score: Confidence in the link (for AI-suggested)
            rationale: Why this link exists
            created_by: User creating the link

        Returns:
            Created trace link
        """
        # Check if link already exists
        existing = self.db.query(RequirementDesignTrace).filter(
            and_(
                RequirementDesignTrace.requirement_id == requirement_id,
                RequirementDesignTrace.design_component_id == design_component_id
            )
        ).first()

        if existing:
            logger.warning(f"Trace link already exists between REQ-{requirement_id} and DESIGN-{design_component_id}")
            return existing

        trace = RequirementDesignTrace(
            requirement_id=requirement_id,
            design_component_id=design_component_id,
            trace_type=trace_type,
            confidence_score=confidence_score,
            rationale=rationale,
            created_by=created_by
        )

        self.db.add(trace)
        self.db.commit()
        self.db.refresh(trace)

        logger.info(f"Created requirement-design trace: REQ-{requirement_id} -> DESIGN-{design_component_id}")
        return trace

    def create_requirement_test_trace(
        self,
        requirement_id: int,
        test_case_id: int,
        trace_type: TraceType = TraceType.MANUAL,
        coverage_notes: Optional[str] = None,
        created_by: str = "system"
    ) -> RequirementTestTrace:
        """
        Create traceability link between requirement and test.

        Traceability: REQ-TRACE-010 - Requirement-test linking
        """
        existing = self.db.query(RequirementTestTrace).filter(
            and_(
                RequirementTestTrace.requirement_id == requirement_id,
                RequirementTestTrace.test_case_id == test_case_id
            )
        ).first()

        if existing:
            logger.warning(f"Trace link already exists between REQ-{requirement_id} and TEST-{test_case_id}")
            return existing

        trace = RequirementTestTrace(
            requirement_id=requirement_id,
            test_case_id=test_case_id,
            trace_type=trace_type,
            coverage_notes=coverage_notes,
            created_by=created_by
        )

        self.db.add(trace)
        self.db.commit()
        self.db.refresh(trace)

        logger.info(f"Created requirement-test trace: REQ-{requirement_id} -> TEST-{test_case_id}")
        return trace

    def create_design_test_trace(
        self,
        design_component_id: int,
        test_case_id: int,
        trace_type: TraceType = TraceType.MANUAL,
        created_by: str = "system"
    ) -> DesignTestTrace:
        """
        Create traceability link between design and test.

        Traceability: REQ-TRACE-011 - Design-test linking
        """
        existing = self.db.query(DesignTestTrace).filter(
            and_(
                DesignTestTrace.design_component_id == design_component_id,
                DesignTestTrace.test_case_id == test_case_id
            )
        ).first()

        if existing:
            logger.warning(f"Trace link already exists between DESIGN-{design_component_id} and TEST-{test_case_id}")
            return existing

        trace = DesignTestTrace(
            design_component_id=design_component_id,
            test_case_id=test_case_id,
            trace_type=trace_type,
            created_by=created_by
        )

        self.db.add(trace)
        self.db.commit()
        self.db.refresh(trace)

        logger.info(f"Created design-test trace: DESIGN-{design_component_id} -> TEST-{test_case_id}")
        return trace

    def get_requirement_coverage(self, requirement_id: int) -> Dict[str, Any]:
        """
        Get complete coverage analysis for a requirement.

        Traceability: REQ-TRACE-012 - Coverage analysis

        Returns:
            Dict with design and test coverage information
        """
        requirement = self.db.query(Requirement).filter(Requirement.id == requirement_id).first()

        if not requirement:
            raise ValueError(f"Requirement {requirement_id} not found")

        # Get linked design components
        design_traces = self.db.query(RequirementDesignTrace).filter(
            RequirementDesignTrace.requirement_id == requirement_id
        ).all()

        # Get linked test cases
        test_traces = self.db.query(RequirementTestTrace).filter(
            RequirementTestTrace.requirement_id == requirement_id
        ).all()

        has_design_coverage = len(design_traces) > 0
        has_test_coverage = len(test_traces) > 0

        return {
            "requirement_id": requirement.requirement_id,
            "has_design_coverage": has_design_coverage,
            "design_count": len(design_traces),
            "has_test_coverage": has_test_coverage,
            "test_count": len(test_traces),
            "is_fully_traced": has_design_coverage and has_test_coverage,
            "design_components": [trace.design_component_id for trace in design_traces],
            "test_cases": [trace.test_case_id for trace in test_traces]
        }

    def detect_gaps(self, project_id: int) -> List[TraceabilityGap]:
        """
        Detect traceability gaps in a project.

        Traceability:
        - REQ-TRACE-013: Gap detection
        - REQ-QA-002: Quality assurance

        Args:
            project_id: Project ID to analyze

        Returns:
            List of detected gaps
        """
        gaps = []

        # Find requirements without design
        requirements = self.db.query(Requirement).filter(Requirement.project_id == project_id).all()
        for req in requirements:
            design_traces = self.db.query(RequirementDesignTrace).filter(
                RequirementDesignTrace.requirement_id == req.id
            ).count()

            if design_traces == 0:
                gap = TraceabilityGap(
                    project_id=project_id,
                    gap_type=GapType.MISSING_DESIGN,
                    severity="high" if req.priority.value in ["critical", "high"] else "medium",
                    description=f"Requirement {req.requirement_id} has no design implementation",
                    requirement_id=req.id,
                    detection_method="automated_scan"
                )
                gaps.append(gap)

        # Find requirements without tests
        for req in requirements:
            test_traces = self.db.query(RequirementTestTrace).filter(
                RequirementTestTrace.requirement_id == req.id
            ).count()

            if test_traces == 0:
                gap = TraceabilityGap(
                    project_id=project_id,
                    gap_type=GapType.MISSING_TEST,
                    severity="critical" if req.priority.value == "critical" else "high",
                    description=f"Requirement {req.requirement_id} has no test coverage",
                    requirement_id=req.id,
                    detection_method="automated_scan"
                )
                gaps.append(gap)

        # Find orphan design components
        designs = self.db.query(DesignComponent).filter(DesignComponent.project_id == project_id).all()
        for design in designs:
            req_traces = self.db.query(RequirementDesignTrace).filter(
                RequirementDesignTrace.design_component_id == design.id
            ).count()

            if req_traces == 0:
                gap = TraceabilityGap(
                    project_id=project_id,
                    gap_type=GapType.ORPHAN_DESIGN,
                    severity="medium",
                    description=f"Design component {design.component_id} has no requirement traceability",
                    design_component_id=design.id,
                    detection_method="automated_scan"
                )
                gaps.append(gap)

        # Find orphan test cases
        tests = self.db.query(TestCase).filter(TestCase.project_id == project_id).all()
        for test in tests:
            req_traces = self.db.query(RequirementTestTrace).filter(
                RequirementTestTrace.test_case_id == test.id
            ).count()

            if req_traces == 0:
                gap = TraceabilityGap(
                    project_id=project_id,
                    gap_type=GapType.ORPHAN_TEST,
                    severity="low",
                    description=f"Test case {test.test_id} has no requirement traceability",
                    test_case_id=test.id,
                    detection_method="automated_scan"
                )
                gaps.append(gap)

        # Save all detected gaps
        for gap in gaps:
            self.db.add(gap)

        self.db.commit()

        logger.info(f"Detected {len(gaps)} traceability gaps for project {project_id}")
        return gaps

    def generate_traceability_matrix(self, project_id: int) -> Dict[str, Any]:
        """
        Generate complete traceability matrix for a project.

        Traceability:
        - REQ-TRACE-014: Traceability matrix generation
        - REQ-CERT-006: Certification artifact

        Returns:
            Complete traceability matrix data
        """
        requirements = self.db.query(Requirement).filter(Requirement.project_id == project_id).all()

        matrix = []
        for req in requirements:
            # Get all traces
            design_traces = self.db.query(RequirementDesignTrace).filter(
                RequirementDesignTrace.requirement_id == req.id
            ).all()

            test_traces = self.db.query(RequirementTestTrace).filter(
                RequirementTestTrace.requirement_id == req.id
            ).all()

            # Get design components
            design_components = []
            for trace in design_traces:
                design = self.db.query(DesignComponent).filter(DesignComponent.id == trace.design_component_id).first()
                if design:
                    design_components.append({
                        "id": design.component_id,
                        "name": design.name,
                        "trace_type": trace.trace_type.value
                    })

            # Get test cases
            test_cases = []
            for trace in test_traces:
                test = self.db.query(TestCase).filter(TestCase.id == trace.test_case_id).first()
                if test:
                    test_cases.append({
                        "id": test.test_id,
                        "title": test.title,
                        "status": test.status.value,
                        "trace_type": trace.trace_type.value
                    })

            matrix.append({
                "requirement_id": req.requirement_id,
                "title": req.title,
                "type": req.type.value,
                "priority": req.priority.value,
                "status": req.status.value,
                "design_components": design_components,
                "test_cases": test_cases,
                "design_coverage": len(design_components) > 0,
                "test_coverage": len(test_cases) > 0,
                "fully_traced": len(design_components) > 0 and len(test_cases) > 0
            })

        # Calculate statistics
        total_requirements = len(matrix)
        fully_traced = sum(1 for row in matrix if row["fully_traced"])
        with_design = sum(1 for row in matrix if row["design_coverage"])
        with_tests = sum(1 for row in matrix if row["test_coverage"])

        return {
            "matrix": matrix,
            "statistics": {
                "total_requirements": total_requirements,
                "fully_traced": fully_traced,
                "with_design_coverage": with_design,
                "with_test_coverage": with_tests,
                "coverage_percentage": (fully_traced / total_requirements * 100) if total_requirements > 0 else 0,
                "design_coverage_percentage": (with_design / total_requirements * 100) if total_requirements > 0 else 0,
                "test_coverage_percentage": (with_tests / total_requirements * 100) if total_requirements > 0 else 0
            }
        }
