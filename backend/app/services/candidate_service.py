"""Candidate data retrieval service."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from app.exceptions import CandidateNotFoundError
from app.models.candidate import Candidate, CandidateData
from app.services.data_loader import DATA_DIR, load_and_validate

_CANDIDATES_PATH = DATA_DIR / "candidates.json"


@lru_cache(maxsize=1)
def _load_candidates(path: Path = _CANDIDATES_PATH) -> CandidateData:
    """Load and validate the full candidates data file.

    Results are cached after the first successful call.

    Args:
        path: Path to candidates.json (overridable for testing).

    Returns:
        Validated CandidateData instance.

    Raises:
        DataFileNotFoundError: If the file is missing.
        DataFileParseError: If the file contains invalid JSON.
        DataValidationError: If the data fails schema validation.
    """
    return load_and_validate(path, CandidateData)


def get_candidates(path: Path = _CANDIDATES_PATH) -> list[Candidate]:
    """Return all candidates.

    Args:
        path: Path to candidates.json (overridable for testing).

    Returns:
        List of Candidate instances.
    """
    data = _load_candidates(path)
    return data.candidates


def get_candidate_by_id(
    candidate_id: str,
    path: Path = _CANDIDATES_PATH,
) -> Candidate:
    """Look up a single candidate by their ID.

    Args:
        candidate_id: The candidate identifier (e.g. "CAND-001").
        path: Path to candidates.json (overridable for testing).

    Returns:
        Matching Candidate instance.

    Raises:
        CandidateNotFoundError: If no candidate matches the given ID.
    """
    for candidate in get_candidates(path):
        if candidate.member.id == candidate_id:
            return candidate
    raise CandidateNotFoundError(candidate_id)
