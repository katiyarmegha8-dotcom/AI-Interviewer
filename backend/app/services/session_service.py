"""In-memory interview session manager.

Provides operations for creating, retrieving, updating, and removing
interview sessions.  All state is held in process memory — suitable for
single-instance development and hackathon demos.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.exceptions import SessionNotFoundError
from app.models.candidate import Candidate
from app.models.session import (
    ConversationMessage,
    InterviewProgress,
    InterviewSession,
    InterviewStatus,
    QuestionAsked,
)


class SessionManager:
    """Manages interview sessions in memory.

    Each session is keyed by its unique ``sessionId``.  Sessions are
    completely isolated — data from one session cannot leak into another.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, InterviewSession] = {}

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create_session(
        self,
        candidate: Candidate,
        session_id: str | None = None,
    ) -> InterviewSession:
        """Create a new interview session for a candidate.

        Args:
            candidate: The candidate to interview.
            session_id: Optional explicit session ID.  If ``None``, a
                        UUID4 is generated automatically.

        Returns:
            The newly created ``InterviewSession``.
        """
        sid = session_id or str(uuid4())
        session = InterviewSession(sessionId=sid, candidate=candidate)
        self._sessions[sid] = session
        return session

    # ------------------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------------------

    def get_session(self, session_id: str) -> InterviewSession:
        """Retrieve a session by its ID.

        Args:
            session_id: The session identifier.

        Returns:
            The matching ``InterviewSession``.

        Raises:
            SessionNotFoundError: If the session ID is unknown.
        """
        session = self._sessions.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)
        return session

    # ------------------------------------------------------------------
    # Conversation history
    # ------------------------------------------------------------------

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> InterviewSession:
        """Append a message to the session's conversation history.

        Args:
            session_id: The session identifier.
            role: Message origin (``"interviewer"`` or ``"candidate"``).
            content: Message text.

        Returns:
            The updated session.

        Raises:
            SessionNotFoundError: If the session ID is unknown.
        """
        session = self.get_session(session_id)
        msg = ConversationMessage(role=role, content=content)
        session.history.append(msg)
        session.updatedAt = datetime.now(timezone.utc)
        return session

    # ------------------------------------------------------------------
    # Questions asked
    # ------------------------------------------------------------------

    def add_question(
        self,
        session_id: str,
        day: int,
        question: str,
    ) -> InterviewSession:
        """Record a question asked during the interview.

        Also adds the day to ``curriculumDaysCovered`` if not already
        present, and increments ``progress.questionsAsked``.

        Args:
            session_id: The session identifier.
            day: Curriculum day number the question relates to.
            question: The question text.

        Returns:
            The updated session.

        Raises:
            SessionNotFoundError: If the session ID is unknown.
        """
        session = self.get_session(session_id)
        q = QuestionAsked(day=day, question=question)
        session.questionsAsked.append(q)
        if day not in session.curriculumDaysCovered:
            session.curriculumDaysCovered.append(day)
        session.progress.questionsAsked += 1
        session.progress.currentDay = day
        session.updatedAt = datetime.now(timezone.utc)
        return session

    # ------------------------------------------------------------------
    # Candidate answer tracking
    # ------------------------------------------------------------------

    def record_answer(self, session_id: str) -> InterviewSession:
        """Record that the candidate has provided an answer.

        Increments ``progress.questionsAnswered``.

        Args:
            session_id: The session identifier.

        Returns:
            The updated session.

        Raises:
            SessionNotFoundError: If the session ID is unknown.
        """
        session = self.get_session(session_id)
        session.progress.questionsAnswered += 1
        session.updatedAt = datetime.now(timezone.utc)
        return session

    # ------------------------------------------------------------------
    # Progress
    # ------------------------------------------------------------------

    def update_progress(
        self,
        session_id: str,
        **fields: int,
    ) -> InterviewSession:
        """Update interview progress fields.

        Accepts keyword arguments matching ``InterviewProgress`` field
        names (``currentDay``, ``totalDays``, ``questionsAsked``,
        ``questionsAnswered``).

        Args:
            session_id: The session identifier.
            **fields: Progress fields to update.

        Returns:
            The updated session.

        Raises:
            SessionNotFoundError: If the session ID is unknown.
        """
        session = self.get_session(session_id)
        progress = session.progress.model_copy(update=fields)
        session.progress = progress
        session.updatedAt = datetime.now(timezone.utc)
        return session

    # ------------------------------------------------------------------
    # Complete
    # ------------------------------------------------------------------

    def complete_session(self, session_id: str) -> InterviewSession:
        """Mark a session as completed.

        Args:
            session_id: The session identifier.

        Returns:
            The updated session with ``status=COMPLETED``.

        Raises:
            SessionNotFoundError: If the session ID is unknown.
        """
        session = self.get_session(session_id)
        session.status = InterviewStatus.COMPLETED
        session.updatedAt = datetime.now(timezone.utc)
        return session

    # ------------------------------------------------------------------
    # Remove
    # ------------------------------------------------------------------

    def remove_session(self, session_id: str) -> None:
        """Remove a session from the manager.

        Args:
            session_id: The session identifier.

        Raises:
            SessionNotFoundError: If the session ID is unknown.
        """
        if session_id not in self._sessions:
            raise SessionNotFoundError(session_id)
        del self._sessions[session_id]

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def list_sessions(self) -> list[InterviewSession]:
        """Return all active sessions."""
        return list(self._sessions.values())

    def session_count(self) -> int:
        """Return the number of managed sessions."""
        return len(self._sessions)

    def clear(self) -> None:
        """Remove all sessions (useful for testing)."""
        self._sessions.clear()
