"""Curriculum data retrieval service."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from app.models.curriculum import Curriculum
from app.services.data_loader import DATA_DIR, load_and_validate

_CURRICULUM_PATH = DATA_DIR / "curriculum.json"


@lru_cache(maxsize=1)
def get_curriculum(path: Path = _CURRICULUM_PATH) -> Curriculum:
    """Load, validate, and return the curriculum data.

    Results are cached after the first successful call.

    Args:
        path: Path to curriculum.json (overridable for testing).

    Returns:
        Validated Curriculum instance.

    Raises:
        DataFileNotFoundError: If the file is missing.
        DataFileParseError: If the file contains invalid JSON.
        DataValidationError: If the data fails schema validation.
    """
    return load_and_validate(path, Curriculum)
