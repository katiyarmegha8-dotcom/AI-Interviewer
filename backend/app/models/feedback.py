"""Pydantic models for structured interview feedback.

The ``DetailedFeedback`` model captures the five conceptual sections
required by Milestone 9.  It is produced by the feedback generator
service and can be mapped to the API-level ``Feedback`` model for
the ``POST /api/interview`` response.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class DetailedFeedback(BaseModel):
    """Structured feedback with five conceptual sections.

    This is the internal representation produced by the feedback
    generator.  It can be converted to the API-level ``Feedback``
    model via ``to_api_feedback()``.
    """

    overall_summary: str = Field(
        description="Overall summary of the candidate's interview performance",
    )
    technical_strengths: list[str] = Field(
        description="Technical areas where the candidate demonstrated strength",
    )
    knowledge_gaps: list[str] = Field(
        description="Topics where the candidate showed gaps in knowledge",
    )
    communication_assessment: str = Field(
        description="Assessment of the candidate's communication skills",
    )
    recommended_next_topics: list[str] = Field(
        description="Recommended topics for the candidate to study next",
    )

    def to_api_feedback(self) -> "Feedback":
        """Convert to the API-level ``Feedback`` model.

        Maps the five sections into the three-array format required by
        the technical specification:

        - ``summary`` → ``overall_summary`` + ``communication_assessment``
        - ``strengths`` → ``technical_strengths``
        - ``gaps`` → ``knowledge_gaps``
        - ``next`` → ``recommended_next_topics``
        """
        from app.models.interview import Feedback

        combined_summary = (
            f"{self.overall_summary}\n\n"
            f"Communication: {self.communication_assessment}"
        )
        return Feedback(
            summary=combined_summary,
            strengths=self.technical_strengths,
            gaps=self.knowledge_gaps,
            next=self.recommended_next_topics,
        )
