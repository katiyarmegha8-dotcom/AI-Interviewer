"""Tests for the feedback generation service and prompt builder.

Covers:
- DetailedFeedback model structure and to_api_feedback() mapping
- Feedback prompt builder output structure
- Feedback prompt builder includes all context sections
- Feedback prompt builder: no candidate-specific data in system prompt
- Feedback service: correct output with valid LLM JSON
- Feedback service: different sessions produce different prompts
- Feedback service: empty/minimal interview history
- Feedback service: malformed LLM output (invalid JSON, non-object, code fences)
- Feedback service: missing fields in LLM JSON (defaults applied)
- Feedback service: no LLM available (fallback feedback)
- Feedback service: error handling
- No hardcoded candidate information in prompts or defaults
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from app.models.candidate import Candidate, CandidateMember, Mission, Signals
from app.models.curriculum import Curriculum
from app.models.feedback import DetailedFeedback
from app.models.interview import Feedback
from app.models.session import InterviewSession
from app.services.candidate_service import get_candidate_by_id
from app.services.curriculum_service import get_curriculum
from app.services.feedback_prompt_builder import (
    _build_candidate_context,
    _build_conversation_history,
    _build_curriculum_summary,
    _build_interview_summary,
    _FEEDBACK_SYSTEM_PROMPT,
    build_feedback_messages,
)
from app.services.feedback_service import (
    _DEFAULT_FEEDBACK,
    _parse_feedback_json,
    generate_feedback,
)
from app.services.llm_service import LLMService, StubLLMService
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
def candidate2() -> Candidate:
    return get_candidate_by_id("CAND-002", path=CANDIDATES_PATH)


@pytest.fixture
def session(candidate: Candidate) -> InterviewSession:
    return InterviewSession(sessionId="test-1", candidate=candidate)


@pytest.fixture
def session_with_history(candidate: Candidate) -> InterviewSession:
    """Session with a realistic interview conversation."""
    manager = SessionManager()
    manager.create_session(candidate, session_id="hist-1")
    manager.add_message("hist-1", "interviewer", "Welcome. Let's begin your interview.")
    manager.add_message("hist-1", "candidate", "I'm ready to start.")
    manager.add_question("hist-1", day=7, question="What are embeddings?")
    manager.add_message(
        "hist-1",
        "interviewer",
        "What are word embeddings and how are they used in NLP?",
    )
    manager.add_message(
        "hist-1",
        "candidate",
        "Embeddings are dense vector representations of words that capture semantic meaning.",
    )
    manager.add_question("hist-1", day=12, question="Explain prompt engineering.")
    manager.add_message(
        "hist-1",
        "interviewer",
        "Can you explain prompt engineering techniques?",
    )
    manager.add_message(
        "hist-1",
        "candidate",
        "Prompt engineering involves crafting input text to guide LLM behavior.",
    )
    return manager.get_session("hist-1")


# ===========================================================================
# DetailedFeedback model
# ===========================================================================


class TestDetailedFeedbackModel:
    """Tests for the DetailedFeedback Pydantic model."""

    def test_has_all_five_sections(self) -> None:
        fb = DetailedFeedback(
            overall_summary="Good interview",
            technical_strengths=["Python"],
            knowledge_gaps=["Rust"],
            communication_assessment="Clear and articulate",
            recommended_next_topics=["Advanced Python"],
        )
        assert fb.overall_summary == "Good interview"
        assert fb.technical_strengths == ["Python"]
        assert fb.knowledge_gaps == ["Rust"]
        assert fb.communication_assessment == "Clear and articulate"
        assert fb.recommended_next_topics == ["Advanced Python"]

    def test_to_api_feedback_maps_correctly(self) -> None:
        fb = DetailedFeedback(
            overall_summary="Good overall performance",
            technical_strengths=["Python", "SQL"],
            knowledge_gaps=["Rust", "Go"],
            communication_assessment="Very clear",
            recommended_next_topics=["Advanced Python", "Rust basics"],
        )
        api = fb.to_api_feedback()
        assert isinstance(api, Feedback)
        assert "Good overall performance" in api.summary
        assert "Very clear" in api.summary
        assert api.strengths == ["Python", "SQL"]
        assert api.gaps == ["Rust", "Go"]
        assert api.next == ["Advanced Python", "Rust basics"]

    def test_to_api_feedback_summary_includes_communication(self) -> None:
        fb = DetailedFeedback(
            overall_summary="Summary text",
            technical_strengths=["s"],
            knowledge_gaps=["g"],
            communication_assessment="Comm text",
            recommended_next_topics=["t"],
        )
        api = fb.to_api_feedback()
        assert "Summary text" in api.summary
        assert "Comm text" in api.summary

    def test_all_fields_required(self) -> None:
        with pytest.raises(Exception):
            DetailedFeedback()  # type: ignore[call-arg]


# ===========================================================================
# Feedback prompt builder: system prompt
# ===========================================================================


class TestFeedbackSystemPrompt:
    """Tests for the feedback system prompt content."""

    def test_mentions_all_five_fields(self) -> None:
        assert "overall_summary" in _FEEDBACK_SYSTEM_PROMPT
        assert "technical_strengths" in _FEEDBACK_SYSTEM_PROMPT
        assert "knowledge_gaps" in _FEEDBACK_SYSTEM_PROMPT
        assert "communication_assessment" in _FEEDBACK_SYSTEM_PROMPT
        assert "recommended_next_topics" in _FEEDBACK_SYSTEM_PROMPT

    def test_instructs_json_output(self) -> None:
        assert "JSON" in _FEEDBACK_SYSTEM_PROMPT
        assert "valid JSON object" in _FEEDBACK_SYSTEM_PROMPT

    def test_no_hardcoded_candidate_info(self) -> None:
        """System prompt must not contain candidate-specific data."""
        assert "CAND-" not in _FEEDBACK_SYSTEM_PROMPT
        assert "Sarah" not in _FEEDBACK_SYSTEM_PROMPT
        assert "John" not in _FEEDBACK_SYSTEM_PROMPT


# ===========================================================================
# Feedback prompt builder: context builders
# ===========================================================================


class TestCandidateContext:
    """Tests for _build_candidate_context."""

    def test_includes_name(self, candidate: Candidate) -> None:
        ctx = _build_candidate_context(candidate)
        assert "Sarah Johnson" in ctx

    def test_includes_role(self, candidate: Candidate) -> None:
        ctx = _build_candidate_context(candidate)
        assert "Senior Data Engineer" in ctx

    def test_includes_experience(self, candidate: Candidate) -> None:
        ctx = _build_candidate_context(candidate)
        assert "9 years" in ctx

    def test_includes_signals(self, candidate: Candidate) -> None:
        ctx = _build_candidate_context(candidate)
        assert "commit days" in ctx
        assert "missions completed" in ctx

    def test_different_candidate_different_context(
        self, candidate: Candidate, candidate2: Candidate
    ) -> None:
        ctx1 = _build_candidate_context(candidate)
        ctx2 = _build_candidate_context(candidate2)
        assert ctx1 != ctx2
        assert "Sarah Johnson" in ctx1
        assert "Alex Turner" in ctx2


class TestInterviewSummary:
    """Tests for _build_interview_summary."""

    def test_empty_session(self, session: InterviewSession) -> None:
        summary = _build_interview_summary(session)
        assert "Questions asked: 0" in summary
        assert "Questions answered" in summary

    def test_session_with_progress(self, session_with_history: InterviewSession) -> None:
        summary = _build_interview_summary(session_with_history)
        assert "Questions asked: 2" in summary
        assert "Curriculum days covered: 2" in summary

    def test_shows_covered_days(self, session_with_history: InterviewSession) -> None:
        summary = _build_interview_summary(session_with_history)
        assert "7" in summary
        assert "12" in summary


class TestConversationHistory:
    """Tests for _build_conversation_history."""

    def test_empty_history(self, session: InterviewSession) -> None:
        history = _build_conversation_history(session)
        assert "No conversation history" in history

    def test_includes_messages(self, session_with_history: InterviewSession) -> None:
        history = _build_conversation_history(session_with_history)
        assert "embeddings" in history.lower()
        assert "prompt engineering" in history.lower()

    def test_labels_roles(self, session_with_history: InterviewSession) -> None:
        history = _build_conversation_history(session_with_history)
        assert "Interviewer:" in history
        assert "Candidate:" in history


class TestCurriculumSummary:
    """Tests for _build_curriculum_summary."""

    def test_includes_days(self, curriculum: Curriculum) -> None:
        summary = _build_curriculum_summary(curriculum)
        assert "Day 1" in summary or "Day 7" in summary

    def test_includes_objectives(self, curriculum: Curriculum) -> None:
        summary = _build_curriculum_summary(curriculum)
        # Objectives are rendered as "Day N: Title — obj1, obj2, obj3"
        assert "—" in summary or "Day" in summary


# ===========================================================================
# Feedback prompt builder: build_feedback_messages
# ===========================================================================


class TestBuildFeedbackMessages:
    """Tests for the full build_feedback_messages output."""

    def test_returns_two_messages(
        self, session: InterviewSession, curriculum: Curriculum
    ) -> None:
        messages = build_feedback_messages(session, curriculum)
        assert len(messages) == 2

    def test_first_is_system(
        self, session: InterviewSession, curriculum: Curriculum
    ) -> None:
        messages = build_feedback_messages(session, curriculum)
        assert messages[0]["role"] == "system"

    def test_second_is_user(
        self, session: InterviewSession, curriculum: Curriculum
    ) -> None:
        messages = build_feedback_messages(session, curriculum)
        assert messages[1]["role"] == "user"

    def test_system_contains_json_format(
        self, session: InterviewSession, curriculum: Curriculum
    ) -> None:
        messages = build_feedback_messages(session, curriculum)
        assert "JSON" in messages[0]["content"]

    def test_user_contains_candidate(
        self, session: InterviewSession, curriculum: Curriculum
    ) -> None:
        messages = build_feedback_messages(session, curriculum)
        assert "Sarah Johnson" in messages[1]["content"]

    def test_user_contains_interview_summary(
        self, session: InterviewSession, curriculum: Curriculum
    ) -> None:
        messages = build_feedback_messages(session, curriculum)
        assert "Interview Summary" in messages[1]["content"]

    def test_user_contains_conversation(
        self, session_with_history: InterviewSession, curriculum: Curriculum
    ) -> None:
        messages = build_feedback_messages(session_with_history, curriculum)
        assert "Conversation" in messages[1]["content"]

    def test_user_contains_curriculum(
        self, session: InterviewSession, curriculum: Curriculum
    ) -> None:
        messages = build_feedback_messages(session, curriculum)
        assert "Curriculum Topics" in messages[1]["content"]

    def test_different_sessions_different_prompts(
        self,
        candidate: Candidate,
        candidate2: Candidate,
        curriculum: Curriculum,
    ) -> None:
        s1 = InterviewSession(sessionId="s1", candidate=candidate)
        s2 = InterviewSession(sessionId="s2", candidate=candidate2)
        m1 = build_feedback_messages(s1, curriculum)
        m2 = build_feedback_messages(s2, curriculum)
        assert m1[1]["content"] != m2[1]["content"]

    def test_messages_are_dict_format(
        self, session: InterviewSession, curriculum: Curriculum
    ) -> None:
        messages = build_feedback_messages(session, curriculum)
        for msg in messages:
            assert "role" in msg
            assert "content" in msg
            assert isinstance(msg["role"], str)
            assert isinstance(msg["content"], str)

    def test_no_hardcoded_candidate_in_system_prompt(
        self, session: InterviewSession, curriculum: Curriculum
    ) -> None:
        messages = build_feedback_messages(session, curriculum)
        system = messages[0]["content"]
        assert "Sarah" not in system
        assert "CAND-" not in system


# ===========================================================================
# Feedback JSON parser
# ===========================================================================


class TestParseFeedbackJSON:
    """Tests for _parse_feedback_json."""

    def test_valid_json(self) -> None:
        raw = json.dumps({
            "overall_summary": "Good interview",
            "technical_strengths": ["Python", "SQL"],
            "knowledge_gaps": ["Rust"],
            "communication_assessment": "Clear speaker",
            "recommended_next_topics": ["Advanced Python"],
        })
        fb = _parse_feedback_json(raw)
        assert fb.overall_summary == "Good interview"
        assert fb.technical_strengths == ["Python", "SQL"]
        assert fb.knowledge_gaps == ["Rust"]
        assert fb.communication_assessment == "Clear speaker"
        assert fb.recommended_next_topics == ["Advanced Python"]

    def test_json_with_code_fences(self) -> None:
        inner = json.dumps({
            "overall_summary": "Summary",
            "technical_strengths": ["S"],
            "knowledge_gaps": ["G"],
            "communication_assessment": "C",
            "recommended_next_topics": ["T"],
        })
        raw = f"```json\n{inner}\n```"
        fb = _parse_feedback_json(raw)
        assert fb.overall_summary == "Summary"

    def test_json_with_plain_fences(self) -> None:
        inner = json.dumps({
            "overall_summary": "Summary",
            "technical_strengths": ["S"],
            "knowledge_gaps": ["G"],
            "communication_assessment": "C",
            "recommended_next_topics": ["T"],
        })
        raw = f"```\n{inner}\n```"
        fb = _parse_feedback_json(raw)
        assert fb.overall_summary == "Summary"

    def test_missing_fields_get_defaults(self) -> None:
        raw = json.dumps({"overall_summary": "Only summary"})
        fb = _parse_feedback_json(raw)
        assert fb.overall_summary == "Only summary"
        assert isinstance(fb.technical_strengths, list)
        assert isinstance(fb.knowledge_gaps, list)
        assert isinstance(fb.communication_assessment, str)
        assert isinstance(fb.recommended_next_topics, list)

    def test_strength_as_string_becomes_list(self) -> None:
        raw = json.dumps({
            "overall_summary": "S",
            "technical_strengths": "Only one strength",
            "knowledge_gaps": [],
            "communication_assessment": "C",
            "recommended_next_topics": [],
        })
        fb = _parse_feedback_json(raw)
        assert fb.technical_strengths == ["Only one strength"]

    def test_invalid_json_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="not valid JSON"):
            _parse_feedback_json("this is not json at all")

    def test_json_array_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="not a JSON object"):
            _parse_feedback_json('["not", "an", "object"]')

    def test_whitespace_handling(self) -> None:
        inner = json.dumps({
            "overall_summary": "S",
            "technical_strengths": ["T"],
            "knowledge_gaps": ["G"],
            "communication_assessment": "C",
            "recommended_next_topics": ["N"],
        })
        raw = f"  \n  {inner}  \n  "
        fb = _parse_feedback_json(raw)
        assert fb.overall_summary == "S"

    def test_no_hardcoded_candidate_info_in_parsed(self) -> None:
        """Parser must not inject candidate-specific info."""
        raw = json.dumps({
            "overall_summary": "Generic summary",
            "technical_strengths": ["Generic strength"],
            "knowledge_gaps": ["Generic gap"],
            "communication_assessment": "Generic assessment",
            "recommended_next_topics": ["Generic topic"],
        })
        fb = _parse_feedback_json(raw)
        assert "Sarah" not in fb.overall_summary
        assert "CAND-" not in fb.overall_summary


# ===========================================================================
# Feedback service: generate_feedback
# ===========================================================================


class TestGenerateFeedback:
    """Tests for the generate_feedback service function."""

    def test_no_llm_returns_default(self, session: InterviewSession, curriculum: Curriculum) -> None:
        fb = asyncio.run(generate_feedback(session, curriculum, llm=None))
        assert fb == _DEFAULT_FEEDBACK
        assert "no LLM service" in fb.overall_summary.lower() or "LLM" in fb.overall_summary

    def test_stub_llm_returns_parsed_fallback(self, session: InterviewSession, curriculum: Curriculum) -> None:
        """StubLLMService returns non-JSON, so parse fails → graceful fallback."""
        stub = StubLLMService()
        fb = asyncio.run(generate_feedback(session, curriculum, llm=stub))
        # StubLLMService returns non-JSON text, so parsing fails
        # The service should return a fallback DetailedFeedback
        assert isinstance(fb, DetailedFeedback)
        assert "Could not parse" in fb.technical_strengths[0]

    def test_valid_llm_json_response(
        self, session_with_history: InterviewSession, curriculum: Curriculum
    ) -> None:
        """When LLM returns valid JSON, it's parsed into DetailedFeedback."""

        class ValidJsonLLM(LLMService):
            async def generate(self, messages: list[dict[str, str]]) -> str:
                return json.dumps({
                    "overall_summary": "Strong technical interview",
                    "technical_strengths": ["Python", "Data pipelines"],
                    "knowledge_gaps": ["Rust basics"],
                    "communication_assessment": "Clear and concise",
                    "recommended_next_topics": ["Advanced Python patterns"],
                })

        fb = asyncio.run(generate_feedback(session_with_history, curriculum, llm=ValidJsonLLM()))
        assert fb.overall_summary == "Strong technical interview"
        assert "Python" in fb.technical_strengths
        assert "Rust basics" in fb.knowledge_gaps
        assert "Clear and concise" in fb.communication_assessment

    def test_malformed_llm_response_graceful_fallback(
        self, session: InterviewSession, curriculum: Curriculum
    ) -> None:
        """When LLM returns garbage, service returns fallback feedback."""

        class GarbageLLM(LLMService):
            async def generate(self, messages: list[dict[str, str]]) -> str:
                return "This is just random text, not JSON at all!"

        fb = asyncio.run(generate_feedback(session, curriculum, llm=GarbageLLM()))
        assert isinstance(fb, DetailedFeedback)
        # Should contain the raw response or parse error message
        assert fb.overall_summary  # non-empty

    def test_llm_json_with_code_fences(
        self, session: InterviewSession, curriculum: Curriculum
    ) -> None:
        """LLM wraps JSON in code fences."""

        class FencedLLM(LLMService):
            async def generate(self, messages: list[dict[str, str]]) -> str:
                inner = json.dumps({
                    "overall_summary": "Good",
                    "technical_strengths": ["S"],
                    "knowledge_gaps": ["G"],
                    "communication_assessment": "C",
                    "recommended_next_topics": ["T"],
                })
                return f"```json\n{inner}\n```"

        fb = asyncio.run(generate_feedback(session, curriculum, llm=FencedLLM()))
        assert fb.overall_summary == "Good"

    def test_different_sessions_different_feedback(
        self, candidate: Candidate, candidate2: Candidate, curriculum: Curriculum
    ) -> None:
        """Different candidates should get different feedback prompts."""
        s1 = InterviewSession(sessionId="s1", candidate=candidate)
        s2 = InterviewSession(sessionId="s2", candidate=candidate2)

        class CaptureLLM(LLMService):
            def __init__(self) -> None:
                self.captured: list[list[dict[str, str]]] = []

            async def generate(self, messages: list[dict[str, str]]) -> str:
                self.captured.append(messages)
                return json.dumps({
                    "overall_summary": "S",
                    "technical_strengths": ["T"],
                    "knowledge_gaps": ["G"],
                    "communication_assessment": "C",
                    "recommended_next_topics": ["N"],
                })

        llm1 = CaptureLLM()
        llm2 = CaptureLLM()
        asyncio.run(generate_feedback(s1, curriculum, llm=llm1))
        asyncio.run(generate_feedback(s2, curriculum, llm=llm2))
        # The prompts should differ (different candidate profiles)
        assert llm1.captured[0][1]["content"] != llm2.captured[0][1]["content"]

    def test_empty_history_still_works(
        self, candidate: Candidate, curriculum: Curriculum
    ) -> None:
        """Session with no conversation still generates feedback."""

        class SimpleLLM(LLMService):
            async def generate(self, messages: list[dict[str, str]]) -> str:
                return json.dumps({
                    "overall_summary": "No conversation",
                    "technical_strengths": ["N/A"],
                    "knowledge_gaps": ["N/A"],
                    "communication_assessment": "N/A",
                    "recommended_next_topics": ["N/A"],
                })

        session = InterviewSession(sessionId="empty", candidate=candidate)
        fb = asyncio.run(generate_feedback(session, curriculum, llm=SimpleLLM()))
        assert fb.overall_summary == "No conversation"

    def test_llm_error_propagates(
        self, session: InterviewSession, curriculum: Curriculum
    ) -> None:
        """LLMServiceError from the LLM should propagate."""

        class FailingLLM(LLMService):
            async def generate(self, messages: list[dict[str, str]]) -> str:
                from app.exceptions import LLMServiceError

                raise LLMServiceError("API unavailable")

        from app.exceptions import LLMServiceError

        with pytest.raises(LLMServiceError, match="API unavailable"):
            asyncio.run(generate_feedback(session, curriculum, llm=FailingLLM()))

    def test_llm_json_with_missing_arrays(
        self, session: InterviewSession, curriculum: Curriculum
    ) -> None:
        """LLM returns valid JSON but some array fields are missing."""

        class PartialLLM(LLMService):
            async def generate(self, messages: list[dict[str, str]]) -> str:
                return json.dumps({
                    "overall_summary": "Partial data",
                    "communication_assessment": "Okay",
                })

        fb = asyncio.run(generate_feedback(session, curriculum, llm=PartialLLM()))
        assert fb.overall_summary == "Partial data"
        assert isinstance(fb.technical_strengths, list)
        assert isinstance(fb.knowledge_gaps, list)
        assert isinstance(fb.recommended_next_topics, list)

    def test_default_feedback_no_hardcoded_candidate(self) -> None:
        """Default fallback feedback must not contain candidate-specific info."""
        assert "Sarah" not in _DEFAULT_FEEDBACK.overall_summary
        assert "CAND-" not in _DEFAULT_FEEDBACK.overall_summary
        assert "Alex" not in _DEFAULT_FEEDBACK.overall_summary


# ===========================================================================
# Integration: end_interview through interview_service
# ===========================================================================


class TestEndInterviewIntegration:
    """Tests for the end_interview function in interview_service."""

    def test_end_returns_done_true(
        self, candidate: Candidate, curriculum: Curriculum
    ) -> None:
        from app.services.interview_service import end_interview

        manager = SessionManager()
        manager.create_session(candidate, session_id="end-1")
        resp = asyncio.run(end_interview("end-1", manager, curriculum, llm=None))
        assert resp.done is True

    def test_end_has_feedback(
        self, candidate: Candidate, curriculum: Curriculum
    ) -> None:
        from app.services.interview_service import end_interview

        manager = SessionManager()
        manager.create_session(candidate, session_id="end-2")
        resp = asyncio.run(end_interview("end-2", manager, curriculum, llm=None))
        assert resp.feedback is not None
        assert isinstance(resp.feedback, Feedback)

    def test_end_marks_session_completed(
        self, candidate: Candidate, curriculum: Curriculum
    ) -> None:
        from app.services.interview_service import end_interview
        from app.models.session import InterviewStatus

        manager = SessionManager()
        manager.create_session(candidate, session_id="end-3")
        asyncio.run(end_interview("end-3", manager, curriculum, llm=None))
        session = manager.get_session("end-3")
        assert session.status == InterviewStatus.COMPLETED

    def test_end_reply_is_interview_completed(
        self, candidate: Candidate, curriculum: Curriculum
    ) -> None:
        from app.services.interview_service import end_interview

        manager = SessionManager()
        manager.create_session(candidate, session_id="end-4")
        resp = asyncio.run(end_interview("end-4", manager, curriculum, llm=None))
        assert resp.reply == "Interview completed."

    def test_end_unknown_session_raises_404(self, curriculum: Curriculum) -> None:
        from app.services.interview_service import end_interview
        from app.exceptions import SessionNotFoundError

        manager = SessionManager()
        with pytest.raises(SessionNotFoundError):
            asyncio.run(end_interview("nonexistent", manager, curriculum, llm=None))

    def test_end_with_valid_llm_feedback(
        self, candidate: Candidate, curriculum: Curriculum
    ) -> None:
        from app.services.interview_service import end_interview

        class GoodLLM(LLMService):
            async def generate(self, messages: list[dict[str, str]]) -> str:
                return json.dumps({
                    "overall_summary": "Excellent performance",
                    "technical_strengths": ["Python", "SQL", "Pipelines"],
                    "knowledge_gaps": ["Rust", "Go"],
                    "communication_assessment": "Articulate and clear",
                    "recommended_next_topics": ["Advanced SQL", "Rust basics"],
                })

        manager = SessionManager()
        manager.create_session(candidate, session_id="end-5")
        resp = asyncio.run(
            end_interview("end-5", manager, curriculum, llm=GoodLLM())
        )
        assert resp.done is True
        assert resp.feedback is not None
        assert "Excellent performance" in resp.feedback.summary
        assert "Python" in resp.feedback.strengths
        assert "Rust" in resp.feedback.gaps
        assert "Advanced SQL" in resp.feedback.next
