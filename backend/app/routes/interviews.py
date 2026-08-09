"""Interview API route — POST /api/interview."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.exceptions import SessionNotFoundError
from app.models.interview import InterviewRequest, InterviewResponse
from app.services.curriculum_service import get_curriculum
from app.services.interview_service import continue_interview, end_interview, start_interview
from app.services.llm_service import LLMService, StubLLMService
from app.services.session_service import SessionManager

router = APIRouter(tags=["interview"])

# ---------------------------------------------------------------------------
# Singletons — shared across all requests.
# Override via FastAPI dependency overrides in tests.
# ---------------------------------------------------------------------------

_session_manager = SessionManager()

# StubLLMService is used by default so the app starts without an API key.
# When OPENAI_API_KEY is configured, callers should override this
# dependency with an OpenAIService instance.
_llm_service: LLMService = StubLLMService()


def get_session_manager() -> SessionManager:
    """Provide the shared SessionManager instance."""
    return _session_manager


def get_llm_service() -> LLMService:
    """Provide the LLM service instance."""
    return _llm_service


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("/interview", response_model=InterviewResponse)
async def interview_endpoint(
    request: InterviewRequest,
    manager: SessionManager = Depends(get_session_manager),
    llm: LLMService = Depends(get_llm_service),
) -> InterviewResponse:
    """Handle interview start, continuation, and end requests.

    - If ``candidate`` is present → start a new session.
    - If ``done`` is true → end the session and generate feedback.
    - If ``message`` is present → continue an existing session.

    The distinction is enforced by ``InterviewRequest`` validation.
    """
    curriculum = get_curriculum()

    if request.candidate is not None:
        return start_interview(
            session_id=request.sessionId,
            candidate=request.candidate,
            manager=manager,
        )

    if request.done is True:
        return await end_interview(
            session_id=request.sessionId,
            manager=manager,
            curriculum=curriculum,
            llm=llm,
        )

    # message is guaranteed present by the model validator
    return await continue_interview(
        session_id=request.sessionId,
        message=request.message,  # type: ignore[arg-type]
        manager=manager,
        curriculum=curriculum,
        llm=llm,
    )
