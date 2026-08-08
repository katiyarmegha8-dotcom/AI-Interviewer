"""Generic JSON data-file loading and Pydantic validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.exceptions import DataFileNotFoundError, DataFileParseError, DataValidationError

T = TypeVar("T", bound=BaseModel)

# Base data directory: backend/app/data/
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_and_validate(path: Path, model: type[T]) -> T:
    """Read a JSON file, parse it, and validate it against a Pydantic model.

    Args:
        path: Absolute or relative path to the JSON file.
        model: Pydantic model class to validate against.

    Returns:
        Validated instance of the Pydantic model.

    Raises:
        DataFileNotFoundError: If the file does not exist.
        DataFileParseError: If the file is not valid JSON.
        DataValidationError: If the data fails Pydantic validation.
    """
    if not path.exists():
        raise DataFileNotFoundError(str(path))

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DataFileParseError(str(path), str(exc)) from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DataFileParseError(str(path), str(exc)) from exc

    try:
        return model.model_validate(data)
    except ValidationError as exc:
        raise DataValidationError(str(path), exc.error_count()) from exc
