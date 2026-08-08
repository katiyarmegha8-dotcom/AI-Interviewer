"""Pydantic models for interview session state."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field

from app.models.candidate import Candidate


class InterviewStatus(str, Enum):
    """Lifecycle status of an interview session."""

    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class ConversationMessage(BaseModel):
    """A single message in the interview conversation history."""

    role: str = Field(description="Message origin: 'interviewer' or 'candidate'")
    content: str = Field(description="Message text")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of the message",
    )


class QuestionAsked(BaseModel):
    """Record of a question posed during the interview."""

    day: int = Field(description="Curriculum day number the question relates to")
    question: str = Field(description="The question text")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the question was asked",
    )


class InterviewProgress(BaseModel):
    """Tracks how far the interview has progressed."""

    currentDay: int = Field(default=1, description="Current curriculum day in the interview")
    totalDays: int = Field(default=31, description="Total curriculum days to cover")
    questionsAsked: int = Field(default=0, description="Number of questions asked so far")
    questionsAnswered: int = Field(default=0, description="Number of candidate answers provided")


class InterviewSession(BaseModel):
    """Complete state for a single interview session.

    Each session is isolated — it carries its own conversation history,
    question log, curriculum coverage, and candidate profile.
    """

    sessionId: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique session identifier",
    )
    candidate: Candidate = Field(description="Candidate being interviewed")
    status: InterviewStatus = Field(
        default=InterviewStatus.ACTIVE,
        description="Current session status",
    )
    history: list[ConversationMessage] = Field(
        default_factory=list,
        description="Full conversation history",
    )
    questionsAsked: list[QuestionAsked] = Field(
        default_factory=list,
        description="Questions posed during the interview",
    )
    curriculumDaysCovered: list[int] = Field(
        default_factory=list,
        description="Curriculum day numbers that have been covered",
    )
    progress: InterviewProgress = Field(
        default_factory=InterviewProgress,
        description="Interview progress tracker",
    )
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the session was created",
    )
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of the last update",
    )
