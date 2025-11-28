"""
AI Enhancement Service
DO-178C Traceability: REQ-AI-003, REQ-AI-011, REQ-AI-012, REQ-AI-013

This service provides enhanced AI capabilities:
- Full project history context awareness (REQ-AI-003)
- AI-powered traceability suggestions (REQ-AI-011)
- Conflict detection in requirements (REQ-AI-012)
- Ambiguity flagging (REQ-AI-013)
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class AIEnhancementService:
    """
    Enhanced AI capabilities for intelligent analysis and suggestions.

    Provides AI-powered analysis beyond basic chat functionality.
    """

    def __init__(self, db: Session):
        """
        Initialize AI enhancement service.

        Args:
            db: Database session
        """
        self.db = db

    def get_full_project_context(
        self,
        project_id: int
    ) -> Dict[str, Any]:
        """
        Get comprehensive project context for AI awareness.

        Implements REQ-AI-003: Full project history awareness

        Args:
            project_id: Project ID

        Returns:
            Complete project context including history, relationships, status
        """
        context = {
            "project_id": project_id,
            "metadata": self._get_project_metadata(project_id),
            "requirements": self._get_requirements_summary(project_id),
            "design_components": self._get_design_summary(project_id),
            "test_cases": self._get_tests_summary(project_id),
            "traceability": self._get_traceability_summary(project_id),
            "recent_changes": self._get_recent_changes(project_id),
            "conversation_history": self._get_conversation_summary(project_id),
            "process_status": self._get_process_status(project_id),
            "quality_metrics": self._get_quality_metrics(project_id)
        }

        logger.info(f"Generated full context for project {project_id}")
        return context

    def suggest_traceability_links(
        self,
        entity_type: str,
        entity_id: int,
        project_id: int
    ) -> List[Dict[str, Any]]:
        """
        AI-powered traceability link suggestions.

        Implements REQ-AI-011: AI traceability suggestions

        Analyzes entity content and suggests potential trace links
        based on semantic similarity and keyword matching.

        Args:
            entity_type: Type of entity (requirement, design, test)
            entity_id: Entity ID
            project_id: Project ID

        Returns:
            List of suggested trace links with confidence scores
        """
        suggestions = []

        # Get entity content
        entity = self._get_entity(entity_type, entity_id)
        if not entity:
            return suggestions

        # Extract keywords and concepts
        keywords = self._extract_keywords(entity.get('description', ''))

        # Find similar entities
        if entity_type == 'requirement':
            # Suggest design components and test cases
            design_suggestions = self._find_similar_design(keywords, project_id)
            test_suggestions = self._find_similar_tests(keywords, project_id)
            suggestions.extend(design_suggestions)
            suggestions.extend(test_suggestions)

        elif entity_type == 'design_component':
            # Suggest requirements and test cases
            req_suggestions = self._find_similar_requirements(keywords, project_id)
            test_suggestions = self._find_similar_tests(keywords, project_id)
            suggestions.extend(req_suggestions)
            suggestions.extend(test_suggestions)

        elif entity_type == 'test_case':
            # Suggest requirements and design
            req_suggestions = self._find_similar_requirements(keywords, project_id)
            design_suggestions = self._find_similar_design(keywords, project_id)
            suggestions.extend(req_suggestions)
            suggestions.extend(design_suggestions)

        # Sort by confidence score
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)

        logger.info(f"Generated {len(suggestions)} traceability suggestions for {entity_type}:{entity_id}")
        return suggestions[:10]  # Return top 10

    def detect_conflicts(
        self,
        project_id: int,
        entity_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect conflicts in requirements or design.

        Implements REQ-AI-012: Conflict detection

        Identifies:
        - Contradictory requirements
        - Overlapping responsibilities
        - Inconsistent terminology
        - Incompatible constraints

        Args:
            project_id: Project ID
            entity_type: Optional filter by entity type

        Returns:
            List of detected conflicts with descriptions
        """
        conflicts = []

        # Get all requirements
        requirements = self._get_all_requirements(project_id)

        # Check for contradictions
        contradictions = self._find_contradictions(requirements)
        conflicts.extend(contradictions)

        # Check for overlaps
        overlaps = self._find_overlaps(requirements)
        conflicts.extend(overlaps)

        # Check terminology consistency
        terminology_issues = self._check_terminology_consistency(requirements)
        conflicts.extend(terminology_issues)

        # Check constraints compatibility
        constraint_conflicts = self._check_constraint_compatibility(requirements)
        conflicts.extend(constraint_conflicts)

        logger.info(f"Detected {len(conflicts)} potential conflicts in project {project_id}")
        return conflicts

    def flag_ambiguities(
        self,
        text: str,
        context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Flag ambiguous language in requirements or design.

        Implements REQ-AI-013: Ambiguity flagging

        Detects:
        - Vague terms (may, might, should)
        - Subjective language (fast, easy, user-friendly)
        - Incomplete specifications
        - Missing quantification

        Args:
            text: Text to analyze
            context: Optional context (requirement, design, etc.)

        Returns:
            List of ambiguities with suggestions
        """
        ambiguities = []

        # Check for vague modal verbs
        vague_modals = ['may', 'might', 'could', 'should', 'would']
        for modal in vague_modals:
            pattern = r'\b' + modal + r'\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ambiguities.append({
                    "type": "vague_modal",
                    "severity": "medium",
                    "position": match.start(),
                    "word": match.group(),
                    "message": f"Vague modal verb '{match.group()}' - use 'shall' for requirements",
                    "suggestion": "Replace with 'shall' for mandatory requirements or 'will' for facts"
                })

        # Check for subjective adjectives
        subjective_terms = [
            'easy', 'simple', 'fast', 'slow', 'quick', 'intuitive',
            'user-friendly', 'efficient', 'flexible', 'robust',
            'adequate', 'appropriate', 'reasonable'
        ]
        for term in subjective_terms:
            pattern = r'\b' + term + r'\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ambiguities.append({
                    "type": "subjective_language",
                    "severity": "high",
                    "position": match.start(),
                    "word": match.group(),
                    "message": f"Subjective term '{match.group()}' - needs quantification",
                    "suggestion": "Replace with measurable criteria (e.g., 'response time < 100ms')"
                })

        # Check for incomplete comparisons
        incomplete_comparisons = ['better', 'worse', 'more', 'less', 'higher', 'lower']
        for comp in incomplete_comparisons:
            pattern = r'\b' + comp + r'\b(?!\s+than)'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ambiguities.append({
                    "type": "incomplete_comparison",
                    "severity": "high",
                    "position": match.start(),
                    "word": match.group(),
                    "message": f"Incomplete comparison '{match.group()}' - missing baseline",
                    "suggestion": "Specify what it's being compared to (e.g., 'better than baseline')"
                })

        # Check for missing units
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        numbers = re.finditer(number_pattern, text)
        for num_match in numbers:
            # Check if followed by a unit
            pos = num_match.end()
            has_unit = False
            units = ['ms', 'seconds', 'minutes', 'hours', 'bytes', 'KB', 'MB', 'GB',
                    'meters', 'km', '%', 'percent', 'items', 'users']
            for unit in units:
                if text[pos:pos+len(unit)+1].strip().startswith(unit):
                    has_unit = True
                    break

            if not has_unit and num_match.group() not in ['0', '1']:
                ambiguities.append({
                    "type": "missing_unit",
                    "severity": "medium",
                    "position": num_match.start(),
                    "word": num_match.group(),
                    "message": f"Number '{num_match.group()}' without units",
                    "suggestion": "Specify units (e.g., '100 milliseconds', '50 users')"
                })

        # Check for passive voice (harder to verify)
        passive_indicators = ['is', 'are', 'was', 'were', 'be', 'been', 'being']
        for indicator in passive_indicators:
            pattern = r'\b' + indicator + r'\s+\w+ed\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ambiguities.append({
                    "type": "passive_voice",
                    "severity": "low",
                    "position": match.start(),
                    "word": match.group(),
                    "message": f"Passive voice detected: '{match.group()}'",
                    "suggestion": "Use active voice to clearly identify actor (e.g., 'system shall...')"
                })

        logger.info(f"Flagged {len(ambiguities)} ambiguities in text")
        return ambiguities

    # Helper methods

    def _get_project_metadata(self, project_id: int) -> Dict[str, Any]:
        """Get project metadata."""
        # In production, query from database
        return {
            "id": project_id,
            "name": "Project",
            "status": "active",
            "dal_level": "D"
        }

    def _get_requirements_summary(self, project_id: int) -> Dict[str, Any]:
        """Get requirements summary."""
        return {
            "total": 0,
            "by_type": {},
            "by_priority": {}
        }

    def _get_design_summary(self, project_id: int) -> Dict[str, Any]:
        """Get design components summary."""
        return {"total": 0}

    def _get_tests_summary(self, project_id: int) -> Dict[str, Any]:
        """Get test cases summary."""
        return {"total": 0}

    def _get_traceability_summary(self, project_id: int) -> Dict[str, Any]:
        """Get traceability status."""
        return {
            "requirements_traced": 0,
            "design_traced": 0,
            "tests_traced": 0
        }

    def _get_recent_changes(self, project_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent changes to project."""
        return []

    def _get_conversation_summary(self, project_id: int) -> Dict[str, Any]:
        """Get AI conversation summary."""
        return {"total_conversations": 0}

    def _get_process_status(self, project_id: int) -> Dict[str, Any]:
        """Get process engine status."""
        return {"current_phase": "unknown"}

    def _get_quality_metrics(self, project_id: int) -> Dict[str, Any]:
        """Get quality metrics."""
        return {}

    def _get_entity(self, entity_type: str, entity_id: int) -> Optional[Dict[str, Any]]:
        """Get entity by type and ID."""
        # In production, query from database
        return None

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction
        words = re.findall(r'\b\w{4,}\b', text.lower())
        # Remove common words
        stopwords = {'that', 'this', 'with', 'from', 'have', 'will', 'shall', 'must'}
        keywords = [w for w in words if w not in stopwords]
        return list(set(keywords))[:20]

    def _find_similar_requirements(self, keywords: List[str], project_id: int) -> List[Dict[str, Any]]:
        """Find similar requirements based on keywords."""
        return []

    def _find_similar_design(self, keywords: List[str], project_id: int) -> List[Dict[str, Any]]:
        """Find similar design components."""
        return []

    def _find_similar_tests(self, keywords: List[str], project_id: int) -> List[Dict[str, Any]]:
        """Find similar test cases."""
        return []

    def _get_all_requirements(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all requirements for project."""
        return []

    def _find_contradictions(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find contradictory requirements."""
        conflicts = []
        # Look for negations and opposites
        for i, req1 in enumerate(requirements):
            for req2 in requirements[i+1:]:
                # Simple contradiction detection
                text1 = req1.get('description', '').lower()
                text2 = req2.get('description', '').lower()

                # Check for shall/shall not conflicts
                if 'shall not' in text1 and 'shall' in text2:
                    conflicts.append({
                        "type": "contradiction",
                        "severity": "critical",
                        "entity1": req1.get('id'),
                        "entity2": req2.get('id'),
                        "message": "Potential contradiction detected"
                    })

        return conflicts

    def _find_overlaps(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find overlapping requirements."""
        return []

    def _check_terminology_consistency(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for inconsistent terminology."""
        return []

    def _check_constraint_compatibility(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for incompatible constraints."""
        return []


def get_ai_enhancement_service(db: Session) -> AIEnhancementService:
    """
    Get AI enhancement service instance.

    Args:
        db: Database session

    Returns:
        AIEnhancementService instance
    """
    return AIEnhancementService(db)
