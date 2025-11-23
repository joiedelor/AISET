"""
Artifact Generator for AISET Process Engine

This module generates documents from Jinja2 templates and database data.
It is part of the "Codification of the Systems Engineer" - providing
deterministic document generation.

Key Features:
- Template-based document generation
- Query database for data
- Apply filters and transformations
- Track generated documents

Traceability: REQ-AG-001 to REQ-AG-005
"""

import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from jinja2 import Environment, FileSystemLoader, select_autoescape


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class GeneratedDocument:
    """A generated document"""
    document_id: str
    document_type: str
    title: str
    content: str
    version: int
    template_id: str
    template_version: str
    source_data_hash: str
    generated_at: datetime
    status: str = "draft"
    project_id: Optional[int] = None
    ci_id: Optional[int] = None


# =============================================================================
# ARTIFACT GENERATOR SERVICE
# =============================================================================

class ArtifactGeneratorService:
    """
    Generates documents from templates and database data.

    This is a deterministic generator - all content comes from
    templates and stored data, not AI generation.
    """

    TEMPLATES_PATH = Path(__file__).parent.parent / "document_templates"

    def __init__(self, db_session=None):
        """
        Initialize the Artifact Generator.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        self.env = Environment(
            loader=FileSystemLoader(self.TEMPLATES_PATH),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self._register_filters()

    def _register_filters(self):
        """Register custom Jinja2 filters."""
        # Date formatting
        self.env.filters["date"] = lambda d: d.strftime("%Y-%m-%d") if d else ""
        self.env.filters["datetime"] = lambda d: d.strftime("%Y-%m-%d %H:%M:%S UTC") if d else ""

        # Text manipulation
        self.env.filters["truncate"] = lambda s, length=50: (s[:length] + "...") if s and len(s) > length else (s or "")

        # List formatting
        self.env.filters["join_ids"] = lambda items, attr="id": ", ".join(str(getattr(i, attr, i)) for i in items) if items else "-"

    # =========================================================================
    # DOCUMENT GENERATION
    # =========================================================================

    def generate_srs(self, project_id: int) -> GeneratedDocument:
        """
        Generate Software Requirements Specification.

        Args:
            project_id: Project ID

        Returns:
            GeneratedDocument
        """
        # Load data
        project = self._get_project(project_id)
        requirements = self._get_requirements(project_id)
        standards = self._get_project_standards(project_id)

        # Render template
        template = self.env.get_template("SRS_template.md")
        content = template.render(
            project=project,
            requirements=requirements,
            standards=standards,
            document={
                "version": self._get_next_doc_version(project_id, "SRS"),
                "generated_at": datetime.utcnow(),
                "status": "draft"
            }
        )

        # Create document record
        doc = GeneratedDocument(
            document_id=f"{project.project_code or 'PROJ'}-SRS-001",
            document_type="SRS",
            title=f"Software Requirements Specification - {project.name}",
            content=content,
            version=self._get_next_doc_version(project_id, "SRS"),
            template_id="SRS_template",
            template_version="1.0",
            source_data_hash=self._hash_source_data(requirements),
            generated_at=datetime.utcnow(),
            project_id=project_id
        )

        # Store if database available
        if self.db_session:
            self._store_document(doc)

        return doc

    def generate_traceability_matrix(self, project_id: int) -> GeneratedDocument:
        """
        Generate Requirements Traceability Matrix.

        Args:
            project_id: Project ID

        Returns:
            GeneratedDocument
        """
        # Load data
        project = self._get_project(project_id)
        requirements = self._get_requirements(project_id)
        traces = self._get_traceability_data(project_id)
        gaps = self._identify_gaps(project_id)
        coverage = self._calculate_coverage(project_id)

        # Render template
        template = self.env.get_template("RTM_template.md")
        content = template.render(
            project=project,
            requirements=requirements,
            traces=traces,
            gaps=gaps,
            coverage=coverage,
            document={
                "version": self._get_next_doc_version(project_id, "RTM"),
                "generated_at": datetime.utcnow(),
                "status": "draft"
            }
        )

        doc = GeneratedDocument(
            document_id=f"{project.project_code or 'PROJ'}-RTM-001",
            document_type="RTM",
            title=f"Requirements Traceability Matrix - {project.name}",
            content=content,
            version=self._get_next_doc_version(project_id, "RTM"),
            template_id="RTM_template",
            template_version="1.0",
            source_data_hash=self._hash_source_data(traces),
            generated_at=datetime.utcnow(),
            project_id=project_id
        )

        if self.db_session:
            self._store_document(doc)

        return doc

    def generate_gap_analysis(self, project_id: int) -> GeneratedDocument:
        """
        Generate Gap Analysis Report.

        Args:
            project_id: Project ID

        Returns:
            GeneratedDocument
        """
        # Load data
        project = self._get_project(project_id)
        gaps = {
            "requirements_without_design": self._find_unallocated_requirements(project_id),
            "requirements_without_tests": self._find_untested_requirements(project_id),
            "design_without_requirements": self._find_orphan_design(project_id),
            "orphan_tests": self._find_orphan_tests(project_id),
            "cis_without_requirements": self._find_unallocated_cis(project_id)
        }
        summary = self._summarize_gaps(project_id, gaps)

        # Render template
        template = self.env.get_template("Gap_Analysis_template.md")
        content = template.render(
            project=project,
            gaps=gaps,
            summary=summary,
            document={
                "version": self._get_next_doc_version(project_id, "GAP_ANALYSIS"),
                "generated_at": datetime.utcnow(),
                "status": "draft"
            }
        )

        doc = GeneratedDocument(
            document_id=f"{project.project_code or 'PROJ'}-GAP-001",
            document_type="GAP_ANALYSIS",
            title=f"Gap Analysis Report - {project.name}",
            content=content,
            version=self._get_next_doc_version(project_id, "GAP_ANALYSIS"),
            template_id="Gap_Analysis_template",
            template_version="1.0",
            source_data_hash=self._hash_source_data(gaps),
            generated_at=datetime.utcnow(),
            project_id=project_id
        )

        if self.db_session:
            self._store_document(doc)

        return doc

    # =========================================================================
    # DATA RETRIEVAL (to be connected to actual DB models)
    # =========================================================================

    def _get_project(self, project_id: int) -> Any:
        """Get project by ID."""
        if self.db_session:
            from models.project import Project
            return self.db_session.query(Project).filter_by(id=project_id).first()

        # Return mock for testing
        class MockProject:
            id = project_id
            name = "Test Project"
            project_code = "TEST-001"
            description = "A test project"
            domain = "aerospace"
            product_type = "software"
            safety_critical = True
            dal_level = "DAL_C"
            initialization_context = {}

        return MockProject()

    def _get_requirements(self, project_id: int) -> List[Any]:
        """Get requirements for a project."""
        if self.db_session:
            from models.requirement import Requirement
            return self.db_session.query(Requirement).filter_by(project_id=project_id).all()
        return []

    def _get_project_standards(self, project_id: int) -> List[Dict]:
        """Get standards associated with a project."""
        # This would query a standards mapping table
        # For now, return based on project context
        project = self._get_project(project_id)
        standards = []

        if hasattr(project, 'initialization_context') and project.initialization_context:
            ctx = project.initialization_context
            if isinstance(ctx, dict):
                applicable = ctx.get('applicable_standards', [])
                for std in applicable:
                    standards.append({
                        "name": std,
                        "version": "Latest",
                        "description": f"Applicable standard: {std}"
                    })

        return standards

    def _get_traceability_data(self, project_id: int) -> List[Dict]:
        """Get traceability data for a project."""
        if self.db_session:
            from models.traceability import RequirementDesignTrace, RequirementTestTrace
            req_design = self.db_session.query(RequirementDesignTrace).filter_by(project_id=project_id).all()
            req_test = self.db_session.query(RequirementTestTrace).filter_by(project_id=project_id).all()

            traces = []
            for t in req_design:
                traces.append({
                    "type": "requirement_design",
                    "requirement_id": t.requirement_id,
                    "design_ids": [t.design_component_id],
                    "trace_type": t.trace_type,
                    "status": t.status
                })
            for t in req_test:
                traces.append({
                    "type": "requirement_test",
                    "requirement_id": t.requirement_id,
                    "test_ids": [t.test_case_id],
                    "test_status": "Not Run",
                    "verification_method": "Test"
                })
            return traces
        return []

    def _identify_gaps(self, project_id: int) -> Dict:
        """Identify traceability gaps."""
        return {
            "requirements_without_design": self._find_unallocated_requirements(project_id),
            "requirements_without_tests": self._find_untested_requirements(project_id),
            "orphan_design": self._find_orphan_design(project_id),
            "orphan_tests": self._find_orphan_tests(project_id)
        }

    def _calculate_coverage(self, project_id: int) -> Dict:
        """Calculate coverage statistics."""
        requirements = self._get_requirements(project_id)
        traces = self._get_traceability_data(project_id)

        total = len(requirements)
        if total == 0:
            return {
                "total_requirements": 0,
                "with_design": 0,
                "with_tests": 0,
                "fully_traced": 0,
                "design_coverage": 0,
                "test_coverage": 0,
                "full_coverage": 0
            }

        reqs_with_design = set()
        reqs_with_tests = set()

        for trace in traces:
            if trace.get("type") == "requirement_design":
                reqs_with_design.add(trace.get("requirement_id"))
            elif trace.get("type") == "requirement_test":
                reqs_with_tests.add(trace.get("requirement_id"))

        fully_traced = reqs_with_design & reqs_with_tests

        return {
            "total_requirements": total,
            "with_design": len(reqs_with_design),
            "with_tests": len(reqs_with_tests),
            "fully_traced": len(fully_traced),
            "design_coverage": round(len(reqs_with_design) / total * 100, 1),
            "test_coverage": round(len(reqs_with_tests) / total * 100, 1),
            "full_coverage": round(len(fully_traced) / total * 100, 1)
        }

    def _find_unallocated_requirements(self, project_id: int) -> List[Dict]:
        """Find requirements without design allocation."""
        requirements = self._get_requirements(project_id)
        traces = self._get_traceability_data(project_id)

        traced_req_ids = {t.get("requirement_id") for t in traces if t.get("type") == "requirement_design"}
        unallocated = []

        for req in requirements:
            req_id = getattr(req, 'id', None) or req.get('id')
            if req_id not in traced_req_ids:
                unallocated.append({
                    "requirement_id": getattr(req, 'requirement_id', req_id),
                    "title": getattr(req, 'title', 'Untitled'),
                    "type": getattr(req, 'type', 'functional'),
                    "priority": getattr(req, 'priority', 'Medium')
                })

        return unallocated

    def _find_untested_requirements(self, project_id: int) -> List[Dict]:
        """Find requirements without test coverage."""
        requirements = self._get_requirements(project_id)
        traces = self._get_traceability_data(project_id)

        tested_req_ids = {t.get("requirement_id") for t in traces if t.get("type") == "requirement_test"}
        untested = []

        for req in requirements:
            req_id = getattr(req, 'id', None) or req.get('id')
            if req_id not in tested_req_ids:
                untested.append({
                    "requirement_id": getattr(req, 'requirement_id', req_id),
                    "title": getattr(req, 'title', 'Untitled'),
                    "verification_method": getattr(req, 'verification_method', 'Test'),
                    "priority": getattr(req, 'priority', 'Medium')
                })

        return untested

    def _find_orphan_design(self, project_id: int) -> List[Dict]:
        """Find design components without requirements."""
        # Would query design_components and check against traces
        return []

    def _find_orphan_tests(self, project_id: int) -> List[Dict]:
        """Find test cases without requirements."""
        # Would query test_cases and check against traces
        return []

    def _find_unallocated_cis(self, project_id: int) -> List[Dict]:
        """Find CIs without requirements."""
        # Would query configuration_items and check against allocations
        return []

    def _summarize_gaps(self, project_id: int, gaps: Dict) -> Dict:
        """Create summary statistics for gaps."""
        coverage = self._calculate_coverage(project_id)
        requirements = self._get_requirements(project_id)

        # Count by type
        functional_count = sum(1 for r in requirements if getattr(r, 'type', 'functional') == 'functional')
        safety_count = sum(1 for r in requirements if getattr(r, 'type', '') == 'safety')

        return {
            "total_requirements": len(requirements),
            "functional_count": functional_count,
            "non_functional_count": len(requirements) - functional_count,
            "safety_count": safety_count,
            "reqs_with_design": coverage["with_design"],
            "reqs_without_design": len(gaps.get("requirements_without_design", [])),
            "reqs_with_tests": coverage["with_tests"],
            "reqs_without_tests": len(gaps.get("requirements_without_tests", [])),
            "fully_traced": coverage["fully_traced"],
            "not_fully_traced": coverage["total_requirements"] - coverage["fully_traced"],
            "design_coverage": coverage["design_coverage"],
            "test_coverage": coverage["test_coverage"],
            "full_trace_coverage": coverage["full_coverage"]
        }

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def _get_next_doc_version(self, project_id: int, doc_type: str) -> int:
        """Get next version number for a document type."""
        if self.db_session:
            # Query max version from generated_documents
            # For now, return 1
            pass
        return 1

    def _hash_source_data(self, data: Any) -> str:
        """Create hash of source data for change detection."""
        import json
        try:
            if isinstance(data, list):
                # Convert objects to dicts if needed
                serializable = []
                for item in data:
                    if hasattr(item, '__dict__'):
                        serializable.append(str(item.__dict__))
                    elif isinstance(item, dict):
                        serializable.append(str(item))
                    else:
                        serializable.append(str(item))
                data_str = json.dumps(serializable, sort_keys=True)
            else:
                data_str = str(data)
            return hashlib.sha256(data_str.encode()).hexdigest()[:16]
        except Exception:
            return hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()[:16]

    def _store_document(self, doc: GeneratedDocument) -> int:
        """Store generated document in database."""
        # This would insert into generated_documents table
        # For now, just return a mock ID
        return 1


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def generate_document(
    project_id: int,
    doc_type: str,
    db_session=None
) -> GeneratedDocument:
    """
    Convenience function to generate a document.

    Args:
        project_id: Project ID
        doc_type: Document type (SRS, RTM, GAP_ANALYSIS)
        db_session: Optional database session

    Returns:
        GeneratedDocument
    """
    generator = ArtifactGeneratorService(db_session)

    generators = {
        "SRS": generator.generate_srs,
        "RTM": generator.generate_traceability_matrix,
        "GAP_ANALYSIS": generator.generate_gap_analysis
    }

    gen_func = generators.get(doc_type.upper())
    if not gen_func:
        raise ValueError(f"Unknown document type: {doc_type}")

    return gen_func(project_id)


def list_available_templates() -> List[Dict]:
    """List available document templates."""
    templates_path = ArtifactGeneratorService.TEMPLATES_PATH
    templates = []

    if templates_path.exists():
        for template_file in templates_path.glob("*.md"):
            name = template_file.stem
            templates.append({
                "template_id": name,
                "name": name.replace("_template", "").replace("_", " ").title(),
                "file": template_file.name
            })

    return templates
