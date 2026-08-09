"""End-to-end interview lifecycle tests.

Covers the hackathon requirements:
- 8 primary interview questions
- 4 curriculum days
- Follow-up questions
- Conversation memory / context
- Structured feedback
- API contract
- Interview state machine
- Edge cases: completed session, invalid transitions
- Progress tracking
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.session_service import SessionManager
from app.services.llm_service import StubLLMService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client() -> TestClient:
    """Fresh TestClient with isolated session/LLM state per test."""
    manager = SessionManager()
    llm_service = StubLLMService()

    app.dependency_overrides.clear()
    from app.routes.interviews import get_session_manager, get_llm_service
    app.dependency_overrides[get_session_manager] = lambda: manager
    app.dependency_overrides[get_llm_service] = lambda: llm_service

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


SAMPLE_CANDIDATE = {
    "member": {
        "id": "CAND-001",
        "name": "Sarah Johnson",
        "jobRole": "Senior Data Engineer",
        "yearsExperience": 9,
        "education": "MS Computer Science",
        "status": "COMPLETED",
    },
    "missions": [
        {"day": 1, "title": "Setup", "passed": True, "attempts": 1, "skipped": None},
        {"day": 2, "title": "LLM Setup", "passed": True, "attempts": 2, "skipped": None},
    ],
    "signals": {"commitDays": 28, "missionsCompleted": 30, "missionsFirstTry": 20},
}


def _start(client: TestClient, sid: str = "s1") -> dict:
    """Start a session and return the JSON response."""
    resp = client.post(
        "/api/interview",
        json={"sessionId": sid, "candidate": SAMPLE_CANDIDATE},
    )
    return resp.json()


def _continue(client: TestClient, sid: str = "s1", msg: str = "Answer") -> dict:
    """Continue a session and return the JSON response."""
    resp = client.post(
        "/api/interview",
        json={"sessionId": sid, "message": msg},
    )
    return resp.json()


def _end(client: TestClient, sid: str = "s1") -> dict:
    """End a session and return the JSON response."""
    resp = client.post(
        "/api/interview",
        json={"sessionId": sid, "done": True},
    )
    return resp.json()


# ===========================================================================
# 1. Interview State Machine
# ===========================================================================

class TestInterviewStateMachine:
    """Verify the full interview lifecycle."""

    def test_start_creates_active_session(self, client: TestClient) -> None:
        data = _start(client)
        assert data["done"] is False
        assert data["reply"] == "Welcome. Let's begin your interview."
        assert data["feedback"] is None
        assert "progress" in data

    def test_continue_after_start(self, client: TestClient) -> None:
        _start(client)
        data = _continue(client, msg="I have 5 years of Python experience")
        assert data["done"] is False
        assert isinstance(data["reply"], str)
        assert len(data["reply"]) > 0

    def test_end_returns_done_true_with_feedback(self, client: TestClient) -> None:
        _start(client)
        _continue(client, msg="I know Python")
        data = _end(client)
        assert data["done"] is True
        assert data["feedback"] is not None
        assert "summary" in data["feedback"]
        assert "strengths" in data["feedback"]
        assert "gaps" in data["feedback"]
        assert "next" in data["feedback"]

    def test_cannot_continue_after_end(self, client: TestClient) -> None:
        """A completed session must reject further messages."""
        _start(client)
        _continue(client, msg="Some answer")
        _end(client)
        resp = client.post(
            "/api/interview",
            json={"sessionId": "s1", "message": "Another answer"},
        )
        assert resp.status_code == 409

    def test_cannot_end_after_end(self, client: TestClient) -> None:
        """Ending a completed session again must fail."""
        _start(client)
        _continue(client, msg="Some answer")
        _end(client)
        resp = client.post(
            "/api/interview",
            json={"sessionId": "s1", "done": True},
        )
        assert resp.status_code == 409

    def test_unknown_session_returns_404(self, client: TestClient) -> None:
        resp = client.post(
            "/api/interview",
            json={"sessionId": "nonexistent", "message": "hello"},
        )
        assert resp.status_code == 404


# ===========================================================================
# 2. Progress Tracking (8 Questions, 4 Curriculum Days)
# ===========================================================================

class TestProgressTracking:
    """Verify that progress is tracked correctly in every response."""

    def test_start_progress_is_zero(self, client: TestClient) -> None:
        data = _start(client)
        p = data["progress"]
        assert p["questionsAsked"] == 0
        assert p["questionsAnswered"] == 0
        assert p["curriculumDaysCovered"] == 0

    def test_continue_increments_questions_asked(self, client: TestClient) -> None:
        _start(client)
        data = _continue(client, msg="Answer 1")
        assert data["progress"]["questionsAsked"] == 1
        assert data["progress"]["questionsAnswered"] == 1

    def test_multiple_continues_track_progress(self, client: TestClient) -> None:
        _start(client)
        for i in range(5):
            data = _continue(client, msg=f"Answer {i + 1}")
        assert data["progress"]["questionsAsked"] == 5
        assert data["progress"]["questionsAnswered"] == 5

    def test_progress_included_in_end_response(self, client: TestClient) -> None:
        _start(client)
        _continue(client, msg="Answer 1")
        _continue(client, msg="Answer 2")
        data = _end(client)
        assert "progress" in data
        assert data["progress"]["questionsAsked"] == 2
        assert data["progress"]["questionsAnswered"] == 2

    def test_8_question_interview_progress(self, client: TestClient) -> None:
        """Simulate an 8-question interview and verify progress."""
        _start(client)
        for i in range(8):
            data = _continue(client, msg=f"Answer to question {i + 1}")
        assert data["progress"]["questionsAsked"] == 8
        assert data["progress"]["questionsAnswered"] == 8

    def test_curriculum_days_covered_increases(self, client: TestClient) -> None:
        """At least 1 day should be covered after continuing."""
        _start(client)
        data = _continue(client, msg="Answer 1")
        assert data["progress"]["curriculumDaysCovered"] >= 1


# ===========================================================================
# 3. Conversation Memory / Context
# ===========================================================================

class TestConversationMemory:
    """Verify that conversation history grows and is maintained."""

    def test_history_grows_with_each_turn(self, client: TestClient) -> None:
        _start(client)
        data = _continue(client, msg="My first answer")
        assert data["progress"]["questionsAnswered"] == 1

    def test_multiple_answers_accumulate(self, client: TestClient) -> None:
        _start(client)
        for i in range(3):
            _continue(client, msg=f"Answer {i + 1}")
        data = _continue(client, msg="Answer 4")
        assert data["progress"]["questionsAnswered"] == 4

    def test_different_sessions_are_independent(self, client: TestClient) -> None:
        _start(client, sid="s1")
        _start(client, sid="s2")
        _continue(client, sid="s1", msg="Answer for s1")
        data = _continue(client, sid="s2", msg="Answer for s2")
        assert data["progress"]["questionsAnswered"] == 1


# ===========================================================================
# 4. Structured Feedback
# ===========================================================================

class TestStructuredFeedback:
    """Verify the complete feedback pipeline."""

    def test_feedback_has_required_fields(self, client: TestClient) -> None:
        _start(client)
        _continue(client, msg="I know Python")
        data = _end(client)
        fb = data["feedback"]
        assert isinstance(fb["summary"], str)
        assert isinstance(fb["strengths"], list)
        assert isinstance(fb["gaps"], list)
        assert isinstance(fb["next"], list)

    def test_feedback_arrays_contain_strings(self, client: TestClient) -> None:
        _start(client)
        _continue(client, msg="I know Python")
        data = _end(client)
        fb = data["feedback"]
        for s in fb["strengths"]:
            assert isinstance(s, str)
        for g in fb["gaps"]:
            assert isinstance(g, str)
        for n in fb["next"]:
            assert isinstance(n, str)

    def test_done_true_response_structure(self, client: TestClient) -> None:
        _start(client)
        _continue(client, msg="Answer")
        data = _end(client)
        assert data["done"] is True
        assert data["reply"] == "Interview completed."
        assert data["feedback"] is not None


# ===========================================================================
# 5. API Contract
# ===========================================================================

class TestAPIContract:
    """Verify the POST /api/interview contract."""

    def test_start_shape(self, client: TestClient) -> None:
        resp = client.post(
            "/api/interview",
            json={"sessionId": "test-start", "candidate": SAMPLE_CANDIDATE},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data
        assert "done" in data
        assert "feedback" in data
        assert "progress" in data

    def test_continue_shape(self, client: TestClient) -> None:
        _start(client, sid="test-cont")
        resp = client.post(
            "/api/interview",
            json={"sessionId": "test-cont", "message": "Hello"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data
        assert "done" in data
        assert data["done"] is False

    def test_end_shape(self, client: TestClient) -> None:
        _start(client, sid="test-end")
        _continue(client, sid="test-end", msg="Answer")
        resp = client.post(
            "/api/interview",
            json={"sessionId": "test-end", "done": True},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["done"] is True
        assert data["feedback"] is not None

    def test_invalid_request_returns_422(self, client: TestClient) -> None:
        resp = client.post(
            "/api/interview",
            json={"sessionId": "test-bad"},
        )
        assert resp.status_code == 422

    def test_done_false_without_message_returns_422(self, client: TestClient) -> None:
        resp = client.post(
            "/api/interview",
            json={"sessionId": "test-bad", "done": False},
        )
        assert resp.status_code == 422


# ===========================================================================
# 6. Prompt Builder Integration
# ===========================================================================

class TestPromptBuilderIntegration:
    """Verify that the prompt builder receives correct context."""

    def test_prompt_includes_eight_question_rule(self) -> None:
        from app.services.prompt_builder import _SYSTEM_RULES
        assert "8" in _SYSTEM_RULES or "eight" in _SYSTEM_RULES.lower()

    def test_prompt_includes_four_day_rule(self) -> None:
        from app.services.prompt_builder import _SYSTEM_RULES
        assert "4" in _SYSTEM_RULES or "four" in _SYSTEM_RULES.lower()

    def test_prompt_includes_followup_rule(self) -> None:
        from app.services.prompt_builder import _SYSTEM_RULES
        assert "follow-up" in _SYSTEM_RULES.lower() or "follow up" in _SYSTEM_RULES.lower()

    def test_prompt_includes_no_repeat_rule(self) -> None:
        from app.services.prompt_builder import _SYSTEM_RULES
        assert "repeat" in _SYSTEM_RULES.lower()

    def test_prompt_includes_conversation_context_rule(self) -> None:
        from app.services.prompt_builder import _SYSTEM_RULES
        assert "context" in _SYSTEM_RULES.lower() or "previous" in _SYSTEM_RULES.lower()


# ===========================================================================
# 7. Curriculum and Candidate Data
# ===========================================================================

class TestCurriculumCandidateData:
    """Verify data loading from JSON files."""

    def test_curriculum_has_31_days(self) -> None:
        from app.services.curriculum_service import get_curriculum
        c = get_curriculum()
        assert len(c.days) == 31

    def test_curriculum_has_8_modules(self) -> None:
        from app.services.curriculum_service import get_curriculum
        c = get_curriculum()
        assert len(c.modules) == 8

    def test_candidates_load(self) -> None:
        from app.services.candidate_service import get_candidates
        cands = get_candidates()
        assert len(cands) > 0

    def test_candidate_lookup_works(self) -> None:
        from app.services.candidate_service import get_candidate_by_id
        c = get_candidate_by_id("CAND-001")
        assert c.member.name == "Sarah Johnson"

    def test_candidate_has_missions_and_signals(self) -> None:
        from app.services.candidate_service import get_candidate_by_id
        c = get_candidate_by_id("CAND-001")
        assert len(c.missions) > 0
        assert c.signals.commitDays > 0


# ===========================================================================
# 8. LLM Service Abstraction
# ===========================================================================

class TestLLMAbstraction:
    """Verify the LLM service interface."""

    def test_stub_llm_returns_string(self) -> None:
        import asyncio
        stub = StubLLMService()
        result = asyncio.run(stub.generate([{"role": "user", "content": "test"}]))
        assert isinstance(result, str)

    def test_stub_llm_returns_default_reply(self) -> None:
        import asyncio
        stub = StubLLMService()
        result = asyncio.run(stub.generate([{"role": "user", "content": "test"}]))
        assert result == "Thank you for your response. Let's continue."

    def test_custom_stub_reply(self) -> None:
        import asyncio
        stub = StubLLMService(reply="Custom reply")
        result = asyncio.run(stub.generate([{"role": "user", "content": "test"}]))
        assert result == "Custom reply"
