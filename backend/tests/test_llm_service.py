"""Tests for the LLM service layer.

All tests use mocks — no real API keys or external LLM API calls are made.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.exceptions import LLMConfigurationError, LLMServiceError
from app.services.llm_service import LLMMessage, LLMService, OpenAIService, StubLLMService


# ===========================================================================
# StubLLMService
# ===========================================================================


class TestStubLLMService:
    """Tests for the stub LLM service (no API key required)."""

    @pytest.mark.asyncio
    async def test_returns_default_reply(self) -> None:
        service = StubLLMService()
        result = await service.generate([{"role": "user", "content": "Hello"}])
        assert result == "Thank you for your response. Let's continue."

    @pytest.mark.asyncio
    async def test_returns_custom_reply(self) -> None:
        service = StubLLMService(reply="Custom reply")
        result = await service.generate([{"role": "user", "content": "Hello"}])
        assert result == "Custom reply"

    @pytest.mark.asyncio
    async def test_ignores_input_messages(self) -> None:
        service = StubLLMService(reply="Fixed")
        result = await service.generate([
            {"role": "system", "content": "You are an interviewer"},
            {"role": "user", "content": "My answer"},
        ])
        assert result == "Fixed"

    @pytest.mark.asyncio
    async def test_handles_empty_messages(self) -> None:
        service = StubLLMService()
        result = await service.generate([])
        assert result == "Thank you for your response. Let's continue."


# ===========================================================================
# OpenAIService — configuration
# ===========================================================================


class TestOpenAIServiceConfiguration:
    """Tests for OpenAI service configuration and error handling."""

    def test_missing_api_key_raises_configuration_error(self) -> None:
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai_api_key = ""
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_base_url = ""
            with pytest.raises(LLMConfigurationError) as exc_info:
                OpenAIService()
            assert "OPENAI_API_KEY" in str(exc_info.value)

    def test_explicit_api_key_bypasses_settings(self) -> None:
        """When an API key is passed explicitly, no error even if settings has none."""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai_api_key = ""
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_base_url = ""
            # Should not raise — explicit key provided
            service = OpenAIService(api_key="sk-test-explicit")
            assert service._api_key == "sk-test-explicit"

    def test_uses_settings_model(self) -> None:
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4o"
            mock_settings.openai_base_url = ""
            service = OpenAIService()
            assert service._model == "gpt-4o"

    def test_explicit_model_overrides_settings(self) -> None:
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_base_url = ""
            service = OpenAIService(model="gpt-4o")
            assert service._model == "gpt-4o"

    def test_explicit_base_url_overrides_settings(self) -> None:
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_base_url = ""
            service = OpenAIService(base_url="http://localhost:11434/v1")
            assert service._base_url == "http://localhost:11434/v1"


# ===========================================================================
# OpenAIService — generate (mocked API calls)
# ===========================================================================


class TestOpenAIServiceGenerate:
    """Tests for OpenAI service generation with mocked API calls."""

    @pytest.mark.asyncio
    async def test_generate_returns_content(self) -> None:
        """Successful API call returns the generated text."""
        mock_choice = MagicMock()
        mock_choice.message.content = "Tell me about your experience with RAG."

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_base_url = ""

            service = OpenAIService()
            service._client = mock_client

            result = await service.generate([
                {"role": "system", "content": "You are an interviewer"},
                {"role": "user", "content": "I know Python"},
            ])
            assert result == "Tell me about your experience with RAG."

    @pytest.mark.asyncio
    async def test_generate_strips_whitespace(self) -> None:
        """Response text is stripped of leading/trailing whitespace."""
        mock_choice = MagicMock()
        mock_choice.message.content = "  Hello there  \n"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_base_url = ""

            service = OpenAIService()
            service._client = mock_client

            result = await service.generate([{"role": "user", "content": "Hi"}])
            assert result == "Hello there"

    @pytest.mark.asyncio
    async def test_generate_none_content_raises(self) -> None:
        """If the API returns None content, raise LLMServiceError."""
        mock_choice = MagicMock()
        mock_choice.message.content = None

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_base_url = ""

            service = OpenAIService()
            service._client = mock_client

            with pytest.raises(LLMServiceError) as exc_info:
                await service.generate([{"role": "user", "content": "Hi"}])
            assert "no content" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_connection_error_raises(self) -> None:
        """API connection errors are wrapped in LLMServiceError."""
        from openai import APIConnectionError

        mock_request = MagicMock()

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = APIConnectionError(
            message="Connection failed",
            request=mock_request,
        )

        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_base_url = ""

            service = OpenAIService()
            service._client = mock_client

            with pytest.raises(LLMServiceError) as exc_info:
                await service.generate([{"role": "user", "content": "Hi"}])
            assert "Connection error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_status_error_raises(self) -> None:
        """API status errors (e.g. 401, 429) are wrapped in LLMServiceError."""
        from openai import APIStatusError

        mock_response = MagicMock()
        mock_response.status_code = 429

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = APIStatusError(
            message="Rate limit exceeded",
            response=mock_response,
            body=None,
        )

        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_base_url = ""

            service = OpenAIService()
            service._client = mock_client

            with pytest.raises(LLMServiceError) as exc_info:
                await service.generate([{"role": "user", "content": "Hi"}])
            assert "API error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_unexpected_error_raises(self) -> None:
        """Unexpected exceptions are wrapped in LLMServiceError."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RuntimeError("Unexpected")

        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_base_url = ""

            service = OpenAIService()
            service._client = mock_client

            with pytest.raises(LLMServiceError) as exc_info:
                await service.generate([{"role": "user", "content": "Hi"}])
            assert "Unexpected error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_passes_correct_model(self) -> None:
        """The model name is passed to the API call."""
        mock_choice = MagicMock()
        mock_choice.message.content = "Reply"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_base_url = ""

            service = OpenAIService(model="gpt-4o")
            service._client = mock_client

            await service.generate([{"role": "user", "content": "Hi"}])

            call_kwargs = mock_client.chat.completions.create.call_args
            assert call_kwargs.kwargs["model"] == "gpt-4o"

    @pytest.mark.asyncio
    async def test_generate_passes_messages(self) -> None:
        """The full message list is passed to the API call."""
        mock_choice = MagicMock()
        mock_choice.message.content = "Reply"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_base_url = ""

            service = OpenAIService()
            service._client = mock_client

            messages = [
                {"role": "system", "content": "You are an interviewer"},
                {"role": "user", "content": "I know Python"},
            ]
            await service.generate(messages)

            call_kwargs = mock_client.chat.completions.create.call_args
            assert call_kwargs.kwargs["messages"] == messages


# ===========================================================================
# LLMMessage model
# ===========================================================================


class TestLLMMessage:
    """Tests for the LLMMessage Pydantic model."""

    def test_valid_message(self) -> None:
        msg = LLMMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_system_message(self) -> None:
        msg = LLMMessage(role="system", content="You are an interviewer")
        assert msg.role == "system"

    def test_assistant_message(self) -> None:
        msg = LLMMessage(role="assistant", content="Tell me more")
        assert msg.role == "assistant"


# ===========================================================================
# LLMService interface compliance
# ===========================================================================


class TestLLMServiceInterface:
    """Tests that StubLLMService and OpenAIService implement the LLMService interface."""

    def test_stub_is_llm_service(self) -> None:
        service = StubLLMService()
        assert isinstance(service, LLMService)

    def test_openai_is_llm_service(self) -> None:
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_base_url = ""
            service = OpenAIService()
            assert isinstance(service, LLMService)
