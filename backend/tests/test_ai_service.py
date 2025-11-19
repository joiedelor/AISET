"""
Unit tests for AI Service
DO-178C Traceability: Verification of REQ-AI-001, REQ-AI-002, REQ-AI-010
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from services.ai_service import AIService, ClaudeProvider, LMStudioProvider


class TestAIServiceBehavior:
    """Test AI behavior compliance with DO-178C requirements."""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance for testing."""
        return AIService()

    @pytest.mark.asyncio
    async def test_single_question_validation_valid(self, ai_service):
        """
        Test REQ-AI-001: Validate single question detection (valid case).

        Verification Method: Test
        Expected: Response with one question mark should be valid.
        """
        response = "What is the maximum operating altitude for your aircraft?"

        validation = await ai_service.validate_single_question(response)

        assert validation["valid"] is True
        assert validation["question_count"] == 1
        assert len(validation["issues"]) == 0

    @pytest.mark.asyncio
    async def test_single_question_validation_invalid_multiple(self, ai_service):
        """
        Test REQ-AI-001: Validate single question detection (invalid case).

        Verification Method: Test
        Expected: Response with multiple questions should be flagged.
        """
        response = "What is the altitude? What is the speed? What is the range?"

        validation = await ai_service.validate_single_question(response)

        assert validation["valid"] is False
        assert validation["question_count"] == 3
        assert len(validation["issues"]) > 0

    @pytest.mark.asyncio
    async def test_single_question_validation_statement(self, ai_service):
        """
        Test REQ-AI-001: Validate handling of statements (no questions).

        Verification Method: Test
        Expected: Statement without questions should be valid.
        """
        response = "I understand your requirements. Let me document this information."

        validation = await ai_service.validate_single_question(response)

        assert validation["valid"] is True
        assert validation["question_count"] == 0

    def test_requirements_elicitation_system_prompt_content(self, ai_service):
        """
        Test REQ-AI-001, REQ-AI-002, REQ-AI-010: Verify system prompt contains rules.

        Verification Method: Review
        Expected: System prompt should enforce single question, simple language, no design decisions.
        """
        # Access the requirements_elicitation method and check its implementation
        import inspect
        source = inspect.getsource(ai_service.requirements_elicitation)

        # Verify critical rules are in the implementation
        assert "SINGLE QUESTION ONLY" in source or "single question" in source.lower()
        assert "SIMPLE LANGUAGE" in source or "simple language" in source.lower()
        assert "NO DESIGN DECISIONS" in source or "no design decisions" in source.lower()
        assert "REQ-AI-001" in source
        assert "REQ-AI-002" in source
        assert "REQ-AI-010" in source

    def test_simple_language_enforcement(self, ai_service):
        """
        Test REQ-AI-002: Verify simple language instruction.

        Verification Method: Review
        Expected: System prompt should instruct AI to avoid technical jargon.
        """
        import inspect
        source = inspect.getsource(ai_service.requirements_elicitation)

        # Verify simple language instructions
        assert "simple" in source.lower() or "plain" in source.lower()
        assert "jargon" in source.lower() or "technical" in source.lower()

    def test_no_design_decisions_enforcement(self, ai_service):
        """
        Test REQ-AI-010: Verify no design decisions instruction.

        Verification Method: Review
        Expected: System prompt should forbid AI from making design choices.
        """
        import inspect
        source = inspect.getsource(ai_service.requirements_elicitation)

        # Verify no design decisions instructions
        assert "never make design decisions" in source.lower() or "not make design decisions" in source.lower()
        assert "offer options" in source.lower() or "present options" in source.lower()
        assert "user is the decision-maker" in source.lower() or "decision-maker" in source.lower()


class TestAIProviders:
    """Test AI provider implementations."""

    @pytest.mark.asyncio
    @patch('anthropic.Anthropic')
    async def test_claude_provider_chat(self, mock_anthropic):
        """
        Test Claude provider chat method.

        Verification Method: Test
        """
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        mock_response.usage.input_tokens = 50
        mock_response.usage.output_tokens = 50
        mock_response.stop_reason = "end_turn"

        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Test
        provider = ClaudeProvider()
        provider.client = mock_client

        response = await provider.chat(
            messages=[{"role": "user", "content": "Hello"}],
            system_prompt="Test prompt"
        )

        assert response["content"] == "Test response"
        assert response["tokens_used"] == 100
        assert mock_client.messages.create.called

    @pytest.mark.asyncio
    async def test_lmstudio_provider_initialization(self):
        """
        Test LM Studio provider initialization.

        Verification Method: Test
        """
        provider = LMStudioProvider()

        assert provider.base_url is not None
        assert provider.model is not None
        assert provider.get_model_name() == provider.model


class TestRequirementsExtraction:
    """Test requirements extraction functionality."""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance for testing."""
        return AIService()

    @pytest.mark.asyncio
    @patch('services.ai_service.ClaudeProvider.chat')
    async def test_extract_requirements_json_parsing(self, mock_chat, ai_service):
        """
        Test REQ-AI-009: Extract requirements with valid JSON.

        Verification Method: Test
        Expected: Valid JSON should be parsed correctly.
        """
        mock_response = """[
            {
                "title": "User Authentication",
                "description": "The system shall verify user credentials",
                "type": "security",
                "priority": "high",
                "acceptance_criteria": "User cannot access without valid credentials",
                "confidence_score": 0.95
            }
        ]"""

        mock_chat.return_value = {
            "content": mock_response,
            "model": "claude-3-opus",
            "tokens_used": 200,
            "stop_reason": "end_turn"
        }

        conversation_text = "User: We need user authentication\nAssistant: What type of credentials?"
        requirements = await ai_service.extract_requirements(conversation_text)

        assert len(requirements) == 1
        assert requirements[0]["title"] == "User Authentication"
        assert requirements[0]["type"] == "security"
        assert requirements[0]["confidence_score"] == 0.95

    @pytest.mark.asyncio
    @patch('services.ai_service.ClaudeProvider.chat')
    async def test_extract_requirements_invalid_json(self, mock_chat, ai_service):
        """
        Test REQ-AI-009: Handle invalid JSON gracefully.

        Verification Method: Test
        Expected: Invalid JSON should return empty list, not crash.
        """
        mock_chat.return_value = {
            "content": "This is not valid JSON",
            "model": "claude-3-opus",
            "tokens_used": 50,
            "stop_reason": "end_turn"
        }

        conversation_text = "Some conversation"
        requirements = await ai_service.extract_requirements(conversation_text)

        assert requirements == []


class TestTraceabilitySuggestion:
    """Test traceability suggestion functionality."""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance for testing."""
        return AIService()

    @pytest.mark.asyncio
    @patch('services.ai_service.ClaudeProvider.chat')
    async def test_suggest_traceability(self, mock_chat, ai_service):
        """
        Test REQ-AI-010: Suggest traceability links.

        Verification Method: Test
        """
        mock_response = """[
            {
                "component_id": "COMP-AUTH-001",
                "confidence_score": 0.85,
                "rationale": "This component handles user authentication"
            }
        ]"""

        mock_chat.return_value = {
            "content": mock_response,
            "model": "claude-3-opus",
            "tokens_used": 150,
            "stop_reason": "end_turn"
        }

        requirement_text = "The system shall authenticate users"
        design_components = [
            {
                "component_id": "COMP-AUTH-001",
                "name": "Authentication Module",
                "description": "Handles user login and verification"
            }
        ]

        suggestions = await ai_service.suggest_traceability(requirement_text, design_components)

        assert len(suggestions) == 1
        assert suggestions[0]["component_id"] == "COMP-AUTH-001"
        assert suggestions[0]["confidence_score"] == 0.85


# Test execution metadata
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
