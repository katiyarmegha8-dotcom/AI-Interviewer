"""Pydantic models for candidate data."""

from pydantic import BaseModel, Field


class CandidateMember(BaseModel):
    """Core identity fields for a candidate."""

    id: str = Field(description="Unique candidate identifier, e.g. CAND-001")
    name: str = Field(description="Candidate full name")
    jobRole: str = Field(description="Current job role")
    yearsExperience: int = Field(description="Years of professional experience")
    education: str = Field(description="Highest education or credential")
    status: str = Field(description="Completion status, e.g. COMPLETED")


class Mission(BaseModel):
    """A single mission (day task) within a candidate's record.

    Missions are either attempted (passed + attempts present)
    or skipped (skipped=True, no passed/attempts).
    """

    day: int = Field(description="Curriculum day number")
    title: str = Field(description="Mission title")
    passed: bool | None = Field(default=None, description="Whether the mission was passed")
    attempts: int | None = Field(default=None, description="Number of attempts")
    skipped: bool | None = Field(default=None, description="Whether the mission was skipped")


class Signals(BaseModel):
    """Aggregate engagement signals for a candidate."""

    commitDays: int = Field(description="Number of days with commits")
    missionsCompleted: int = Field(description="Total missions completed")
    missionsFirstTry: int = Field(description="Missions passed on the first attempt")


class Candidate(BaseModel):
    """A single candidate with member info, missions, and signals."""

    member: CandidateMember = Field(description="Candidate identity")
    missions: list[Mission] = Field(description="List of mission records")
    signals: Signals = Field(description="Aggregate engagement signals")


class CandidateData(BaseModel):
    """Top-level candidates structure matching candidates.json."""

    candidates: list[Candidate] = Field(description="List of all candidates")
