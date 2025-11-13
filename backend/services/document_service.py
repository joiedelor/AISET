"""
Document Generation Service
DO-178C Traceability: REQ-SERVICE-004
Purpose: Generate certification documentation

This service generates DO-178C compliant documentation including
SRS, SDD, RTM, and test reports from the database.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import os
import hashlib
import logging

from models.project import Project
from models.requirement import Requirement
from models.design_component import DesignComponent
from models.test_case import TestCase
from models.document_export import DocumentExport, DocumentType, ExportFormat
from services.traceability_service import TraceabilityService
from config.settings import settings

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service for generating certification documents.

    Traceability:
    - REQ-DOC-002: Document generation
    - REQ-CERT-007: Certification artifacts
    """

    def __init__(self, db: Session):
        self.db = db
        self.traceability_service = TraceabilityService(db)

        # Initialize Jinja2 environment
        template_dir = settings.export_templates_dir
        if os.path.exists(template_dir):
            self.jinja_env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(['html', 'xml'])
            )
        else:
            logger.warning(f"Template directory not found: {template_dir}")
            self.jinja_env = None

    def generate_srs(
        self,
        project_id: int,
        generated_by: str = "system"
    ) -> DocumentExport:
        """
        Generate Software Requirements Specification (SRS).

        Traceability:
        - REQ-DOC-003: SRS generation
        - REQ-CERT-008: DO-178C SRS compliance

        Args:
            project_id: Project ID
            generated_by: User generating the document

        Returns:
            DocumentExport record
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        requirements = self.db.query(Requirement).filter(
            Requirement.project_id == project_id
        ).order_by(Requirement.requirement_id).all()

        # Prepare document data
        document_data = {
            "project": project,
            "requirements": requirements,
            "generated_at": datetime.utcnow(),
            "generated_by": generated_by,
            "document_type": "Software Requirements Specification",
            "document_id": f"SRS-{project.project_code}-{datetime.utcnow().strftime('%Y%m%d')}"
        }

        # Generate markdown content
        content = self._render_srs_markdown(document_data)

        # Save to file
        filename = f"SRS_{project.project_code}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
        file_path = os.path.join(settings.export_output_dir, filename)

        os.makedirs(settings.export_output_dir, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Calculate file hash
        file_hash = self._calculate_file_hash(file_path)

        # Create export record
        export = DocumentExport(
            project_id=project_id,
            document_type=DocumentType.SRS,
            export_format=ExportFormat.MARKDOWN,
            title=f"Software Requirements Specification - {project.name}",
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            file_hash=file_hash,
            generated_by=generated_by,
            included_requirements=[req.id for req in requirements],
            version="1.0"
        )

        self.db.add(export)
        self.db.commit()
        self.db.refresh(export)

        logger.info(f"Generated SRS for project {project_id}: {file_path}")
        return export

    def generate_rtm(
        self,
        project_id: int,
        generated_by: str = "system"
    ) -> DocumentExport:
        """
        Generate Requirements Traceability Matrix (RTM).

        Traceability:
        - REQ-DOC-004: RTM generation
        - REQ-CERT-009: DO-178C traceability compliance

        Args:
            project_id: Project ID
            generated_by: User generating the document

        Returns:
            DocumentExport record
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Get traceability matrix
        matrix_data = self.traceability_service.generate_traceability_matrix(project_id)

        # Prepare document data
        document_data = {
            "project": project,
            "matrix": matrix_data["matrix"],
            "statistics": matrix_data["statistics"],
            "generated_at": datetime.utcnow(),
            "generated_by": generated_by,
            "document_type": "Requirements Traceability Matrix",
            "document_id": f"RTM-{project.project_code}-{datetime.utcnow().strftime('%Y%m%d')}"
        }

        # Generate markdown content
        content = self._render_rtm_markdown(document_data)

        # Save to file
        filename = f"RTM_{project.project_code}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
        file_path = os.path.join(settings.export_output_dir, filename)

        os.makedirs(settings.export_output_dir, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Calculate file hash
        file_hash = self._calculate_file_hash(file_path)

        # Create export record
        export = DocumentExport(
            project_id=project_id,
            document_type=DocumentType.RTM,
            export_format=ExportFormat.MARKDOWN,
            title=f"Requirements Traceability Matrix - {project.name}",
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            file_hash=file_hash,
            generated_by=generated_by,
            version="1.0"
        )

        self.db.add(export)
        self.db.commit()
        self.db.refresh(export)

        logger.info(f"Generated RTM for project {project_id}: {file_path}")
        return export

    def _render_srs_markdown(self, data: Dict[str, Any]) -> str:
        """Render SRS as markdown."""
        content = f"""# Software Requirements Specification

**Project:** {data['project'].name}
**Project Code:** {data['project'].project_code}
**Certification Level:** DO-178C Level {data['project'].certification_level}
**Document ID:** {data['document_id']}
**Generated:** {data['generated_at'].strftime('%Y-%m-%d %H:%M:%S UTC')}
**Generated By:** {data['generated_by']}

---

## 1. Introduction

This Software Requirements Specification (SRS) defines the requirements for {data['project'].name}.

**Project Description:**
{data['project'].description or 'N/A'}

**Certification Level:**
This project is being developed to DO-178C Level {data['project'].certification_level}.

---

## 2. Requirements

Total Requirements: {len(data['requirements'])}

"""
        # Group requirements by type
        by_type = {}
        for req in data['requirements']:
            req_type = req.type.value
            if req_type not in by_type:
                by_type[req_type] = []
            by_type[req_type].append(req)

        for req_type, reqs in by_type.items():
            content += f"\n### 2.{list(by_type.keys()).index(req_type) + 1} {req_type.replace('_', ' ').title()} Requirements\n\n"

            for req in reqs:
                content += f"#### {req.requirement_id}: {req.title}\n\n"
                content += f"**Description:**  \n{req.description}\n\n"
                content += f"**Priority:** {req.priority.value.title()}  \n"
                content += f"**Status:** {req.status.value.replace('_', ' ').title()}  \n\n"

                if req.rationale:
                    content += f"**Rationale:**  \n{req.rationale}\n\n"

                if req.acceptance_criteria:
                    content += f"**Acceptance Criteria:**  \n{req.acceptance_criteria}\n\n"

                content += "---\n\n"

        content += f"""
## 3. Traceability

This SRS is part of a complete traceability system. See the Requirements Traceability Matrix (RTM) for links to design and test artifacts.

---

## 4. Document Control

**Version:** {data.get('version', '1.0')}
**Status:** Draft
**Approvals:** Pending

---

*This document was automatically generated by AISET (AI Systems Engineering Tool)*
"""
        return content

    def _render_rtm_markdown(self, data: Dict[str, Any]) -> str:
        """Render RTM as markdown."""
        stats = data['statistics']

        content = f"""# Requirements Traceability Matrix

**Project:** {data['project'].name}
**Project Code:** {data['project'].project_code}
**Document ID:** {data['document_id']}
**Generated:** {data['generated_at'].strftime('%Y-%m-%d %H:%M:%S UTC')}
**Generated By:** {data['generated_by']}

---

## Coverage Statistics

- **Total Requirements:** {stats['total_requirements']}
- **Fully Traced:** {stats['fully_traced']} ({stats['coverage_percentage']:.1f}%)
- **With Design Coverage:** {stats['with_design_coverage']} ({stats['design_coverage_percentage']:.1f}%)
- **With Test Coverage:** {stats['with_test_coverage']} ({stats['test_coverage_percentage']:.1f}%)

---

## Traceability Matrix

| Requirement ID | Title | Type | Priority | Design Components | Test Cases | Status |
|---------------|-------|------|----------|-------------------|------------|--------|
"""
        for row in data['matrix']:
            design_list = ', '.join([d['id'] for d in row['design_components']]) or '-'
            test_list = ', '.join([t['id'] for t in row['test_cases']]) or '-'
            status = '✓' if row['fully_traced'] else '⚠'

            content += f"| {row['requirement_id']} | {row['title'][:40]} | {row['type']} | {row['priority']} | {design_list} | {test_list} | {status} |\n"

        content += """

**Legend:**
✓ = Fully traced (has both design and test coverage)
⚠ = Incomplete traceability

---

*This document was automatically generated by AISET (AI Systems Engineering Tool)*
"""
        return content

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file for integrity verification."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
