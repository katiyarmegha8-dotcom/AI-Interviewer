"""Feedback generation service.

Generates structured interview feedback by building a prompt via the
feedback prompt builder and sending it through the LLM service.  Parses
the LLM's JSON response into a ``DetailedFeedback`` model.

Feedback generation is kept **separate** from the LLM provider — this
module orchestrates the prompt construction and response parsing while
delegating the actual LLM call to the injected ``LLMService``.
"""

from __future__ import annotations

import json

from app.models.curriculum import Curriculum
from app.models.feedback import DetailedFeedback
from app.models.session import InterviewSession
from app.services.feedback_prompt_builder import build_feedback_messages
from app.services.llm_service import LLMService

# ---------------------------------------------------------------------------
# Default fallback feedback (when no LLM is available)
# ---------------------------------------------------------------------------

_DEFAULT_FEEDBACK = DetailedFeedback(
    overall_summary="Interview completed. Detailed feedback generation "
    "requires an LLM service.",
    technical_strengths=["Unable to assess — no LLM service configured"],
    knowledge_gaps=["Unable to assess — no LLM service configured"],
    communication_assessment="Unable to assess — no LLM service configured.",
    recommended_next_topics=["Configure an LLM service for detailed feedback"],
)


# ---------------------------------------------------------------------------
# JSON parsing
# ---------------------------------------------------------------------------


def _parse_feedback_json(raw: str) -> DetailedFeedback:
    """Parse the LLM's JSON response into a ``DetailedFeedback`` model.

    Handles common LLM output issues:
      - Markdown code fences (```json ... ```)
      - Leading/trailing whitespace
      - Missing or extra fields (fills defaults for missing)

    Args:
        raw: The raw text returned by the LLM.

    Returns:
        A validated ``DetailedFeedback`` instance.

    Raises:
        ValueError: If the response cannot be parsed as valid JSON or
                    the resulting object cannot be validated as
                    ``DetailedFeedback``.
    """
    text = raw.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        # Remove opening fence (```json or ```)
        first_newline = text.index("\n") if "\n" in text else len(text)
        text = text[first_newline + 1 :]
        # Remove closing fence
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3].rstrip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM response is not valid JSON: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            f"LLM response is not a JSON object, got {type(data).__name__}"
        )

    # Map and validate with sensible defaults for missing fields
    return DetailedFeedback(
        overall_summary=data.get("overall_summary", "No summary provided."),
        technical_strengths=_ensure_list(data.get("technical_strengths", [])),
        knowledge_gaps=_ensure_list(data.get("knowledge_gaps", [])),
        communication_assessment=data.get(
            "communication_assessment", "No communication assessment provided."
        ),
        recommended_next_topics=_ensure_list(
            data.get("recommended_next_topics", [])
        ),
    )


def _ensure_list(value: object) -> list[str]:
    """Ensure a value is a list of strings.

    Handles cases where the LLM returns a single string instead of a list,
    or non-string items.
    """
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        return [value]
    return [str(value)] if value is not None else []


# ---------------------------------------------------------------------------
# Main feedback generator
# ---------------------------------------------------------------------------


async def generate_feedback(
    session: InterviewSession,
    curriculum: Curriculum,
    llm: LLMService | None = None,
) -> DetailedFeedback:
    """Generate structured feedback for a completed interview.

    If an LLM service is provided, builds a feedback prompt, sends it
    through the LLM, and parses the JSON response.  If no LLM is
    available or parsing fails, returns a default fallback feedback.

    Args:
        session: The completed interview session.
        curriculum: The full curriculum data.
        llm: Optional LLM service for generating feedback.

    Returns:
        A ``DetailedFeedback`` instance with all five sections populated.

    Raises:
        LLMServiceError: If the LLM API call fails.
    """
    if llm is None:
        return _DEFAULT_FEEDBACK

    # Build the feedback prompt
    messages = build_feedback_messages(session, curriculum)

    # Call the LLM
    raw_response = await llm.generate(messages)

    # Parse the structured response
    try:
        return _parse_feedback_json(raw_response)
    except ValueError:
        # If parsing fails, return feedback with the raw response as summary
        return DetailedFeedback(
            overall_summary=raw_response[:500] if raw_response else "No feedback generated.",
            technical_strengths=["Could not parse structured feedback from LLM"],
            knowledge_gaps=["Could not parse structured feedback from LLM"],
            communication_assessment="Could not parse structured feedback from LLM.",
            recommended_next_topics=["Retry feedback generation or review raw LLM output"],
        )
