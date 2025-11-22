"""
AI Context Loader Service
DO-178C Traceability: REQ-AI-046, REQ-AI-047, REQ-DOC-001

Purpose: Load and manage AI instruction context from AI_INSTRUCTION.md
Provides role-specific context snippets for AI prompts.
"""

import os
from typing import Dict, Optional
from pathlib import Path


class AIContextLoader:
    """
    Loads AI_INSTRUCTION.md and provides context snippets for AI prompts.

    Traceability:
    - REQ-AI-046: Context Snapshot Builder
    - REQ-AI-047: Dynamic System Prompt Construction
    - REQ-DOC-001: AI_INSTRUCTION.md creation and usage
    """

    def __init__(self):
        self._full_content: Optional[str] = None
        self._sections: Dict[str, str] = {}
        self._load_instruction_file()

    def _load_instruction_file(self):
        """Load AI_INSTRUCTION.md from project root."""
        # Try multiple possible paths
        possible_paths = [
            Path(__file__).parent.parent.parent / "AI_INSTRUCTION.md",  # backend/../AI_INSTRUCTION.md
            Path("/home/joiedelor/aiset/AI_INSTRUCTION.md"),
            Path("AI_INSTRUCTION.md"),
        ]

        for path in possible_paths:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    self._full_content = f.read()
                self._parse_sections()
                return

        # If not found, use embedded summary
        self._full_content = self._get_embedded_summary()
        self._sections = {"summary": self._full_content}

    def _parse_sections(self):
        """Parse the document into sections for selective loading."""
        if not self._full_content:
            return

        current_section = "header"
        current_content = []

        for line in self._full_content.split("\n"):
            if line.startswith("## ") and not line.startswith("## Document"):
                # Save previous section
                if current_content:
                    self._sections[current_section] = "\n".join(current_content)
                # Start new section
                current_section = line.replace("## ", "").strip().lower().replace(" ", "_")
                current_content = [line]
            else:
                current_content.append(line)

        # Save last section
        if current_content:
            self._sections[current_section] = "\n".join(current_content)

    def _get_embedded_summary(self) -> str:
        """Fallback summary if file not found."""
        return """
# AI_INSTRUCTION.md Summary

## Database Overview
- PostgreSQL 15+ with 47 tables
- Hybrid IDs: guid (UUID) + display_id (human-readable)
- All tables have: guid, display_id, created_at, updated_at, version

## Key Tables
- projects: Engineering projects with safety_critical, certification_level
- requirements: System requirements with type, priority, status
- configuration_items: Product structure (34+ fields)
- ai_conversations: AI chat sessions
- ai_messages: Individual messages with role (user/assistant/system)

## AI Behavior Rules
1. Ask ONE question at a time (REQ-AI-001)
2. Use simple language (REQ-AI-002)
3. Never make design decisions - propose options (REQ-AI-010)
4. Always ask for clarification when ambiguous (REQ-AI-013)

## Valid Enumerations
- requirement.type: functional, performance, safety, security, interface, operational
- requirement.priority: critical, high, medium, low
- requirement.status: draft, proposed, pending_review, approved, rejected, implemented, verified
- project.certification_level: DAL-A, DAL-B, DAL-C, DAL-D, SIL-1, SIL-2, SIL-3, SIL-4, None
"""

    def get_summary_context(self) -> str:
        """
        Get a condensed summary suitable for every AI call.
        ~500 tokens max.
        """
        return """
DATABASE KNOWLEDGE (from AI_INSTRUCTION.md):

CORE TABLES:
- projects: name, project_code, safety_critical (bool), certification_level (DAL-A/B/C/D, SIL-1/2/3/4)
- requirements: title, description, type, priority, status, verification_method
- configuration_items: ci_name, ci_type, part_number, 34+ metadata fields
- ai_conversations: project_guid, title, purpose, status
- ai_messages: conversation_guid, role (user/assistant), content

VALID VALUES:
- requirement.type: functional, performance, safety, security, interface, operational
- requirement.priority: critical, high, medium, low
- requirement.status: draft, proposed, approved, rejected, verified
- verification_method: test, analysis, inspection, demonstration

AI RULES (MUST FOLLOW):
1. Ask ONE question at a time
2. Use SIMPLE language
3. PROPOSE options, never DECIDE
4. Ask for CLARIFICATION when ambiguous
"""

    def get_requirements_context(self) -> str:
        """Get context for requirements elicitation."""
        return """
REQUIREMENTS EXTRACTION RULES (from AI_INSTRUCTION.md):

When extracting requirements, ALWAYS include:
- title: One-line summary
- description: Detailed statement using "shall" language
- type: functional/performance/safety/security/interface/operational
- priority: critical/high/medium/low
- confidence_score: Your confidence (0.0 to 1.0)

OPTIONAL but recommended:
- rationale: Why this requirement exists
- acceptance_criteria: How to verify
- verification_method: test/analysis/inspection/demonstration

EXAMPLE requirement format:
{
    "title": "Autopilot Engagement Time",
    "description": "The system shall engage the autopilot within 2 seconds of pilot command",
    "type": "functional",
    "priority": "critical",
    "status": "proposed",
    "rationale": "Timely engagement is critical for flight safety",
    "verification_method": "test",
    "confidence_score": 0.95
}

NEVER:
- Make design decisions for the user
- Auto-approve requirements
- Create requirements without user input
"""

    def get_project_context(self) -> str:
        """Get context for project initialization."""
        return """
PROJECT INITIALIZATION RULES (from AI_INSTRUCTION.md):

PROJECT FIELDS TO COLLECT:
- name: Project name
- project_code: Unique identifier (e.g., "FCS-2025")
- description: What the project does
- industry_sector: aerospace, automotive, medical, industrial, other
- safety_critical: true/false
- certification_level: DAL-A/B/C/D, SIL-1/2/3/4, or None
- lifecycle_phase: concept, requirements, design, implementation, verification, certification

VALID CERTIFICATION LEVELS:
- Aerospace (DO-178C): DAL-A (highest), DAL-B, DAL-C, DAL-D (lowest)
- Automotive (ISO 26262): ASIL-D (highest), ASIL-C, ASIL-B, ASIL-A (lowest)
- Industrial (IEC 61508): SIL-4 (highest), SIL-3, SIL-2, SIL-1 (lowest)
- Medical (IEC 62304): Class C (highest), Class B, Class A (lowest)
- Not safety-critical: None

VALID LIFECYCLE PHASES:
concept, requirements, architecture, design, implementation, verification, certification, production, maintenance

INTERVIEW APPROACH:
1. Ask about what they're building
2. Determine if safety-critical
3. Identify industry/domain
4. Determine applicable standards
5. Ask about current lifecycle phase
"""

    def get_ci_context(self) -> str:
        """Get context for Configuration Item management."""
        return """
CONFIGURATION ITEM RULES (from AI_INSTRUCTION.md):

CI FIELDS (34+ total, key ones):
- ci_identifier: Unique ID within project
- ci_name: Human-readable name
- ci_type: system, subsystem, assembly, component, part, software, hardware, document
- part_number: Manufacturing part number
- parent_guid: Reference to parent CI (for hierarchy)
- safety_classification: Safety-Critical, Safety-Related, Non-Safety
- certification_status: Certification state

VALID CI TYPES:
system, subsystem, assembly, component, part, software, hardware, document

BOM/PBS STRUCTURE:
- System (top level)
  - Subsystem
    - Assembly
      - Component
        - Part

MAKE/BUY DECISION:
make, buy, both, TBD
"""

    def get_full_content(self) -> str:
        """Get the complete AI_INSTRUCTION.md content."""
        return self._full_content or self._get_embedded_summary()

    def get_section(self, section_name: str) -> Optional[str]:
        """Get a specific section by name."""
        return self._sections.get(section_name.lower().replace(" ", "_"))


# Global singleton instance
ai_context_loader = AIContextLoader()
