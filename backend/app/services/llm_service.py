"""Reusable LLM service with OpenAI as the primary provider.

The service is provider-agnostic at the call site — it accepts a list of
chat messages and returns the generated text.  Provider-specific API
logic is isolated within this module so that another provider (e.g.
Gemini) can be substituted by implementing the same ``LLMService``
protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from openai import APIConnectionError, APIStatusError, OpenAI
from pydantic import BaseModel, Field

from app.config import settings
from app.exceptions import LLMConfigurationError, LLMServiceError


class LLMMessage(BaseModel):
    """A single message in an LLM conversation."""

    role: str = Field(description="Message role: system, user, or assistant")
    content: str = Field(description="Message text")


class LLMService(ABC):
    """Abstract interface for LLM providers.

    Implementations must provide ``generate`` which accepts a list of
    messages and returns the generated text.
    """

    @abstractmethod
    async def generate(self, messages: list[dict[str, str]]) -> str:
        """Generate a response from the LLM given conversation messages.

        Args:
            messages: List of dicts with ``role`` and ``content`` keys,
                      following the OpenAI chat message format.

        Returns:
            The generated text from the LLM.

        Raises:
            LLMConfigurationError: If the service is misconfigured.
            LLMServiceError: If the API call fails.
        """
        ...


class OpenAIService(LLMService):
    """OpenAI-based LLM service.

    Reads the API key, model, and optional base URL from the
    application settings.  The base URL can be set to use an
    OpenAI-compatible proxy or alternative endpoint.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.openai_api_key
        self._model = model if model is not None else settings.openai_model
        self._base_url = base_url if base_url is not None else settings.openai_base_url

        if not self._api_key:
            raise LLMConfigurationError(
                "OPENAI_API_KEY is not set. "
                "Provide it via the .env file or OPENAI_API_KEY environment variable."
            )

        client_kwargs: dict = {"api_key": self._api_key}
        if self._base_url:
            client_kwargs["base_url"] = self._base_url

        self._client = OpenAI(**client_kwargs)

    async def generate(self, messages: list[dict[str, str]]) -> str:
        """Generate a response using the OpenAI Chat Completions API.

        Args:
            messages: Chat messages in OpenAI format
                      (``{"role": "...", "content": "..."}``).

        Returns:
            The assistant's reply text.

        Raises:
            LLMServiceError: If the API call fails.
        """
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,  # type: ignore[arg-type]
            )
        except APIConnectionError as exc:
            raise LLMServiceError(f"Connection error: {exc}") from exc
        except APIStatusError as exc:
            raise LLMServiceError(
                f"API error (status={exc.status_code}): {exc.message}"
            ) from exc
        except Exception as exc:
            raise LLMServiceError(f"Unexpected error: {exc}") from exc

        content = response.choices[0].message.content
        if content is None:
            raise LLMServiceError("LLM returned no content")

        return content.strip()


class StubLLMService(LLMService):
    """Stub LLM service that returns a fixed reply.

    Used when no API key is configured so the application can still
    start and the interview flow remains functional with placeholder
    responses.
    """

    def __init__(self, reply: str = "Thank you for your response. Let's continue.") -> None:
        self._reply = reply

    async def generate(self, messages: list[dict[str, str]]) -> str:
        """Return the fixed stub reply, ignoring the input messages."""
        return self._reply
