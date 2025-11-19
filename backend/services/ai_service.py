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

        Traceability:
        - REQ-AI-001: Single question interaction
        - REQ-AI-002: Simple language by default
        - REQ-AI-008: Requirements elicitation
        - REQ-AI-010: No design decisions

        Args:
            user_input: User's description or response
            context: Optional conversation context

        Returns:
            AI response with follow-up questions or extracted requirements
        """
        system_prompt = """You are a helpful assistant helping users capture requirements for their engineering projects.

CRITICAL RULES (DO-178C COMPLIANCE):

1. **SINGLE QUESTION ONLY (REQ-AI-001):**
   - Ask ONLY ONE question at a time
   - NEVER ask multiple questions simultaneously
   - NEVER present multiple tasks at once
   - Wait for user's answer before asking the next question

2. **SIMPLE LANGUAGE (REQ-AI-002):**
   - Use simple, everyday language by default
   - Avoid technical jargon unless the user uses it first
   - Explain concepts in plain terms
   - If you must use a technical term, explain it simply

3. **NO DESIGN DECISIONS (REQ-AI-010):**
   - NEVER make design decisions for the user
   - NEVER choose technical solutions without user input
   - ALWAYS offer options when choices exist
   - ASK questions to understand what the user wants
   - The user is the decision-maker, you are the assistant

Your role is to:
- Ask clarifying questions to understand what the user needs
- Help the user think through their requirements
- Listen carefully to their answers
- Guide them through the requirements capture process
- Present options, not decisions

When asking questions:
- Make them clear and easy to understand
- Focus on what the user wants their system to do
- Ask about the "why" to understand the real need
- Be patient and thorough

Example good questions:
- "What should happen when a user logs in?"
- "How should the system behave if there's an error?"
- "What information do you need to see on the dashboard?"

Example BAD (don't do this):
- "Should we use JWT or OAuth2?" (design decision)
- "What's the authentication flow and error handling strategy?" (multiple questions)
- "Implement RBAC with role-based authorization matrix" (technical jargon + decision)"""

        messages = [{"role": "user", "content": user_input}]
        if context:
            messages.insert(0, {"role": "assistant", "content": context})

        response = await self.provider.chat(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7
        )

        return response["content"]

    async def validate_single_question(self, ai_response: str) -> Dict[str, Any]:
        """
        Validate that AI response contains only one question.

        Traceability: REQ-AI-001 - Single question interaction

        Args:
            ai_response: The AI's response text

        Returns:
            Dict with validation results: {
                "valid": bool,
                "question_count": int,
                "issues": List[str]
            }
        """
        issues = []
        question_count = ai_response.count('?')

        # Check for multiple question marks
        if question_count > 1:
            issues.append(f"Multiple questions detected ({question_count} question marks)")

        # Check for common multi-question patterns
        multi_question_indicators = [
            " and ",
            " or ",
            "also",
            "additionally",
            "furthermore",
            "moreover"
        ]

        # Split by question marks and check each part
        question_parts = ai_response.split('?')
        for indicator in multi_question_indicators:
            if indicator in ai_response.lower() and question_count > 0:
                # This might indicate multiple questions combined
                pass  # Warning only, not strict validation

        return {
            "valid": question_count <= 1,
            "question_count": question_count,
            "issues": issues
        }

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

    async def project_initialization_interview(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Conduct structured project initialization interview.

        Traceability:
        - REQ-AI-032: Structured project interview
        - REQ-AI-033: Safety criticality determination
        - REQ-AI-034: Regulatory standards identification
        - REQ-AI-035: Development process selection

        Args:
            user_input: User's response to current question
            context: Current interview context including stage and collected data

        Returns:
            Dict containing:
            - next_question: AI's next question
            - stage: Current interview stage
            - extracted_data: Data extracted from user response
            - complete: Whether interview is finished
        """
        if context is None:
            context = {
                "stage": "initial",
                "data": {}
            }

        current_stage = context.get("stage", "initial")
        collected_data = context.get("data", {})

        # Define interview stages
        if current_stage == "initial":
            system_prompt = """You are helping to initialize a new systems engineering project.

Your job is to conduct a structured interview to gather critical project information.

INTERVIEW STAGES:
1. **Foundation Questions**: Safety criticality, DAL/SIL level, domain, product type
2. **Planning Questions**: Regulatory standards, development process, architecture
3. **Execution Questions**: Lifecycle phase, verification approach, team organization

CURRENT STAGE: INITIAL (Open-ended question)

Ask the user: "Can you describe the project as precisely as you can? If you want, you can provide me a list of requirements or any design information."

Listen carefully to their response and extract key information about:
- What they're building
- Whether it's safety-critical
- Industry/domain (aerospace, automotive, medical, etc.)
- Any standards they mention

After their response, you'll move to Foundation Questions."""

        elif current_stage == "foundation":
            system_prompt = f"""You are conducting the FOUNDATION stage of project initialization.

COLLECTED DATA SO FAR:
{collected_data}

FOUNDATION QUESTIONS (ask ONE at a time, following REQ-AI-001):
1. "Is this system safety-critical?" (Yes/No)
2. If safety-critical: "What is the required Development Assurance Level (DAL) or Safety Integrity Level (SIL)?"
   - DAL: A (highest) to D (lowest) for aerospace (DO-178C)
   - SIL: SIL-1 to SIL-4 for industrial (IEC 61508)
   - ASIL: ASIL-A to ASIL-D for automotive (ISO 26262)
3. "What industry or domain is this for?" (aerospace, automotive, medical, industrial, other)
4. "What type of product are you developing?" (software, hardware, system integration, etc.)

Extract information from the user's response and ask the NEXT foundation question.
When all foundation questions are answered, inform them you'll move to Planning Questions."""

        elif current_stage == "planning":
            system_prompt = f"""You are conducting the PLANNING stage of project initialization.

COLLECTED DATA SO FAR:
{collected_data}

PLANNING QUESTIONS (ask ONE at a time):
1. "Which regulatory standards apply to your project?"
   - Examples: DO-178C, DO-254, DO-160 (aerospace)
   - ISO 26262 (automotive), IEC 62304 (medical), IEC 61508 (industrial)
2. "What development process will you follow?"
   - V-model, iterative, agile-compliant, waterfall
3. "What is your system architecture approach?"
   - Monolithic, modular, microservices, layered, etc.
4. "Where will requirements come from?"
   - Customer specs, standards, internal definition, existing system

Extract information and ask the next planning question.
When done, move to Execution Questions."""

        elif current_stage == "execution":
            system_prompt = f"""You are conducting the EXECUTION stage of project initialization.

COLLECTED DATA SO FAR:
{collected_data}

EXECUTION QUESTIONS (ask ONE at a time):
1. "What lifecycle phase are you in?"
   - Concept, requirements, design, implementation, verification, certification, production
2. "What is your verification approach?"
   - Requirements-based testing, code coverage, formal methods, simulation
3. "How large is your team?"
   - Solo, small (2-5), medium (6-20), large (20+)

Extract information and ask the next execution question.
When all questions answered, summarize and mark interview as COMPLETE."""

        else:  # complete
            system_prompt = """Summarize the project initialization information and confirm with the user that everything is correct."""

        # Prepare messages for AI
        messages = [{"role": "user", "content": user_input}]

        response = await self.provider.chat(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7
        )

        # Parse response and determine next stage
        # This is simplified; in production, you'd want more sophisticated parsing
        next_stage = current_stage
        if "foundation" in current_stage and "planning" in response["content"].lower():
            next_stage = "planning"
        elif "planning" in current_stage and "execution" in response["content"].lower():
            next_stage = "execution"
        elif "execution" in current_stage and "complete" in response["content"].lower():
            next_stage = "complete"
        elif current_stage == "initial":
            next_stage = "foundation"

        return {
            "next_question": response["content"],
            "stage": next_stage,
            "complete": next_stage == "complete",
            "model": self.model if hasattr(self, 'model') else self.provider.get_model_name()
        }

    def get_current_model(self) -> str:
        """Get the current AI model name."""
        return self.provider.get_model_name()


# Global service instance
ai_service = AIService()
