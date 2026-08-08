"""Tests for interview session management.

Covers:
- Session creation and unique sessionId generation
- Candidate profile association
- Conversation history storage and retrieval
- Questions asked storage
- Curriculum days covered storage
- Interview progress updates
- Retrieval of an existing session
- Handling of an unknown sessionId
- Session isolation
- Session completion and removal
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.exceptions import CandidateNotFoundError, SessionNotFoundError
from app.models.candidate import Candidate
from app.models.session import InterviewSession, InterviewStatus
from app.services.candidate_service import get_candidate_by_id
from app.services.session_service import SessionManager

# ---------------------------------------------------------------------------
# Paths to the real data files for loading test candidates
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data"
CANDIDATES_PATH = DATA_DIR / "candidates.json"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def manager() -> SessionManager:
    """Provide a fresh, empty SessionManager for each test."""
    return SessionManager()


@pytest.fixture
def sample_candidate() -> Candidate:
    """Load a real candidate from the data files."""
    return get_candidate_by_id("CAND-001", path=CANDIDATES_PATH)


@pytest.fixture
def second_candidate() -> Candidate:
    """Load a second real candidate for isolation tests."""
    return get_candidate_by_id("CAND-002", path=CANDIDATES_PATH)


# ===========================================================================
# Session creation
# ===========================================================================


class TestSessionCreation:
    """Tests for creating interview sessions."""

    def test_create_session_returns_interview_session(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        assert isinstance(session, InterviewSession)

    def test_create_session_has_session_id(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        assert session.sessionId
        assert isinstance(session.sessionId, str)

    def test_create_session_generates_unique_ids(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        s1 = manager.create_session(sample_candidate)
        s2 = manager.create_session(sample_candidate)
        assert s1.sessionId != s2.sessionId

    def test_create_session_with_explicit_id(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate, session_id="custom-123")
        assert session.sessionId == "custom-123"

    def test_create_session_is_active_by_default(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        assert session.status == InterviewStatus.ACTIVE

    def test_create_session_has_empty_history(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        assert session.history == []

    def test_create_session_has_empty_questions(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        assert session.questionsAsked == []

    def test_create_session_has_empty_curriculum_days(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        assert session.curriculumDaysCovered == []

    def test_session_count_increments(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        assert manager.session_count() == 0
        manager.create_session(sample_candidate)
        assert manager.session_count() == 1
        manager.create_session(sample_candidate)
        assert manager.session_count() == 2


# ===========================================================================
# Candidate profile association
# ===========================================================================


class TestCandidateAssociation:
    """Tests for associating a candidate with a session."""

    def test_session_stores_candidate(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        assert session.candidate == sample_candidate

    def test_session_preserves_candidate_id(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        assert session.candidate.member.id == "CAND-001"

    def test_session_preserves_candidate_name(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        assert session.candidate.member.name == "Sarah Johnson"

    def test_different_candidates_create_independent_sessions(
        self,
        manager: SessionManager,
        sample_candidate: Candidate,
        second_candidate: Candidate,
    ) -> None:
        s1 = manager.create_session(sample_candidate)
        s2 = manager.create_session(second_candidate)
        assert s1.candidate.member.id != s2.candidate.member.id
        assert s1.sessionId != s2.sessionId


# ===========================================================================
# Session retrieval
# ===========================================================================


class TestSessionRetrieval:
    """Tests for retrieving sessions by ID."""

    def test_get_existing_session(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        created = manager.create_session(sample_candidate)
        retrieved = manager.get_session(created.sessionId)
        assert retrieved.sessionId == created.sessionId

    def test_get_unknown_session_raises(self, manager: SessionManager) -> None:
        with pytest.raises(SessionNotFoundError) as exc_info:
            manager.get_session("nonexistent-session")
        assert exc_info.value.session_id == "nonexistent-session"

    def test_get_session_after_removal_raises(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        manager.remove_session(session.sessionId)
        with pytest.raises(SessionNotFoundError):
            manager.get_session(session.sessionId)


# ===========================================================================
# Conversation history
# ===========================================================================


class TestConversationHistory:
    """Tests for conversation history storage and retrieval."""

    def test_add_interviewer_message(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        updated = manager.add_message(session.sessionId, "interviewer", "Hello, let's begin.")
        assert len(updated.history) == 1
        assert updated.history[0].role == "interviewer"
        assert updated.history[0].content == "Hello, let's begin."

    def test_add_candidate_message(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        updated = manager.add_message(session.sessionId, "candidate", "I'm ready.")
        assert updated.history[0].role == "candidate"
        assert updated.history[0].content == "I'm ready."

    def test_multiple_messages_preserve_order(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        sid = session.sessionId
        manager.add_message(sid, "interviewer", "Q1")
        manager.add_message(sid, "candidate", "A1")
        manager.add_message(sid, "interviewer", "Q2")
        result = manager.add_message(sid, "candidate", "A2")
        assert len(result.history) == 4
        assert [m.content for m in result.history] == ["Q1", "A1", "Q2", "A2"]

    def test_message_has_timestamp(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        updated = manager.add_message(session.sessionId, "interviewer", "Hi")
        assert updated.history[0].timestamp is not None

    def test_add_message_to_unknown_session_raises(self, manager: SessionManager) -> None:
        with pytest.raises(SessionNotFoundError):
            manager.add_message("bad-id", "interviewer", "Hi")


# ===========================================================================
# Questions asked
# ===========================================================================


class TestQuestionsAsked:
    """Tests for questions asked storage."""

    def test_add_question(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        updated = manager.add_question(session.sessionId, day=7, question="What are embeddings?")
        assert len(updated.questionsAsked) == 1
        assert updated.questionsAsked[0].day == 7
        assert updated.questionsAsked[0].question == "What are embeddings?"

    def test_add_multiple_questions(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        sid = session.sessionId
        manager.add_question(sid, day=7, question="Q about embeddings")
        result = manager.add_question(sid, day=12, question="Q about prompting")
        assert len(result.questionsAsked) == 2

    def test_add_question_increments_progress_counter(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        sid = session.sessionId
        assert session.progress.questionsAsked == 0
        updated = manager.add_question(sid, day=7, question="Q1")
        assert updated.progress.questionsAsked == 1
        updated = manager.add_question(sid, day=8, question="Q2")
        assert updated.progress.questionsAsked == 2

    def test_add_question_updates_current_day(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        updated = manager.add_question(session.sessionId, day=12, question="Q")
        assert updated.progress.currentDay == 12

    def test_add_question_to_unknown_session_raises(self, manager: SessionManager) -> None:
        with pytest.raises(SessionNotFoundError):
            manager.add_question("bad-id", day=1, question="Q")


# ===========================================================================
# Curriculum days covered
# ===========================================================================


class TestCurriculumDaysCovered:
    """Tests for curriculum days covered storage."""

    def test_add_question_records_day(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        updated = manager.add_question(session.sessionId, day=7, question="Q")
        assert 7 in updated.curriculumDaysCovered

    def test_same_day_not_duplicated(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        sid = session.sessionId
        manager.add_question(sid, day=7, question="Q1")
        updated = manager.add_question(sid, day=7, question="Q2")
        assert updated.curriculumDaysCovered.count(7) == 1

    def test_multiple_days_tracked(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        sid = session.sessionId
        manager.add_question(sid, day=7, question="Q1")
        manager.add_question(sid, day=12, question="Q2")
        updated = manager.add_question(sid, day=22, question="Q3")
        assert sorted(updated.curriculumDaysCovered) == [7, 12, 22]


# ===========================================================================
# Interview progress
# ===========================================================================


class TestInterviewProgress:
    """Tests for interview progress updates."""

    def test_initial_progress(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        assert session.progress.currentDay == 1
        assert session.progress.totalDays == 31
        assert session.progress.questionsAsked == 0
        assert session.progress.questionsAnswered == 0

    def test_record_answer_increments_counter(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        sid = session.sessionId
        updated = manager.record_answer(sid)
        assert updated.progress.questionsAnswered == 1
        updated = manager.record_answer(sid)
        assert updated.progress.questionsAnswered == 2

    def test_update_progress_fields(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        updated = manager.update_progress(
            session.sessionId, currentDay=15, totalDays=31
        )
        assert updated.progress.currentDay == 15
        assert updated.progress.totalDays == 31

    def test_record_answer_on_unknown_session_raises(self, manager: SessionManager) -> None:
        with pytest.raises(SessionNotFoundError):
            manager.record_answer("bad-id")

    def test_update_progress_on_unknown_session_raises(self, manager: SessionManager) -> None:
        with pytest.raises(SessionNotFoundError):
            manager.update_progress("bad-id", currentDay=5)


# ===========================================================================
# Session completion and removal
# ===========================================================================


class TestSessionCompletionAndRemoval:
    """Tests for completing and removing sessions."""

    def test_complete_session(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        updated = manager.complete_session(session.sessionId)
        assert updated.status == InterviewStatus.COMPLETED

    def test_complete_unknown_session_raises(self, manager: SessionManager) -> None:
        with pytest.raises(SessionNotFoundError):
            manager.complete_session("bad-id")

    def test_remove_session(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        session = manager.create_session(sample_candidate)
        assert manager.session_count() == 1
        manager.remove_session(session.sessionId)
        assert manager.session_count() == 0

    def test_remove_unknown_session_raises(self, manager: SessionManager) -> None:
        with pytest.raises(SessionNotFoundError):
            manager.remove_session("bad-id")

    def test_list_sessions(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        s1 = manager.create_session(sample_candidate)
        s2 = manager.create_session(sample_candidate)
        sessions = manager.list_sessions()
        ids = {s.sessionId for s in sessions}
        assert s1.sessionId in ids
        assert s2.sessionId in ids

    def test_clear_removes_all_sessions(
        self, manager: SessionManager, sample_candidate: Candidate
    ) -> None:
        manager.create_session(sample_candidate)
        manager.create_session(sample_candidate)
        assert manager.session_count() == 2
        manager.clear()
        assert manager.session_count() == 0


# ===========================================================================
# Session isolation
# ===========================================================================


class TestSessionIsolation:
    """Tests ensuring data from one session cannot leak into another."""

    def test_conversation_history_isolation(
        self,
        manager: SessionManager,
        sample_candidate: Candidate,
        second_candidate: Candidate,
    ) -> None:
        s1 = manager.create_session(sample_candidate)
        s2 = manager.create_session(second_candidate)
        manager.add_message(s1.sessionId, "interviewer", "Question for S1")
        manager.add_message(s2.sessionId, "interviewer", "Question for S2")
        r1 = manager.get_session(s1.sessionId)
        r2 = manager.get_session(s2.sessionId)
        assert len(r1.history) == 1
        assert r1.history[0].content == "Question for S1"
        assert len(r2.history) == 1
        assert r2.history[0].content == "Question for S2"

    def test_questions_asked_isolation(
        self,
        manager: SessionManager,
        sample_candidate: Candidate,
        second_candidate: Candidate,
    ) -> None:
        s1 = manager.create_session(sample_candidate)
        s2 = manager.create_session(second_candidate)
        manager.add_question(s1.sessionId, day=7, question="Q for S1")
        manager.add_question(s2.sessionId, day=12, question="Q for S2")
        r1 = manager.get_session(s1.sessionId)
        r2 = manager.get_session(s2.sessionId)
        assert len(r1.questionsAsked) == 1
        assert r1.questionsAsked[0].question == "Q for S1"
        assert len(r2.questionsAsked) == 1
        assert r2.questionsAsked[0].question == "Q for S2"

    def test_curriculum_days_isolation(
        self,
        manager: SessionManager,
        sample_candidate: Candidate,
        second_candidate: Candidate,
    ) -> None:
        s1 = manager.create_session(sample_candidate)
        s2 = manager.create_session(second_candidate)
        manager.add_question(s1.sessionId, day=7, question="Q")
        manager.add_question(s2.sessionId, day=22, question="Q")
        r1 = manager.get_session(s1.sessionId)
        r2 = manager.get_session(s2.sessionId)
        assert r1.curriculumDaysCovered == [7]
        assert r2.curriculumDaysCovered == [22]

    def test_progress_isolation(
        self,
        manager: SessionManager,
        sample_candidate: Candidate,
        second_candidate: Candidate,
    ) -> None:
        s1 = manager.create_session(sample_candidate)
        s2 = manager.create_session(second_candidate)
        manager.add_question(s1.sessionId, day=7, question="Q1")
        manager.add_question(s1.sessionId, day=8, question="Q2")
        manager.add_question(s2.sessionId, day=22, question="Q3")
        r1 = manager.get_session(s1.sessionId)
        r2 = manager.get_session(s2.sessionId)
        assert r1.progress.questionsAsked == 2
        assert r2.progress.questionsAsked == 1

    def test_candidate_isolation(
        self,
        manager: SessionManager,
        sample_candidate: Candidate,
        second_candidate: Candidate,
    ) -> None:
        s1 = manager.create_session(sample_candidate)
        s2 = manager.create_session(second_candidate)
        r1 = manager.get_session(s1.sessionId)
        r2 = manager.get_session(s2.sessionId)
        assert r1.candidate.member.id == "CAND-001"
        assert r2.candidate.member.id == "CAND-002"

    def test_removal_does_not_affect_other_sessions(
        self,
        manager: SessionManager,
        sample_candidate: Candidate,
        second_candidate: Candidate,
    ) -> None:
        s1 = manager.create_session(sample_candidate)
        s2 = manager.create_session(second_candidate)
        manager.add_message(s1.sessionId, "interviewer", "Q1")
        manager.remove_session(s1.sessionId)
        # s2 should still be fully accessible
        r2 = manager.get_session(s2.sessionId)
        assert r2.candidate.member.id == "CAND-002"
        # s1 should be gone
        with pytest.raises(SessionNotFoundError):
            manager.get_session(s1.sessionId)
