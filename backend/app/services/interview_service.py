"""Interview orchestration service.

Handles the business logic for starting, continuing, and ending interviews.
When an LLM service is provided, follow-up turns generate replies via
the LLM using a structured prompt built by the prompt builder.
When none is provided, a placeholder reply is returned.

Feedback generation follows the same pattern — the feedback prompt
builder constructs the prompt and the LLM produces structured feedback.

Interview structure requirements:
- At least 8 primary questions must be asked.
- At least 4 distinct curriculum days must be covered.
- The prompt builder instructs the LLM about these thresholds.
- The backend tracks progress and includes it in every response.
- The backend prevents continuing a completed session.
"""

from __future__ import annotations

from app.exceptions import SessionNotFoundError
from app.models.candidate import Candidate
from app.models.curriculum import Curriculum
from app.models.interview import (
    Feedback,
    InterviewProgressResponse,
    InterviewResponse,
)
from app.models.session import InterviewSession, InterviewStatus
from app.services.feedback_service import generate_feedback
from app.services.llm_service import LLMService
from app.services.prompt_builder import build_interview_messages
from app.services.session_service import SessionManager

# Default welcome reply from the technical specification
WELCOME_REPLY = "Welcome. Let's begin your interview."

# Fallback reply when no LLM service is available
_FALLBACK_REPLY = "Thank you for your response. Let's continue."

# Reply when the interview is concluded
_INTERVIEW_DONE_REPLY = "Interview completed."

# Minimum thresholds for a complete interview
MIN_QUESTIONS = 8
MIN_CURRICULUM_DAYS = 4


def _build_progress(session: InterviewSession) -> InterviewProgressResponse:
    """Build an InterviewProgressResponse from the session state."""
    return InterviewProgressResponse(
        questionsAsked=session.progress.questionsAsked,
        questionsAnswered=session.progress.questionsAnswered,
        curriculumDaysCovered=len(session.curriculumDaysCovered),
        currentDay=session.progress.currentDay,
        totalDays=session.progress.totalDays,
    )


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
    session = manager.create_session(candidate, session_id=session_id)
    manager.add_message(session_id, "interviewer", WELCOME_REPLY)
    return InterviewResponse(
        reply=WELCOME_REPLY,
        done=False,
        progress=_build_progress(session),
    )


async def continue_interview(
    session_id: str,
    message: str,
    manager: SessionManager,
    curriculum: Curriculum,
    llm: LLMService | None = None,
) -> InterviewResponse:
    """Process a follow-up turn in an existing interview.

    Records the candidate's message, then either calls the$LLM to
    generate the next interviewer reply (using the prompt builder)
    or returns a placeholder.

    Raises SessionNotFoundError if the session ID is unknown.
    Raises ValueError if the session is already completed.

    Args:
        session_id: Existing session identifier.
        message: The candidate's latest response.
        manager: Session manager instance.
        curriculum: Curriculum data for prompt context.
F       llm: Optional LLM service for generating replies.

    Returns:
        InterviewResponse with a reply and done=False.

    Raises:
        SessionNotFoundError: If the session ID is unknown.
        ValueError: If the session is already completed.
        LLMServiceError: If the LLM API call fails.
    """
    # Verify session exists and is still active
    session = manager.get_session(session_id)

    if session.status == InterviewStatus.COMPLETED:
        raise ValueError(
            f"Interview session '{session_id}' is already completed. "
            "Start a new session to continue interviewing."
        )

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

    # Track this as a question asked (each interviewer turn is a question)
    # Determine the curriculum day from the session's current progress
    updated_session = manager.get_session(session_id)
    current_day = updated_session.progress.currentDay
    manager.add_question(session_id, current_day, reply)

    # Get the final session state for the response
    final_session = manager.get_session(session_id)

    return InterviewResponse(
        reply=reply,
        done=False,
        progress=_build_progress(final_session),
    )


async def end_interview(
    session_id: str,
    manager: SessionManager,
    curriculum: Curriculum,
    llm: LLMService | None = None,
) -> InterviewResponse:
    """End an interview and generate structured feedback.

    Marks the session as completed, generates feedback using the
    feedback service, and returns the spec-compliant response with
    ``done=True``.

    Args:
        session_id: Existing session identifier.
        manager: Session manager instance.
        curriculum: Curriculum data for feedback context.
        llm: Optional LLM service for generating feedback.

    Returns:
        InterviewResponse with the completion reply, done=True,
        and structured feedback.

    Raises:
        SessionNotFoundError: If the session ID is unknown.
        LLMServiceError: If the LLM API call fails.
    """
    # Verify session exists and is still active
    session = manager.get_session(session_id)

    if session.status == InterviewStatus.COMPLETED:
        raise ValueError(
            f"Interview session '{session_id}' is already completed. "
            "Start a new session to continue interviewing."
        )

    # Mark session as completed (raises SessionNotFoundError if missing)
    manager.complete_session(session_id)

    # Get the completed session for feedback generation
    completed_session = manager.get_session(session_id)

    # Generate structured feedback
    detailed = await generate_feedback(completed_session, curriculum, llm=llm)

    # Convert to API-level Feedback model
    feedback = detailed.to_api_feedback()

    # Record the completion message in session history
    manager.add_message(session_id, "interviewer", _INTERVIEW_DONE_REPLY)

    # Get the final session state
    final_session = manager.get_session(session_id)

    return InterviewResponse(
        reply=_INTERVIEW_DONE_REPLY,
        done=True,
        feedback=feedback,
        progress=_build_progress(final_session),
    )
