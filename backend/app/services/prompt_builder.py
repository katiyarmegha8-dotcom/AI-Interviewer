"""Interview prompt builder.

Constructs the LLM messages for an interview turn, including a system
prompt with interview rules and structured context (candidate profile,
curriculum coverage, previously asked questions, conversation history,
and interview objectives).

Prompt construction is kept **separate** from the LLM provider — this
module produces a ``list[dict[str, str]]`` that can be passed directly
to any ``LLMService.generate`` implementation.
"""

from __future__ import annotations

from app.models.candidate import Candidate
from app.models.curriculum import Curriculum
from app.models.session import InterviewSession

# ---------------------------------------------------------------------------
# Interview rules (static, not candidate-specific)
# ---------------------------------------------------------------------------

_SYSTEM_RULES = """\
You are an AI technical interviewer conducting a structured interview.

Interview rules:
1. Ask ONE question at a time. Never ask multiple questions in a single turn.
2. Cover at least four different curriculum days during the interview.
3. Ask at least eight questions before concluding.
4. Generate intelligent follow-up questions based on the candidate's answers.
5. Never repeat a question that has already been asked.
6. Adapt the difficulty and focus of questions based on the candidate's demonstrated knowledge.
7. Stay focused on the interview objectives and the curriculum topics.
8. Maintain conversational context — refer to previous answers when relevant.
9. When the candidate gives a strong answer on a topic, probe deeper or move to a related advanced topic.
10. When the candidate struggles, ask a simpler question on the same topic to gauge baseline understanding.
11. After covering at least four curriculum days and asking at least eight questions, you may conclude the interview by providing feedback."""

# ---------------------------------------------------------------------------
# Context section builders
# ---------------------------------------------------------------------------


def _build_candidate_profile(candidate: Candidate) -> str:
    """Build a text block describing the candidate."""
    m = candidate.member
    lines = [
        f"Name: {m.name}",
        f"Role: {m.jobRole}",
        f"Experience: {m.yearsExperience} years",
        f"Education: {m.education}",
    ]

    # Summarize mission performance
    passed = [mi for mi in candidate.missions if mi.passed is True]
    failed = [mi for mi in candidate.missions if mi.passed is False]
    skipped = [mi for mi in candidate.missions if mi.skipped is True]

    if passed:
        titles = ", ".join(mi.title for mi in passed)
        lines.append(f"Missions passed: {titles}")
    if failed:
        titles = ", ".join(mi.title for mi in failed)
        lines.append(f"Missions failed: {titles}")
    if skipped:
        titles = ", ".join(mi.title for mi in skipped)
        lines.append(f"Missions skipped: {titles}")

    lines.append(
        f"Engagement signals: {candidate.signals.commitDays} commit days, "
        f"{candidate.signals.missionsCompleted} missions completed, "
        f"{candidate.signals.missionsFirstTry} first-try passes"
    )

    return "\n".join(lines)


def _build_curriculum_context(
    curriculum: Curriculum,
    days_covered: list[int],
) -> str:
    """Build a text block describing the curriculum and what's been covered."""
    lines: list[str] = []

    # Modules
    lines.append("Curriculum modules:")
    for module in curriculum.modules:
        lines.append(f"  Module {module.n}: {module.title} (days {module.days[0]}–{module.days[1]})")

    # Covered days detail
    if days_covered:
        lines.append("\nCurriculum days already covered in this interview:")
        covered_days = {d.day: d for d in curriculum.days if d.day in days_covered}
        for day_num in sorted(days_covered):
            cd = covered_days.get(day_num)
            if cd:
                lines.append(f"  Day {cd.day}: {cd.title} — objectives: {'; '.join(cd.objectives)}")
            else:
                lines.append(f"  Day {day_num}")
    else:
        lines.append("\nNo curriculum days have been covered yet.")

    # Remaining days
    remaining = [d for d in curriculum.days if d.day not in days_covered]
    if remaining:
        lines.append("\nRemaining curriculum days available:")
        for cd in remaining:
            lines.append(f"  Day {cd.day}: {cd.title}")

    return "\n".join(lines)


def _build_previously_asked_questions(session: InterviewSession) -> str:
    """Build a text block listing questions already asked."""
    if not session.questionsAsked:
        return "No questions have been asked yet."

    lines = ["Questions already asked (do NOT repeat these):"]
    for i, q in enumerate(session.questionsAsked, 1):
        lines.append(f"  {i}. [Day {q.day}] {q.question}")

    return "\n".join(lines)


def _build_interview_objectives(session: InterviewSession) -> str:
    """Build a text block stating interview objectives and progress."""
    progress = session.progress
    lines = [
        "Interview objectives:",
        f"  - Cover at least 4 curriculum days (currently covered: {len(session.curriculumDaysCovered)})",
        f"  - Ask at least 8 questions (currently asked: {progress.questionsAsked})",
        f"  - Current curriculum day: {progress.currentDay} of {progress.totalDays}",
        f"  - Questions answered by candidate: {progress.questionsAnswered}",
    ]

    covered = len(session.curriculumDaysCovered)
    asked = progress.questionsAsked

    if covered >= 4 and asked >= 8:
        lines.append(
            "\nMinimum thresholds met — you may ask more probing questions "
            "or conclude the interview with feedback."
        )
    else:
        missing = []
        if covered < 4:
            missing.append(f"cover {4 - covered} more curriculum day(s)")
        if asked < 8:
            missing.append(f"ask {8 - asked} more question(s)")
        lines.append(f"\nStill need to: {' and '.join(missing)}.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main prompt builder
# ---------------------------------------------------------------------------


def build_interview_messages(
    session: InterviewSession,
    curriculum: Curriculum,
) -> list[dict[str, str]]:
    """Build the complete list of LLM messages for an interview turn.

    Produces:
      1. A **system** message containing interview rules and all
         structured context (candidate profile, curriculum, questions
         asked, objectives).
      2. The **conversation history** from the session, mapped to
         OpenAI-compatible roles (``interviewer`` → ``assistant``,
         ``candidate`` → ``user``).

    Args:
        session: The current interview session with history and state.
        curriculum: The full curriculum data.

    Returns:
        A list of ``{"role": ..., "content": ...}`` dicts ready for
        ``LLMService.generate``.
    """
    # --- System prompt ---
    candidate_block = _build_candidate_profile(session.candidate)
    curriculum_block = _build_curriculum_context(curriculum, session.curriculumDaysCovered)
    questions_block = _build_previously_asked_questions(session)
    objectives_block = _build_interview_objectives(session)

    system_content = "\n\n".join([
        _SYSTEM_RULES,
        f"## Candidate Profile\n{candidate_block}",
        f"## Curriculum\n{curriculum_block}",
        f"## Previously Asked Questions\n{questions_block}",
        f"## Interview Objectives\n{objectives_block}",
    ])

    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_content},
    ]

    # --- Conversation history ---
    # Map session roles to LLM chat roles
    role_map = {
        "interviewer": "assistant",
        "candidate": "user",
    }

    for msg in session.history:
        llm_role = role_map.get(msg.role, msg.role)
        messages.append({"role": llm_role, "content": msg.content})

    return messages
