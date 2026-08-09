"""Feedback prompt builder.

Constructs the LLM messages for generating structured interview feedback.
Like the interview prompt builder, prompt construction is kept **separate**
from the LLM provider — this module produces a ``list[dict[str, str]]``
that can be passed directly to any ``LLMService.generate`` implementation.
"""

from __future__ import annotations

from app.models.curriculum import Curriculum
from app.models.session import InterviewSession
from app.services.prompt_builder import _build_candidate_profile

# ---------------------------------------------------------------------------
# System prompt for feedback generation
# ---------------------------------------------------------------------------

_FEEDBACK_SYSTEM_PROMPT = """\
You are an AI technical interviewer generating structured feedback after \
a completed interview.

You MUST respond with ONLY a valid JSON object (no markdown, no code fences) \
with exactly these fields:

{
  "overall_summary": "A concise summary of the candidate's interview performance",
  "technical_strengths": ["strength1", "strength2", ...],
  "knowledge_gaps": ["gap1", "gap2", ...],
  "communication_assessment": "Assessment of communication clarity and responsiveness",
  "recommended_next_topics": ["topic1", "topic2", ...]
}

Rules:
- overall_summary: 2-4 sentences evaluating overall performance.
- technical_strengths: specific topics where the candidate showed competence.
- knowledge_gaps: specific topics where the candidate struggled or lacked depth.
- communication_assessment: 1-3 sentences on clarity, articulation, and responsiveness.
- recommended_next_topics: specific curriculum topics or skills to study next.
- Each array must contain at least one item.
- Do NOT include any text outside the JSON object."""


# ---------------------------------------------------------------------------
# Context builders
# ---------------------------------------------------------------------------


def _build_interview_summary(session: InterviewSession) -> str:
    """Build a text block summarizing the interview session."""
    progress = session.progress
    lines = [
        f"Questions asked: {progress.questionsAsked}",
        f"Questions answered by candidate: {progress.questionsAnswered}",
        f"Curriculum days covered: {len(session.curriculumDaysCovered)} "
        f"({', '.join(str(d) for d in sorted(session.curriculumDaysCovered))})"
        if session.curriculumDaysCovered
        else "Curriculum days covered: 0",
        f"Current curriculum day: {progress.currentDay} of {progress.totalDays}",
    ]
    return "\n".join(lines)


def _build_conversation_history(session: InterviewSession) -> str:
    """Build a text block of the full conversation for feedback context."""
    if not session.history:
        return "No conversation history available."

    lines = ["Full interview conversation:"]
    for msg in session.history:
        label = "Interviewer" if msg.role == "interviewer" else "Candidate"
        lines.append(f"  {label}: {msg.content}")

    return "\n".join(lines)


def _build_curriculum_summary(curriculum: Curriculum) -> str:
    """Build a text block of the curriculum for topic recommendations."""
    lines = ["Available curriculum topics:"]
    for day in curriculum.days:
        lines.append(f"  Day {day.day}: {day.title} — {', '.join(day.objectives[:3])}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main prompt builder
# ---------------------------------------------------------------------------


def build_feedback_messages(
    session: InterviewSession,
    curriculum: Curriculum,
) -> list[dict[str, str]]:
    """Build the LLM messages for generating interview feedback.

    Produces:
      1. A **system** message with the JSON output format specification
         and feedback generation rules.
      2. A **user** message containing all interview context (candidate
         profile, interview summary, conversation history, curriculum
         topics) and the instruction to generate feedback.

    Args:
        session: The completed interview session with full history.
        curriculum: The full curriculum data for topic recommendations.

    Returns:
        A list of ``{"role": ..., "content": ...}`` dicts ready for
        ``LLMService.generate``.
    """
    candidate_block = _build_candidate_profile(session.candidate)
    summary_block = _build_interview_summary(session)
    history_block = _build_conversation_history(session)
    curriculum_block = _build_curriculum_summary(curriculum)

    user_content = "\n\n".join([
        "Generate structured feedback for this completed interview.\n",
        f"## Candidate\n{candidate_block}",
        f"## Interview Summary\n{summary_block}",
        f"## Conversation\n{history_block}",
        f"## Curriculum Topics\n{curriculum_block}",
    ])

    return [
        {"role": "system", "content": _FEEDBACK_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
