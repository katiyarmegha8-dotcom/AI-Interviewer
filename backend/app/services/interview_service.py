"""Interview orchestration service.

Handles the business logic for starting and continuing interviews.
LLM-based question generation and adaptive interviewing are later
milestones — this service provides the structural flow only.
"""

from __future__ import annotations

from app.models.candidate import Candidate
from app.models.interview import Feedback, InterviewResponse
from app.models.session import InterviewSession
from app.services.session_service import SessionManager

# Default welcome reply from the technical specification
WELCOME_REPLY = "Welcome. Let's begin your interview."

# Placeholder reply for follow-up turns (LLM integration is a later milestone)
CONTINUE_REPLY = "Thank you for your response. Let's continue."


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


def continue_interview(
    session_id: str,
    message: str,
    manager: SessionManager,
) -> InterviewResponse:
    """Process a follow-up turn in an existing interview.

    Records the candidate's message and answer, then returns a
    placeholder reply.  LLM-based generation is a later milestone.

    Args:
        session_id: Existing session identifier.
        message: The candidate's latest response.
        manager: Session manager instance.

    Returns:
        InterviewResponse with a reply and done=False.

    Raises:
        SessionNotFoundError: If the session ID is unknown.
    """
    # get_session will raise SessionNotFoundError if not found
    session = manager.get_session(session_id)

    # Record the candidate's answer
    manager.add_message(session_id, "candidate", message)
    manager.record_answer(session_id)

    # Return a placeholder interviewer reply (LLM integration later)
    manager.add_message(session_id, "interviewer", CONTINUE_REPLY)
    return InterviewResponse(reply=CONTINUE_REPLY, done=False)
