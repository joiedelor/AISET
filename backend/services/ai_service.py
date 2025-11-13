"""
AI Service
DO-178C Traceability: REQ-SERVICE-001
Purpose: Unified AI service supporting Claude and LM Studio

This service provides a unified interface for AI interactions,
supporting both cloud-based (Claude) and local (LM Studio) models.
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import anthropic
import httpx
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """
    Abstract base class for AI providers.

    Traceability: REQ-AI-004 - AI provider abstraction
    """

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """Send chat messages and receive response."""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the current model name."""
        pass


class ClaudeProvider(AIProvider):
    """
    Anthropic Claude AI provider.

    Traceability:
    - REQ-AI-005: Claude API integration
    - REQ-CLOUD-001: Cloud AI service
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Send chat messages to Claude.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response

        Returns:
            Dict containing response text and metadata
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt if system_prompt else "",
                messages=messages
            )

            return {
                "content": response.content[0].text,
                "model": self.model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "stop_reason": response.stop_reason
            }

        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            raise

    def get_model_name(self) -> str:
        return self.model


class LMStudioProvider(AIProvider):
    """
    LM Studio local AI provider.

    Traceability:
    - REQ-AI-006: Local AI integration
    - REQ-OFFLINE-001: Offline AI capability
    """

    def __init__(self):
        self.base_url = settings.lm_studio_url
        self.model = settings.lm_studio_model

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Send chat messages to LM Studio.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response

        Returns:
            Dict containing response text and metadata
        """
        try:
            # Prepend system message if provided
            full_messages = messages.copy()
            if system_prompt:
                full_messages.insert(0, {"role": "system", "content": system_prompt})

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json={
                        "model": self.model,
                        "messages": full_messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "content": data["choices"][0]["message"]["content"],
                    "model": self.model,
                    "tokens_used": data.get("usage", {}).get("total_tokens", 0),
                    "stop_reason": data["choices"][0].get("finish_reason", "stop")
                }

        except Exception as e:
            logger.error(f"LM Studio API error: {str(e)}")
            raise

    def get_model_name(self) -> str:
        return self.model


class AIService:
    """
    Unified AI service with provider switching.

    Traceability:
    - REQ-AI-007: Unified AI interface
    - REQ-CONFIG-003: AI provider configuration
    """

    def __init__(self):
        self.provider = self._initialize_provider()

    def _initialize_provider(self) -> AIProvider:
        """Initialize the configured AI provider."""
        if settings.ai_service == "claude":
            logger.info("Initializing Claude AI provider")
            return ClaudeProvider()
        elif settings.ai_service == "lmstudio":
            logger.info("Initializing LM Studio AI provider")
            return LMStudioProvider()
        else:
            raise ValueError(f"Unknown AI service: {settings.ai_service}")

    async def requirements_elicitation(
        self,
        user_input: str,
        context: Optional[str] = None
    ) -> str:
        """
        Elicit requirements from user input.

        Traceability: REQ-AI-008 - Requirements elicitation

        Args:
            user_input: User's description or response
            context: Optional conversation context

        Returns:
            AI response with follow-up questions or extracted requirements
        """
        system_prompt = """You are an expert systems engineer helping to elicit requirements for safety-critical systems.

Your role is to:
1. Ask clarifying questions to understand system requirements
2. Extract structured requirements following IEEE 29148 standards
3. Ensure requirements are clear, testable, and traceable
4. Identify functional, performance, safety, and interface requirements

Follow DO-178C guidelines for requirements quality:
- Each requirement must be clear and unambiguous
- Requirements must be verifiable through testing
- Use standard requirement templates
- Maintain traceability to stakeholder needs

When you identify a complete requirement, format it clearly with:
- Type (functional, performance, safety, etc.)
- Description
- Acceptance criteria
- Priority level"""

        messages = [{"role": "user", "content": user_input}]
        if context:
            messages.insert(0, {"role": "assistant", "content": context})

        response = await self.provider.chat(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7
        )

        return response["content"]

    async def extract_requirements(
        self,
        conversation_text: str
    ) -> List[Dict[str, Any]]:
        """
        Extract structured requirements from conversation.

        Traceability: REQ-AI-009 - Requirement extraction

        Args:
            conversation_text: Full conversation text

        Returns:
            List of extracted requirements with metadata
        """
        system_prompt = """Extract all requirements from the provided conversation.

For each requirement, provide:
1. Title: Brief one-line description
2. Description: Detailed requirement statement
3. Type: functional, performance, safety, security, interface, operational, design_constraint, or data
4. Priority: critical, high, medium, or low
5. Acceptance Criteria: How to verify this requirement
6. Confidence Score: Your confidence in this extraction (0.0 to 1.0)

Return ONLY a JSON array of requirements. Example format:
[
  {
    "title": "System shall authenticate users",
    "description": "The system shall verify user credentials before granting access",
    "type": "security",
    "priority": "high",
    "acceptance_criteria": "User cannot access system without valid credentials",
    "confidence_score": 0.95
  }
]"""

        messages = [{"role": "user", "content": f"Extract requirements from:\n\n{conversation_text}"}]

        response = await self.provider.chat(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temperature for more consistent extraction
            max_tokens=4096
        )

        # Parse JSON response
        import json
        try:
            requirements = json.loads(response["content"])
            return requirements
        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON")
            return []

    async def suggest_traceability(
        self,
        requirement_text: str,
        design_components: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Suggest traceability links between requirements and design.

        Traceability: REQ-AI-010 - Traceability suggestion

        Args:
            requirement_text: Requirement description
            design_components: List of available design components

        Returns:
            List of suggested links with confidence scores
        """
        components_text = "\n".join([
            f"- {comp['component_id']}: {comp['name']} - {comp['description']}"
            for comp in design_components
        ])

        system_prompt = """You are analyzing traceability between requirements and design components.

Identify which design components implement the given requirement.
For each match, provide a confidence score (0.0 to 1.0) and rationale.

Return ONLY a JSON array. Example:
[
  {
    "component_id": "COMP-AI-001",
    "confidence_score": 0.85,
    "rationale": "This component directly implements the authentication logic"
  }
]"""

        messages = [{
            "role": "user",
            "content": f"Requirement: {requirement_text}\n\nDesign Components:\n{components_text}"
        }]

        response = await self.provider.chat(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.3
        )

        import json
        try:
            suggestions = json.loads(response["content"])
            return suggestions
        except json.JSONDecodeError:
            logger.error("Failed to parse traceability suggestions")
            return []

    def get_current_model(self) -> str:
        """Get the current AI model name."""
        return self.provider.get_model_name()


# Global service instance
ai_service = AIService()
