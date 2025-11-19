"""
Unit tests for Project Initialization Interview
DO-178C Traceability: Verification of REQ-AI-032 through REQ-AI-037
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from services.ai_service import AIService
from models.project import ProjectInitializationContext


class TestProjectInitializationInterview:
    """Test project initialization interview functionality."""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance for testing."""
        return AIService()

    @pytest.mark.asyncio
    async def test_initial_stage_question(self, ai_service):
        """
        Test REQ-AI-032: Initial open-ended question.

        Verification Method: Test
        Expected: First question asks for project description.
        """
        # Mock the AI provider response
        with patch.object(ai_service.provider, 'chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = {
                "content": "Can you describe the project as precisely as you can?",
                "model": "test-model",
                "tokens_used": 50,
                "stop_reason": "end_turn"
            }

            result = await ai_service.project_initialization_interview(
                user_input="I want to start a new project",
                context=None
            )

            assert "next_question" in result
            assert result["stage"] in ["initial", "foundation"]
            assert result["complete"] is False

    @pytest.mark.asyncio
    async def test_foundation_stage_safety_critical(self, ai_service):
        """
        Test REQ-AI-033: Safety criticality determination.

        Verification Method: Test
        Expected: System asks about safety criticality.
        """
        with patch.object(ai_service.provider, 'chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = {
                "content": "Is this system safety-critical?",
                "model": "test-model",
                "tokens_used": 50,
                "stop_reason": "end_turn"
            }

            context = {
                "stage": "foundation",
                "data": {}
            }

            result = await ai_service.project_initialization_interview(
                user_input="It's an aerospace flight control system",
                context=context
            )

            assert result["stage"] in ["foundation", "planning"]
            # Verify system prompt includes safety questions
            call_args = mock_chat.call_args
            system_prompt = call_args.kwargs.get('system_prompt', '')
            assert "safety" in system_prompt.lower()

    @pytest.mark.asyncio
    async def test_foundation_stage_dal_sil(self, ai_service):
        """
        Test REQ-AI-033: DAL/SIL level determination.

        Verification Method: Test
        Expected: System asks about DAL or SIL level for safety-critical systems.
        """
        with patch.object(ai_service.provider, 'chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = {
                "content": "What is the required Development Assurance Level (DAL)?",
                "model": "test-model",
                "tokens_used": 50,
                "stop_reason": "end_turn"
            }

            context = {
                "stage": "foundation",
                "data": {"safety_critical": True}
            }

            result = await ai_service.project_initialization_interview(
                user_input="Yes, it's safety-critical",
                context=context
            )

            call_args = mock_chat.call_args
            system_prompt = call_args.kwargs.get('system_prompt', '')
            assert "DAL" in system_prompt or "SIL" in system_prompt

    @pytest.mark.asyncio
    async def test_planning_stage_standards(self, ai_service):
        """
        Test REQ-AI-034: Regulatory standards identification.

        Verification Method: Test
        Expected: System asks about applicable regulatory standards.
        """
        with patch.object(ai_service.provider, 'chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = {
                "content": "Which regulatory standards apply to your project?",
                "model": "test-model",
                "tokens_used": 50,
                "stop_reason": "end_turn"
            }

            context = {
                "stage": "planning",
                "data": {
                    "safety_critical": True,
                    "dal_level": "A",
                    "domain": "aerospace"
                }
            }

            result = await ai_service.project_initialization_interview(
                user_input="DAL level A",
                context=context
            )

            call_args = mock_chat.call_args
            system_prompt = call_args.kwargs.get('system_prompt', '')
            assert "standards" in system_prompt.lower()
            assert "DO-178C" in system_prompt or "ISO 26262" in system_prompt

    @pytest.mark.asyncio
    async def test_planning_stage_development_process(self, ai_service):
        """
        Test REQ-AI-035: Development process selection.

        Verification Method: Test
        Expected: System asks about development process.
        """
        with patch.object(ai_service.provider, 'chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = {
                "content": "What development process will you follow?",
                "model": "test-model",
                "tokens_used": 50,
                "stop_reason": "end_turn"
            }

            context = {
                "stage": "planning",
                "data": {
                    "regulatory_standards": ["DO-178C"]
                }
            }

            result = await ai_service.project_initialization_interview(
                user_input="DO-178C and DO-254",
                context=context
            )

            call_args = mock_chat.call_args
            system_prompt = call_args.kwargs.get('system_prompt', '')
            assert "process" in system_prompt.lower()
            assert "v-model" in system_prompt.lower() or "agile" in system_prompt.lower()

    @pytest.mark.asyncio
    async def test_execution_stage_lifecycle(self, ai_service):
        """
        Test execution stage: Lifecycle phase determination.

        Verification Method: Test
        Expected: System asks about current lifecycle phase.
        """
        with patch.object(ai_service.provider, 'chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = {
                "content": "What lifecycle phase are you in?",
                "model": "test-model",
                "tokens_used": 50,
                "stop_reason": "end_turn"
            }

            context = {
                "stage": "execution",
                "data": {
                    "development_process": "V-model"
                }
            }

            result = await ai_service.project_initialization_interview(
                user_input="V-model with iterations",
                context=context
            )

            call_args = mock_chat.call_args
            system_prompt = call_args.kwargs.get('system_prompt', '')
            assert "lifecycle" in system_prompt.lower() or "phase" in system_prompt.lower()

    @pytest.mark.asyncio
    async def test_interview_completion(self, ai_service):
        """
        Test interview completion detection.

        Verification Method: Test
        Expected: Interview marked complete after all stages.
        """
        with patch.object(ai_service.provider, 'chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = {
                "content": "Great! Let me summarize your project setup. COMPLETE",
                "model": "test-model",
                "tokens_used": 50,
                "stop_reason": "end_turn"
            }

            context = {
                "stage": "execution",
                "data": {
                    "safety_critical": True,
                    "dal_level": "B",
                    "domain": "aerospace",
                    "lifecycle_phase": "requirements"
                }
            }

            result = await ai_service.project_initialization_interview(
                user_input="Small team of 3 engineers",
                context=context
            )

            # Check that completion is detected
            assert result["stage"] == "complete" or result["complete"] is True

    def test_initialization_context_model(self):
        """
        Test REQ-AI-037: ProjectInitializationContext data model.

        Verification Method: Test
        Expected: Data model validates correctly with all fields.
        """
        context = ProjectInitializationContext(
            safety_critical=True,
            dal_level="A",
            sil_level=None,
            domain="aerospace",
            product_type="flight control software",
            regulatory_standards=["DO-178C", "DO-254"],
            development_process="V-model",
            architecture_type="modular",
            requirements_source="customer specs",
            lifecycle_phase="requirements",
            verification_approach="requirements-based testing",
            team_size=5,
            initialization_complete=True,
            interview_stage="complete"
        )

        assert context.safety_critical is True
        assert context.dal_level == "A"
        assert context.domain == "aerospace"
        assert "DO-178C" in context.regulatory_standards
        assert context.initialization_complete is True

    def test_initialization_context_defaults(self):
        """
        Test ProjectInitializationContext default values.

        Verification Method: Test
        Expected: Optional fields have appropriate defaults.
        """
        context = ProjectInitializationContext(
            safety_critical=False
        )

        assert context.safety_critical is False
        assert context.dal_level is None
        assert context.regulatory_standards == []
        assert context.initialization_complete is False
        assert context.interview_stage == "foundation"


# Test execution metadata
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
