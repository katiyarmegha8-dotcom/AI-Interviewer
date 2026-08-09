"""Tests for the interview prompt builder.

Covers:
- System prompt includes interview rules
- Candidate profile is included
- Curriculum context is included (covered and remaining days)
- Previously asked questions are listed
- Interview objectives and progress are included
- Conversation history is mapped to LLM roles
- Empty session state is handled correctly
- No candidate-specific information is hardcoded in the rules
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.models.candidate import Candidate
from app.models.curriculum import Curriculum
from app.models.session import InterviewSession
from app.services.candidate_service import get_candidate_by_id
from app.services.curriculum_service import get_curriculum
from app.services.prompt_builder import (
    _build_candidate_profile,
    _build_curriculum_context,
    _build_interview_objectives,
    _build_previously_asked_questions,
    _SYSTEM_RULES,
    build_interview_messages,
)
from app.services.session_service import SessionManager

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data"
CANDIDATES_PATH = DATA_DIR / "candidates.json"
CURRICULUM_PATH = DATA_DIR / "curriculum.json"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def curriculum() -> Curriculum:
    return get_curriculum(path=CURRICULUM_PATH)


@pytest.fixture
def candidate() -> Candidate:
    return get_candidate_by_id("CAND-001", path=CANDIDATES_PATH)


@pytest.fixture
def session(candidate: Candidate) -> InterviewSession:
    return InterviewSession(sessionId="test-1", candidate=candidate)


# ===========================================================================
# System prompt rules
# ===========================================================================


class TestSystemRules:
    """Tests for the static interview rules in the system prompt."""

    def test_rules_ask_one_question(self) -> None:
        assert "ONE question at a time" in _SYSTEM_RULES

    def test_rules_cover_four_days(self) -> None:
        assert "four" in _SYSTEM_RULES and "curriculum days" in _SYSTEM_RULES

    def test_rules_ask_eight_questions(self) -> None:
        assert "eight" in _SYSTEM_RULES and "questions" in _SYSTEM_RULES

    def test_rules_no_repeats(self) -> None:
        assert "repeat" in _SYSTEM_RULES.lower()

    def test_rules_adapt_questions(self) -> None:
        assert "Adapt" in _SYSTEM_RULES or "adapt" in _SYSTEM_RULES

    def test_rules_maintain_context(self) -> None:
        assert "context" in _SYSTEM_RULES.lower()

    def test_rules_no_hardcoded_candidate_info(self) -> None:
        """Rules must not contain any specific candidate names or IDs."""
        assert "CAND-" not in _SYSTEM_RULES
        assert "Sarah" not in _SYSTEM_RULES
        assert "John" not in _SYSTEM_RULES


# ===========================================================================
# Candidate profile
# ===========================================================================


class TestCandidateProfile:
    """Tests for the candidate profile section."""

    def test_includes_name(self, candidate: Candidate) -> None:
        profile = _build_candidate_profile(candidate)
        assert "Sarah Johnson" in profile

    def test_includes_role(self, candidate: Candidate) -> None:
        profile = _build_candidate_profile(candidate)
        assert "Senior Data Engineer" in profile

    def test_includes_experience(self, candidate: Candidate) -> None:
        profile = _build_candidate_profile(candidate)
        assert "9 years" in profile

    def test_includes_education(self, candidate: Candidate) -> None:
        profile = _build_candidate_profile(candidate)
        assert "MS Computer Science" in profile

    def test_includes_missions(self, candidate: Candidate) -> None:
        profile = _build_candidate_profile(candidate)
        assert "Missions passed:" in profile or "Missions failed:" in profile or "Missions skipped:" in profile

    def test_includes_signals(self, candidate: Candidate) -> None:
        profile = _build_candidate_profile(candidate)
        assert "commit days" in profile
        assert "missions completed" in profile
        assert "first-try passes" in profile


# ===========================================================================
# Curriculum context
# ===========================================================================


class TestCurriculumContext:
    """Tests for the curriculum context section."""

    def test_includes_modules(self, curriculum: Curriculum) -> None:
        ctx = _build_curriculum_context(curriculum, days_covered=[])
        assert "Module 1" in ctx
        assert "Environment & Tooling" in ctx

    def test_shows_no_days_covered(self, curriculum: Curriculum) -> None:
        ctx = _build_curriculum_context(curriculum, days_covered=[])
        assert "No curriculum days have been covered yet" in ctx

    def test_shows_covered_days(self, curriculum: Curriculum) -> None:
        ctx = _build_curriculum_context(curriculum, days_covered=[7, 12])
        assert "already covered" in ctx
        assert "Day 7" in ctx
        assert "Day 12" in ctx

    def test_shows_remaining_days(self, curriculum: Curriculum) -> None:
        ctx = _build_curriculum_context(curriculum, days_covered=[7])
        assert "Remaining" in ctx

    def test_shows_day_objectives_for_covered(self, curriculum: Curriculum) -> None:
        ctx = _build_curriculum_context(curriculum, days_covered=[7])
        assert "objectives:" in ctx

    def test_all_days_covered_no_remaining(self, curriculum: Curriculum) -> None:
        all_days = [d.day for d in curriculum.days]
        ctx = _build_curriculum_context(curriculum, days_covered=all_days)
        assert "already covered" in ctx
        assert "Remaining" not in ctx


# ===========================================================================
# Previously asked questions
# ===========================================================================


class TestPreviouslyAskedQuestions:
    """Tests for the previously asked questions section."""

    def test_no_questions_yet(self, session: InterviewSession) -> None:
        result = _build_previously_asked_questions(session)
        assert "No questions have been asked yet" in result

    def test_lists_asked_questions(self, candidate: Candidate) -> None:
        manager = SessionManager()
        manager.create_session(candidate, session_id="t")
        manager.add_question("t", day=7, question="What are embeddings?")
        manager.add_question("t", day=12, question="Explain prompt engineering.")
        session = manager.get_session("t")
        result = _build_previously_asked_questions(session)
        assert "What are embeddings?" in result
        assert "Explain prompt engineering." in result
        assert "[Day 7]" in result
        assert "[Day 12]" in result

    def test_includes_do_not_repeat_instruction(self, candidate: Candidate) -> None:
        manager = SessionManager()
        manager.create_session(candidate, session_id="t")
        manager.add_question("t", day=7, question="Q1")
        session = manager.get_session("t")
        result = _build_previously_asked_questions(session)
        assert "do NOT repeat" in result


# ===========================================================================
# Interview objectives
# ===========================================================================


class TestInterviewObjectives:
    """Tests for the interview objectives section."""

    def test_initial_objectives(self, session: InterviewSession) -> None:
        result = _build_interview_objectives(session)
        assert "Cover at least 4 curriculum days" in result
        assert "Ask at least 8 questions" in result

    def test_shows_progress(self, candidate: Candidate) -> None:
        manager = SessionManager()
        manager.create_session(candidate, session_id="t")
        manager.add_question("t", day=7, question="Q1")
        manager.add_question("t", day=8, question="Q2")
        session = manager.get_session("t")
        result = _build_interview_objectives(session)
        assert "currently asked: 2" in result

    def test_shows_still_need(self, session: InterviewSession) -> None:
        result = _build_interview_objectives(session)
        assert "Still need to" in result

    def test_thresholds_met(self, candidate: Candidate) -> None:
        manager = SessionManager()
        manager.create_session(candidate, session_id="t")
        for day in [7, 8, 10, 12]:
            manager.add_question("t", day=day, question=f"Q for day {day}")
        # Add more questions to reach 8
        for i in range(4):
            manager.add_question("t", day=13, question=f"Extra Q {i}")
        session = manager.get_session("t")
        result = _build_interview_objectives(session)
        assert "Minimum thresholds met" in result


# ===========================================================================
# Full message list
# ===========================================================================


class TestBuildInterviewMessages:
    """Tests for the complete build_interview_messages output."""

    def test_first_message_is_system(
        self,
        session: InterviewSession,
        curriculum: Curriculum,
    ) -> None:
        messages = build_interview_messages(session, curriculum)
        assert messages[0]["role"] == "system"

    def test_system_includes_candidate_profile(
        self,
        session: InterviewSession,
        curriculum: Curriculum,
    ) -> None:
        messages = build_interview_messages(session, curriculum)
        system = messages[0]["content"]
        assert "## Candidate Profile" in system
        assert "Sarah Johnson" in system

    def test_system_includes_curriculum(
        self,
        session: InterviewSession,
        curriculum: Curriculum,
    ) -> None:
        messages = build_interview_messages(session, curriculum)
        system = messages[0]["content"]
        assert "## Curriculum" in system

    def test_system_includes_questions(
        self,
        session: InterviewSession,
        curriculum: Curriculum,
    ) -> None:
        messages = build_interview_messages(session, curriculum)
        system = messages[0]["content"]
        assert "## Previously Asked Questions" in system

    def test_system_includes_objectives(
        self,
        session: InterviewSession,
        curriculum: Curriculum,
    ) -> None:
        messages = build_interview_messages(session, curriculum)
        system = messages[0]["content"]
        assert "## Interview Objectives" in system

    def test_system_includes_rules(
        self,
        session: InterviewSession,
        curriculum: Curriculum,
    ) -> None:
        messages = build_interview_messages(session, curriculum)
        system = messages[0]["content"]
        assert "Interview rules" in system

    def test_no_history_returns_only_system(
        self,
        session: InterviewSession,
        curriculum: Curriculum,
    ) -> None:
        messages = build_interview_messages(session, curriculum)
        assert len(messages) == 1

    def test_history_mapped_to_llm_roles(
        self,
        candidate: Candidate,
        curriculum: Curriculum,
    ) -> None:
        manager = SessionManager()
        manager.create_session(candidate, session_id="t")
        manager.add_message("t", "interviewer", "Welcome!")
        manager.add_message("t", "candidate", "Hi, I'm ready.")
        session = manager.get_session("t")

        messages = build_interview_messages(session, curriculum)
        # system + 2 history messages
        assert len(messages) == 3
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "Welcome!"
        assert messages[2]["role"] == "user"
        assert messages[2]["content"] == "Hi, I'm ready."

    def test_messages_are_dict_format(
        self,
        session: InterviewSession,
        curriculum: Curriculum,
    ) -> None:
        messages = build_interview_messages(session, curriculum)
        for msg in messages:
            assert "role" in msg
            assert "content" in msg
            assert isinstance(msg["role"], str)
            assert isinstance(msg["content"], str)

    def test_covered_days_appear_in_context(
        self,
        candidate: Candidate,
        curriculum: Curriculum,
    ) -> None:
        manager = SessionManager()
        manager.create_session(candidate, session_id="t")
        manager.add_question("t", day=7, question="What are embeddings?")
        session = manager.get_session("t")

        messages = build_interview_messages(session, curriculum)
        system = messages[0]["content"]
        assert "Day 7" in system

    def test_different_candidate_different_profile(
        self,
        curriculum: Curriculum,
    ) -> None:
        cand1 = get_candidate_by_id("CAND-001", path=CANDIDATES_PATH)
        cand2 = get_candidate_by_id("CAND-002", path=CANDIDATES_PATH)

        session1 = InterviewSession(sessionId="s1", candidate=cand1)
        session2 = InterviewSession(sessionId="s2", candidate=cand2)

        messages1 = build_interview_messages(session1, curriculum)
        messages2 = build_interview_messages(session2, curriculum)

        assert "Sarah Johnson" in messages1[0]["content"]
        assert "Alex Turner" in messages2[0]["content"]
        assert "Sarah Johnson" not in messages2[0]["content"]
