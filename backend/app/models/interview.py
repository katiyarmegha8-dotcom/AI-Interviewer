"""Pydantic models for the POST /api/interview endpoint.

Models match the technical specification exactly.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.models.candidate import Candidate


class InterviewRequest(BaseModel):
    """Request body for POST /api/interview.

    Two mutually exclusive shapes:
      - Start interview:  sessionId + candidate (no message)
      - Conversation turn: sessionId + message   (no candidate)

    At least one of ``candidate`` or ``message`` must be provided.
    """

    sessionId: str = Field(description="Unique interview session identifier")
    candidate: Candidate | None = Field(
        default=None,
        description="Candidate profile (required to start a new session)",
    )
    message: str | None = Field(
        default=None,
        description="Candidate's latest response (required for a follow-up turn)",
    )

    @model_validator(mode="after")
    def check_start_or_continue(self) -> InterviewRequest:
        has_candidate = self.candidate is not None
        has_message = self.message is not None
        if not has_candidate and not has_message:
            raise ValueError(
                "Request must include either 'candidate' to start a session "
                "or 'message' to continue an existing session."
            )
        return self


class Feedback(BaseModel):
    """Interview feedback returned when done=true."""

    summary: str = Field(description="Overall interview summary")
    strengths: list[str] = Field(description="Candidate strengths observed")
    gaps: list[str] = Field(description="Areas where the candidate can improve")
    next: list[str] = Field(description="Recommended next steps")


class InterviewResponse(BaseModel):
    """Response body for POST /api/interview.

    Matches the technical specification format exactly.
    """

    reply: str = Field(description="Interviewer reply text")
    done: bool = Field(
        default=False,
        description="Whether the interview is complete",
    )
    feedback: Feedback | None = Field(
        default=None,
        description="Feedback summary (present only when done=true)",
    )
