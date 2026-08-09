"""Tests for the POST /api/interview endpoint.

Covers:
- First request / session creation
- Follow-up requests using sessionId
- Session state preservation between requests
- Request validation
- Invalid or missing required fields
- Unknown sessionId handling
- Exact response structure per technical specification
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.models.candidate import Candidate
from app.models.session import InterviewSession
from app.routes.interviews import get_session_manager
from app.services.candidate_service import get_candidate_by_id
from app.services.session_service import SessionManager

# ---------------------------------------------------------------------------
# Paths to the real data files
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data"
CANDIDATES_PATH = DATA_DIR / "candidates.json"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def manager() -> SessionManager:
    """Provide a fresh SessionManager for each test."""
    return SessionManager()


@pytest.fixture
def client(manager: SessionManager) -> TestClient:
    """Provide a TestClient with the SessionManager dependency overridden."""
    app = create_app()
    app.dependency_overrides[get_session_manager] = lambda: manager
    tc = TestClient(app)
    return tc


@pytest.fixture
def sample_candidate() -> Candidate:
    """Load a real candidate from the data files."""
    return get_candidate_by_id("CAND-001", path=CANDIDATES_PATH)


@pytest.fixture
def sample_candidate_dict() -> dict:
    """Return a candidate as a JSON-serializable dict."""
    candidate = get_candidate_by_id("CAND-001", path=CANDIDATES_PATH)
    return candidate.model_dump()


# ===========================================================================
# Session creation (first request)
# ===========================================================================


class TestStartInterview:
    """Tests for the first request that creates a session."""

    def test_start_returns_200(
        self,
        client: TestClient,
        sample_candidate_dict: dict,
    ) -> None:
        resp = client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        assert resp.status_code == 200

    def test_start_response_has_reply(
        self,
        client: TestClient,
        sample_candidate_dict: dict,
    ) -> None:
        resp = client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        data = resp.json()
        assert "reply" in data

    def test_start_response_has_done_false(
        self,
        client: TestClient,
        sample_candidate_dict: dict,
    ) -> None:
        resp = client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        data = resp.json()
        assert data["done"] is False

    def test_start_welcome_reply(
        self,
        client: TestClient,
        sample_candidate_dict: dict,
    ) -> None:
        """The spec requires the exact welcome message."""
        resp = client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        data = resp.json()
        assert data["reply"] == "Welcome. Let's begin your interview."

    def test_start_response_has_no_feedback(
        self,
        client: TestClient,
        sample_candidate_dict: dict,
    ) -> None:
        """Feedback must not be present when done=false."""
        resp = client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        data = resp.json()
        assert data.get("feedback") is None

    def test_start_creates_session_in_manager(
        self,
        client: TestClient,
        manager: SessionManager,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        session = manager.get_session("sess-1")
        assert session.sessionId == "sess-1"
        assert session.candidate.member.id == "CAND-001"

    def test_start_records_welcome_in_history(
        self,
        client: TestClient,
        manager: SessionManager,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        session = manager.get_session("sess-1")
        assert len(session.history) == 1
        assert session.history[0].role == "interviewer"
        assert session.history[0].content == "Welcome. Let's begin your interview."

    def test_start_with_different_session_ids(
        self,
        client: TestClient,
        manager: SessionManager,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-a", "candidate": sample_candidate_dict},
        )
        client.post(
            "/api/interview",
            json={"sessionId": "sess-b", "candidate": sample_candidate_dict},
        )
        assert manager.session_count() == 2
        assert manager.get_session("sess-a").sessionId == "sess-a"
        assert manager.get_session("sess-b").sessionId == "sess-b"


# ===========================================================================
# Follow-up requests
# ===========================================================================


class TestContinueInterview:
    """Tests for follow-up conversation turns."""

    def test_continue_returns_200(
        self,
        client: TestClient,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        resp = client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "I have experience with Python"},
        )
        assert resp.status_code == 200

    def test_continue_response_has_reply(
        self,
        client: TestClient,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        resp = client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "I have experience with Python"},
        )
        data = resp.json()
        assert "reply" in data

    def test_continue_response_has_done_false(
        self,
        client: TestClient,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        resp = client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "I have experience with Python"},
        )
        data = resp.json()
        assert data["done"] is False

    def test_continue_response_has_no_feedback(
        self,
        client: TestClient,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        resp = client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "I have experience with Python"},
        )
        data = resp.json()
        assert data.get("feedback") is None

    def test_continue_records_candidate_message(
        self,
        client: TestClient,
        manager: SessionManager,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "I know RAG pipelines"},
        )
        session = manager.get_session("sess-1")
        # welcome + candidate msg + interviewer reply = 3
        assert len(session.history) == 3
        candidate_msgs = [m for m in session.history if m.role == "candidate"]
        assert len(candidate_msgs) == 1
        assert candidate_msgs[0].content == "I know RAG pipelines"

    def test_multiple_continue_turns(
        self,
        client: TestClient,
        manager: SessionManager,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "Answer 1"},
        )
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "Answer 2"},
        )
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "Answer 3"},
        )
        session = manager.get_session("sess-1")
        candidate_msgs = [m for m in session.history if m.role == "candidate"]
        assert len(candidate_msgs) == 3
        assert session.progress.questionsAnswered == 3


# ===========================================================================
# Session state preservation
# ===========================================================================


class TestSessionStatePreservation:
    """Tests that session state is preserved across requests."""

    def test_candidate_profile_preserved(
        self,
        client: TestClient,
        manager: SessionManager,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "Answer 1"},
        )
        session = manager.get_session("sess-1")
        assert session.candidate.member.id == "CAND-001"
        assert session.candidate.member.name == "Sarah Johnson"

    def test_conversation_history_grows(
        self,
        client: TestClient,
        manager: SessionManager,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "Answer 1"},
        )
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "Answer 2"},
        )
        session = manager.get_session("sess-1")
        # welcome + (candidate answer + interviewer reply) * 2 = 5
        assert len(session.history) == 5

    def test_progress_updates_across_turns(
        self,
        client: TestClient,
        manager: SessionManager,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "Answer 1"},
        )
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "Answer 2"},
        )
        session = manager.get_session("sess-1")
        assert session.progress.questionsAnswered == 2


# ===========================================================================
# Request validation
# ===========================================================================


class TestRequestValidation:
    """Tests for invalid or missing request fields."""

    def test_missing_session_id_returns_422(
        self,
        client: TestClient,
        sample_candidate_dict: dict,
    ) -> None:
        resp = client.post(
            "/api/interview",
            json={"candidate": sample_candidate_dict},
        )
        assert resp.status_code == 422

    def test_missing_both_candidate_and_message_returns_422(
        self,
        client: TestClient,
    ) -> None:
        """Must have either candidate or message."""
        resp = client.post(
            "/api/interview",
            json={"sessionId": "sess-1"},
        )
        assert resp.status_code == 422

    def test_empty_body_returns_422(self, client: TestClient) -> None:
        resp = client.post("/api/interview", json={})
        assert resp.status_code == 422

    def test_invalid_candidate_object_returns_422(
        self,
        client: TestClient,
    ) -> None:
        """Candidate with missing required fields should fail."""
        resp = client.post(
            "/api/interview",
            json={
                "sessionId": "sess-1",
                "candidate": {"id": "CAND-001"},  # missing many required fields
            },
        )
        assert resp.status_code == 422

    def test_invalid_json_returns_422(self, client: TestClient) -> None:
        resp = client.post(
            "/api/interview",
            content="not json",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 422

    def test_get_method_not_allowed(self, client: TestClient) -> None:
        resp = client.get("/api/interview")
        assert resp.status_code == 405


# ===========================================================================
# Unknown sessionId handling
# ===========================================================================


class TestUnknownSessionId:
    """Tests for follow-up requests with unknown session IDs."""

    def test_continue_with_unknown_session_id_returns_404(
        self,
        client: TestClient,
    ) -> None:
        resp = client.post(
            "/api/interview",
            json={"sessionId": "nonexistent", "message": "Hello"},
        )
        assert resp.status_code == 404

    def test_404_response_has_detail(
        self,
        client: TestClient,
    ) -> None:
        resp = client.post(
            "/api/interview",
            json={"sessionId": "nonexistent", "message": "Hello"},
        )
        data = resp.json()
        assert "detail" in data
        assert "nonexistent" in data["detail"]

    def test_continue_after_session_removed_returns_404(
        self,
        client: TestClient,
        manager: SessionManager,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        manager.remove_session("sess-1")
        resp = client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "Hello"},
        )
        assert resp.status_code == 404


# ===========================================================================
# Exact response structure
# ===========================================================================


class TestResponseStructure:
    """Tests verifying the exact response format from the technical specification."""

    def test_start_response_keys(
        self,
        client: TestClient,
        sample_candidate_dict: dict,
    ) -> None:
        resp = client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        data = resp.json()
        # Must have exactly reply, done, feedback keys
        assert set(data.keys()) == {"reply", "done", "feedback"}

    def test_continue_response_keys(
        self,
        client: TestClient,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        resp = client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "Answer"},
        )
        data = resp.json()
        assert set(data.keys()) == {"reply", "done", "feedback"}

    def test_reply_is_string(
        self,
        client: TestClient,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        resp = client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "Answer"},
        )
        data = resp.json()
        assert isinstance(data["reply"], str)

    def test_done_is_bool(
        self,
        client: TestClient,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        resp = client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "message": "Answer"},
        )
        data = resp.json()
        assert isinstance(data["done"], bool)


# ===========================================================================
# Session isolation via API
# ===========================================================================


class TestSessionIsolationViaAPI:
    """Tests that separate sessions don't interfere with each other."""

    def test_separate_sessions_independent(
        self,
        client: TestClient,
        manager: SessionManager,
        sample_candidate_dict: dict,
    ) -> None:
        # Start two sessions
        client.post(
            "/api/interview",
            json={"sessionId": "sess-a", "candidate": sample_candidate_dict},
        )
        cand2 = get_candidate_by_id("CAND-002", path=CANDIDATES_PATH)
        client.post(
            "/api/interview",
            json={"sessionId": "sess-b", "candidate": cand2.model_dump()},
        )

        # Send messages to sess-a only
        client.post(
            "/api/interview",
            json={"sessionId": "sess-a", "message": "Answer for A"},
        )

        # Verify isolation
        sess_a = manager.get_session("sess-a")
        sess_b = manager.get_session("sess-b")

        assert len(sess_a.history) > 1  # welcome + messages
        assert len(sess_b.history) == 1  # only welcome
        assert sess_a.candidate.member.id != sess_b.candidate.member.id

    def test_unknown_session_does_not_affect_existing(
        self,
        client: TestClient,
        manager: SessionManager,
        sample_candidate_dict: dict,
    ) -> None:
        client.post(
            "/api/interview",
            json={"sessionId": "sess-1", "candidate": sample_candidate_dict},
        )
        # Try to continue a non-existent session
        resp = client.post(
            "/api/interview",
            json={"sessionId": "bad-session", "message": "Hello"},
        )
        assert resp.status_code == 404
        # Original session still intact
        session = manager.get_session("sess-1")
        assert session.candidate.member.id == "CAND-001"
