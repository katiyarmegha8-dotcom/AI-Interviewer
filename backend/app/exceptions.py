"""Custom application exceptions."""


class DataFileNotFoundError(Exception):
    """Raised when a required data file is missing from disk."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"Data file not found: {path}")


class DataFileParseError(Exception):
    """Raised when a data file contains invalid JSON."""

    def __init__(self, path: str, detail: str) -> None:
        self.path = path
        self.detail = detail
        super().__init__(f"Invalid JSON in {path}: {detail}")


class DataValidationError(Exception):
    """Raised when file contents fail Pydantic validation."""

    def __init__(self, path: str, detail: str) -> None:
        self.path = path
        self.detail = detail
        super().__init__(f"Validation error in {path}: {detail}")


class CandidateNotFoundError(Exception):
    """Raised when a candidate ID does not match any record."""

    def __init__(self, candidate_id: str) -> None:
        self.candidate_id = candidate_id
        super().__init__(f"Candidate not found: {candidate_id}")


class SessionNotFoundError(Exception):
    """Raised when a session ID does not match any active session."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        super().__init__(f"Session not found: {session_id}")
