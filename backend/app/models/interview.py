"""Pydantic models for the POST /api/interview endpoint.

Models match the technical specification exactly.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.models.candidate import Candidate


class InterviewRequest(BaseModel):
    """Request body for POST /api/interview.

    Three shapes:
      - Start interview:  sessionId + candidate (no message, no done)
      - Conversation turn: sessionId + message   (no candidate, no done)
      - End interview:     sessionId + done=true (no candidate, no message)

    At least one of ``candidate``, ``message``, or ``done`` must be provided.
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
    done: bool | None = Field(
        default=None,
        description="Set to true to end the interview and generate feedback",
    )

    @model_validator(mode="after")
    def check_start_or_continue(self) -> InterviewRequest:
        has_candidate = self.candidate is not None
        has_message = self.message is not None
        # Only done=True is a valid end-interview request on its own.
        # done=False without message/candidate is ambiguous and rejected.
        is_end = self.done is True
        if not has_candidate and not has_message and not is_end:
            raise ValueError(
                "Request must include either 'candidate' to start a session, "
                "'message' to continue an existing session, or 'done'=true to end it."
            )
        return self


class Feedback(BaseModel):
    """Interview feedback returned when done=true."""

    summary: str = Field(description="Overall interview summary")
    strengths: list[str] = Field(description="Candidate strengths observed")
    gaps: list[str] = Field(description="Areas where the candidate can improve")
    next: list[str] = Field(description="Recommended next steps")


class InterviewProgressResponse(BaseModel):
    """Interview progress information returned in every response."""

    questionsAsked: int = Field(
        default=0,
        description="Number of primary questions asked so far",
    )
    questionsAnswered: int = Field(
        default=0,
        description="Number of candidate answers provided",
    )
    curriculumDaysCovered: int = Field(
        default=0,
        description="Number of distinct curriculum days covered",
    )
    currentDay: int = Field(
        default=1,
        description="Current curriculum day in the interview",
    )
    totalDays: int = Field(
        default=31,
        description="Total curriculum days available",
    )


class InterviewResponse(BaseModel):
    """Response body for POST /api/interview.

    Matches the technical specification format exactly, with an additional
    ``progress`` field for interview state tracking.
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
    progress: InterviewProgressResponse = Field(
        default_factory=InterviewProgressResponse,
        description="Interview progress tracking",
    )
