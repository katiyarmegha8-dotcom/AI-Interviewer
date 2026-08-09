"""Interview API route — POST /api/interview."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.exceptions import SessionNotFoundError
from app.models.interview import InterviewRequest, InterviewResponse
from app.services.interview_service import continue_interview, start_interview
from app.services.session_service import SessionManager

router = APIRouter(tags=["interview"])

# ---------------------------------------------------------------------------
# SessionManager singleton — shared across all requests.
# Override via FastAPI dependency overrides in tests.
# ---------------------------------------------------------------------------

_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Provide the shared SessionManager instance."""
    return _session_manager


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("/interview", response_model=InterviewResponse)
def interview_endpoint(
    request: InterviewRequest,
    manager: SessionManager = Depends(get_session_manager),
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
    return continue_interview(
        session_id=request.sessionId,
        message=request.message,  # type: ignore[arg-type]
        manager=manager,
    )
