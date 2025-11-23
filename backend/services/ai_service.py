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
from services.ai_context_loader import ai_context_loader

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
            # Build messages - some models only support user/assistant roles
            # So we prepend system prompt to the first user message instead
            full_messages = messages.copy()
            if system_prompt and full_messages:
                # Find first user message and prepend system context
                for i, msg in enumerate(full_messages):
                    if msg["role"] == "user":
                        full_messages[i] = {
                            "role": "user",
                            "content": f"[System Instructions]\n{system_prompt}\n\n[User Message]\n{msg['content']}"
                        }
                        break
                else:
                    # No user message found, add system as user message
                    full_messages.insert(0, {"role": "user", "content": system_prompt})

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json={
                        "model": self.model,
                        "messages": full_messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=180.0  # 3 minutes for slower local models
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
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[str] = None
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
            conversation_history: Full conversation history for AI memory

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
                "data": {},
                "answered": []  # Track which questions have been answered
            }

        current_stage = context.get("stage", "initial")
        collected_data = context.get("data", {})
        answered_questions = context.get("answered", [])

        # Define all interview questions with their IDs
        FOUNDATION_QUESTIONS = ["safety_critical", "industry", "product_type"]
        PLANNING_QUESTIONS = ["standards", "dev_process", "architecture", "req_source"]
        EXECUTION_QUESTIONS = ["lifecycle_phase", "verification", "team_size"]

        # Check if using local LM Studio (needs shorter prompts)
        is_local_model = settings.ai_service == "lmstudio"

        # Build conversation context - shorter for local models
        history_context = ""
        if conversation_history and not is_local_model:
            history_context = f"""
PREVIOUS CONVERSATION:
{conversation_history}

Remember what the user told you above. Acknowledge their answer briefly.
"""

        # Get AI instruction context - skip for local models to reduce token count
        ai_instruction_context = "" if is_local_model else ai_context_loader.get_project_context()

        # Determine what to ask next based on stage and answered questions
        next_question_id = None

        if current_stage == "initial":
            # Initial stage - just acknowledge and move to foundation
            if is_local_model:
                system_prompt = "You are a project setup assistant. Acknowledge the user's project briefly, then ask: Is this safety-critical? (Yes/No). Be SHORT."
            else:
                system_prompt = f"""You are the AISET project initialization assistant.

{ai_instruction_context}

{history_context}

The user described their project. Briefly acknowledge what they said (1 sentence),
then ask: "Is this a safety-critical system that could cause harm if it fails?" (Yes/No)

Keep your response SHORT - 2-3 sentences max."""
            next_question_id = "safety_critical"

        elif current_stage == "foundation":
            # Find next unanswered foundation question
            for q in FOUNDATION_QUESTIONS:
                if q not in answered_questions:
                    next_question_id = q
                    break

            if is_local_model:
                # Compact prompts for local models
                if next_question_id == "safety_critical":
                    system_prompt = "Ask: Is this safety-critical? (Yes/No). SHORT."
                elif next_question_id == "industry":
                    system_prompt = "Acknowledge briefly. Ask: What industry? (aerospace/automotive/medical/industrial/other). SHORT."
                elif next_question_id == "product_type":
                    system_prompt = "Acknowledge briefly. Ask: Product type? (hardware/software/both). SHORT."
                else:
                    system_prompt = "Say: Moving to Planning. Ask: Any regulatory standards? (DO-178C/ISO/none). SHORT."
                    next_question_id = "standards"
            else:
                # Full prompts for cloud models
                base_context = f"""You are the AISET project initialization assistant.
{ai_instruction_context}
{history_context}
"""
                if next_question_id == "safety_critical":
                    system_prompt = f"""{base_context}
Ask the user: "Is this a safety-critical system?" (Yes/No)
Keep it SHORT."""
                elif next_question_id == "industry":
                    system_prompt = f"""{base_context}
Acknowledge their previous answer briefly. Then ask:
"What industry is this for?" (aerospace, automotive, medical, industrial, office/commercial, other)
Keep it SHORT."""
                elif next_question_id == "product_type":
                    system_prompt = f"""{base_context}
Acknowledge briefly. Then ask:
"What type of product is this?" (hardware, software, system/both)
Keep it SHORT."""
                else:
                    system_prompt = f"""{base_context}
Say: "Great! Moving to Planning Questions."
Then ask: "Do any regulatory standards apply to this project?" (e.g., DO-178C, ISO standards, or "none")
Keep it SHORT."""
                    next_question_id = "standards"

        elif current_stage == "planning":
            for q in PLANNING_QUESTIONS:
                if q not in answered_questions:
                    next_question_id = q
                    break

            if is_local_model:
                if next_question_id == "standards":
                    system_prompt = "Ask: Regulatory standards? (DO-178C/ISO/IEC/none). SHORT."
                elif next_question_id == "dev_process":
                    system_prompt = "Acknowledge. Ask: Development process? (V-model/iterative/agile). SHORT."
                elif next_question_id == "architecture":
                    system_prompt = "Acknowledge. Ask: Architecture? (modular/layered/simple). SHORT."
                elif next_question_id == "req_source":
                    system_prompt = "Acknowledge. Ask: Requirements source? (customer/internal/user needs). SHORT."
                else:
                    system_prompt = "Say: Execution Questions. Ask: Lifecycle phase? (concept/requirements/design/testing). SHORT."
                    next_question_id = "lifecycle_phase"
            else:
                base_context = f"""You are the AISET project initialization assistant.
{ai_instruction_context}
{history_context}
"""
                if next_question_id == "standards":
                    system_prompt = f"""{base_context}
Ask: "Do any regulatory standards apply?" (DO-178C, ISO 26262, IEC standards, or "none")
SHORT response."""
                elif next_question_id == "dev_process":
                    system_prompt = f"""{base_context}
Acknowledge briefly. Ask: "What development process will you follow?" (V-model, iterative, agile, simple/sequential)
SHORT."""
                elif next_question_id == "architecture":
                    system_prompt = f"""{base_context}
Acknowledge briefly. Ask: "What is your architecture approach?" (modular, layered, simple component-based)
SHORT."""
                elif next_question_id == "req_source":
                    system_prompt = f"""{base_context}
Acknowledge briefly. Ask: "Where will requirements come from?" (customer specs, internal definition, user needs)
SHORT."""
                else:
                    system_prompt = f"""{base_context}
Say: "Moving to Execution Questions."
Ask: "What lifecycle phase is this project in?" (concept, requirements, design, implementation, testing)
SHORT."""
                    next_question_id = "lifecycle_phase"

        elif current_stage == "execution":
            for q in EXECUTION_QUESTIONS:
                if q not in answered_questions:
                    next_question_id = q
                    break

            if is_local_model:
                if next_question_id == "lifecycle_phase":
                    system_prompt = "Ask: Lifecycle phase? (concept/requirements/design/testing). SHORT."
                elif next_question_id == "verification":
                    system_prompt = "Acknowledge. Ask: Verification approach? (testing/inspection/review). SHORT."
                elif next_question_id == "team_size":
                    system_prompt = "Acknowledge. Ask: Team size? (solo/small/medium/large). SHORT."
                else:
                    system_prompt = "Summarize project config briefly. Say: Interview COMPLETE."
                    next_question_id = "complete"
            else:
                base_context = f"""You are the AISET project initialization assistant.
{ai_instruction_context}
{history_context}
"""
                if next_question_id == "lifecycle_phase":
                    system_prompt = f"""{base_context}
Ask: "What lifecycle phase?" (concept, requirements, design, implementation, testing)
SHORT."""
                elif next_question_id == "verification":
                    system_prompt = f"""{base_context}
Acknowledge briefly. Ask: "What verification approach?" (testing, inspection, review, combination)
SHORT."""
                elif next_question_id == "team_size":
                    system_prompt = f"""{base_context}
Acknowledge briefly. Ask: "How large is your team?" (solo, small 2-5, medium 6-20, large 20+)
SHORT."""
                else:
                    system_prompt = f"""{base_context}

COLLECTED DATA:
{collected_data}

Provide a brief SUMMARY of the project configuration, then say:
"Interview COMPLETE. Your project is now configured."
"""
                    next_question_id = "complete"

        else:  # complete
            if is_local_model:
                system_prompt = "Interview complete. Thank the user."
            else:
                system_prompt = f"""You are the AISET project initialization assistant.
{ai_instruction_context}
The interview is complete. Thank the user."""

        # Prepare messages for AI
        messages = [{"role": "user", "content": user_input}]

        response = await self.provider.chat(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=512  # Limit response length for faster generation
        )

        # Initialize next_stage with current stage (default: stay in same stage)
        next_stage = current_stage

        # Track the question that was just asked and determine stage transitions
        if current_stage == "initial":
            # First response, move to foundation
            next_stage = "foundation"
        elif current_stage == "foundation":
            # Mark question as answered and check for stage transition
            if next_question_id == "safety_critical" and "safety_critical" not in answered_questions:
                answered_questions.append("safety_critical")
            elif next_question_id == "industry" and "industry" not in answered_questions:
                answered_questions.append("industry")
            elif next_question_id == "product_type" and "product_type" not in answered_questions:
                answered_questions.append("product_type")
            elif next_question_id == "standards":
                # Moving to planning
                next_stage = "planning"
            # Stay in foundation otherwise (next_stage already set to current_stage)
        elif current_stage == "planning":
            if next_question_id == "standards" and "standards" not in answered_questions:
                answered_questions.append("standards")
            elif next_question_id == "dev_process" and "dev_process" not in answered_questions:
                answered_questions.append("dev_process")
            elif next_question_id == "architecture" and "architecture" not in answered_questions:
                answered_questions.append("architecture")
            elif next_question_id == "req_source" and "req_source" not in answered_questions:
                answered_questions.append("req_source")
            elif next_question_id == "lifecycle_phase":
                next_stage = "execution"
            # Stay in planning otherwise
        elif current_stage == "execution":
            if next_question_id == "lifecycle_phase" and "lifecycle_phase" not in answered_questions:
                answered_questions.append("lifecycle_phase")
            elif next_question_id == "verification" and "verification" not in answered_questions:
                answered_questions.append("verification")
            elif next_question_id == "team_size" and "team_size" not in answered_questions:
                answered_questions.append("team_size")
            elif next_question_id == "complete":
                next_stage = "complete"
            # Stay in execution otherwise

        return {
            "next_question": response["content"],
            "stage": next_stage,
            "complete": next_stage == "complete",
            "model": self.model if hasattr(self, 'model') else self.provider.get_model_name(),
            "answered": answered_questions  # Return updated list
        }

    def get_current_model(self) -> str:
        """Get the current AI model name."""
        return self.provider.get_model_name()


# Global service instance
ai_service = AIService()
