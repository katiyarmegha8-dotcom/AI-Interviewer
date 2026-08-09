"""Interview orchestration service.

Handles the business logic for starting and continuing interviews.
When an LLM service is provided, follow-up turns generate replies via
the LLM using a structured prompt built by the prompt builder.
When none is provided, a placeholder reply is returned.
"""

from __future__ import annotations

from app.models.candidate import Candidate
from app.models.curriculum import Curriculum
from app.models.interview import Feedback, InterviewResponse
from app.models.session import InterviewSession
from app.services.llm_service import LLMService
from app.services.prompt_builder import build_interview_messages
from app.services.session_service import SessionManager

# Default welcome reply from the technical specification
WELCOME_REPLY = "Welcome. Let's begin your interview."

# Fallback reply when no LLM service is available
_FALLBACK_REPLY = "Thank you for your response. Let's continue."


def start_interview(
    session_id: str,
    candidate: Candidate,
    manager: SessionManager,
) -> InterviewResponse:
    """Start a new interview session.

    Creates a session in the ``SessionManager``, records the welcome
    message in conversation history, and returns the spec-compliant
    response.

    Args:
        session_id: Client-provided session identifier.
        candidate: Candidate profile to associate with the session.
        manager: Session manager instance.

    Returns:
        InterviewResponse with the welcome reply and done=False.
    """
    manager.create_session(candidate, session_id=session_id)
    manager.add_message(session_id, "interviewer", WELCOME_REPLY)
    return InterviewResponse(reply=WELCOME_REPLY, done=False)


async def continue_interview(
    session_id: str,
    message: str,
    manager: SessionManager,
    curriculum: Curriculum,
    llm: LLMService | None = None,
) -> InterviewResponse:
    """Process a follow-up turn in an existing interview.

    Records the candidate's message, then either calls the LLM to
    generate the next interviewer reply (using the prompt builder)
    or returns a placeholder.

    Args:
        session_id: Existing session identifier.
        message: The candidate's latest response.
        manager: Session manager instance.
        curriculum: Curriculum data for prompt context.
        llm: Optional LLM service for generating replies.

    Returns:
        InterviewResponse with a reply and done=False.

    Raises:
        SessionNotFoundError: If the session ID is unknown.
        LLMServiceError: If the LLM API call fails.
    """
    # Verify session exists
    session = manager.get_session(session_id)

    # Record the candidate's answer
    manager.add_message(session_id, "candidate", message)
    manager.record_answer(session_id)

    # Generate the interviewer reply
    if llm is not None:
        # Get the updated session (includes candidate's latest message)
        updated_session = manager.get_session(session_id)

        # Build structured messages using the prompt builder
        llm_messages = build_interview_messages(updated_session, curriculum)
        reply = await llm.generate(llm_messages)
    else:
        reply = _FALLBACK_REPLY

    # Record the interviewer's reply in session history
    manager.add_message(session_id, "interviewer", reply)
    return InterviewResponse(reply=reply, done=False)
