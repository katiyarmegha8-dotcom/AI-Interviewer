"""Interview API route — POST /api/interview."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.exceptions import SessionNotFoundError
from app.models.interview import InterviewRequest, InterviewResponse
from app.services.interview_service import continue_interview, start_interview
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
    """Handle interview start and continuation requests.

    - If ``candidate`` is present → start a new session.
    - If ``message`` is present → continue an existing session.

    The distinction is enforced by ``InterviewRequest`` validation.
    """
    if request.candidate is not None:
        return start_interview(
            session_id=request.sessionId,
            candidate=request.candidate,
            manager=manager,
        )

    # message is guaranteed present by the model validator
    return await continue_interview(
        session_id=request.sessionId,
        message=request.message,  # type: ignore[arg-type]
        manager=manager,
        llm=llm,
    )
