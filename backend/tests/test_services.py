"""Tests for curriculum and candidate data services.

Covers:
- Successful curriculum loading
- Successful candidate data loading
- Candidate lookup by ID
- Rejection of invalid data (bad JSON, schema mismatches)
- Handling of missing data files
- Handling of unknown candidate IDs
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.exceptions import (
    CandidateNotFoundError,
    DataFileNotFoundError,
    DataFileParseError,
    DataValidationError,
)
from app.models.candidate import Candidate, CandidateData
from app.models.curriculum import Curriculum
from app.services.candidate_service import get_candidate_by_id, get_candidates
from app.services.curriculum_service import get_curriculum
from app.services.data_loader import load_and_validate

# ---------------------------------------------------------------------------
# Paths to the real data files
# ---------------------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data"
CURRICULUM_PATH = DATA_DIR / "curriculum.json"
CANDIDATES_PATH = DATA_DIR / "candidates.json"


# ===========================================================================
# Curriculum service tests
# ===========================================================================

class TestCurriculumLoading:
    """Tests for loading the curriculum from the real JSON file."""

    def test_curriculum_loads_successfully(self) -> None:
        curriculum = get_curriculum(path=CURRICULUM_PATH)
        assert isinstance(curriculum, Curriculum)

    def test_curriculum_has_modules(self) -> None:
        curriculum = get_curriculum(path=CURRICULUM_PATH)
        assert len(curriculum.modules) == 8

    def test_curriculum_has_days(self) -> None:
        curriculum = get_curriculum(path=CURRICULUM_PATH)
        assert len(curriculum.days) == 31

    def test_curriculum_cohort_field(self) -> None:
        curriculum = get_curriculum(path=CURRICULUM_PATH)
        assert "AI Cohort" in curriculum.cohort

    def test_curriculum_modules_have_expected_structure(self) -> None:
        curriculum = get_curriculum(path=CURRICULUM_PATH)
        for module in curriculum.modules:
            assert module.n >= 1
            assert module.title
            assert len(module.days) == 2

    def test_curriculum_days_have_expected_structure(self) -> None:
        curriculum = get_curriculum(path=CURRICULUM_PATH)
        for day in curriculum.days:
            assert day.day >= 1
            assert day.title
            assert day.type
            assert isinstance(day.tools, list)
            assert isinstance(day.objectives, list)


# ===========================================================================
# Candidate service tests
# ===========================================================================

class TestCandidateLoading:
    """Tests for loading candidate data from the real JSON file."""

    def test_candidates_load_successfully(self) -> None:
        candidates = get_candidates(path=CANDIDATES_PATH)
        assert isinstance(candidates, list)
        assert len(candidates) > 0

    def test_all_candidates_are_candidate_type(self) -> None:
        candidates = get_candidates(path=CANDIDATES_PATH)
        for candidate in candidates:
            assert isinstance(candidate, Candidate)

    def test_candidate_count(self) -> None:
        candidates = get_candidates(path=CANDIDATES_PATH)
        assert len(candidates) == 20


class TestCandidateLookupById:
    """Tests for looking up individual candidates by ID."""

    def test_lookup_existing_candidate(self) -> None:
        candidate = get_candidate_by_id("CAND-001", path=CANDIDATES_PATH)
        assert candidate.member.id == "CAND-001"
        assert candidate.member.name == "Sarah Johnson"

    def test_lookup_last_candidate(self) -> None:
        candidate = get_candidate_by_id("CAND-020", path=CANDIDATES_PATH)
        assert candidate.member.id == "CAND-020"
        assert candidate.member.name == "Priyanka Sharma"

    def test_lookup_unknown_candidate_raises(self) -> None:
        with pytest.raises(CandidateNotFoundError) as exc_info:
            get_candidate_by_id("CAND-999", path=CANDIDATES_PATH)
        assert exc_info.value.candidate_id == "CAND-999"

    def test_lookup_empty_id_raises(self) -> None:
        with pytest.raises(CandidateNotFoundError):
            get_candidate_by_id("", path=CANDIDATES_PATH)

    def test_candidate_has_missions(self) -> None:
        candidate = get_candidate_by_id("CAND-001", path=CANDIDATES_PATH)
        assert len(candidate.missions) > 0

    def test_candidate_has_signals(self) -> None:
        candidate = get_candidate_by_id("CAND-001", path=CANDIDATES_PATH)
        assert candidate.signals.commitDays > 0
        assert candidate.signals.missionsCompleted > 0

    def test_mission_skipped_has_no_passed_or_attempts(self) -> None:
        """CAND-001 day 29 is skipped — should have skipped=True, no passed/attempts."""
        candidate = get_candidate_by_id("CAND-001", path=CANDIDATES_PATH)
        skipped_missions = [m for m in candidate.missions if m.skipped is True]
        assert len(skipped_missions) > 0
        for mission in skipped_missions:
            assert mission.passed is None
            assert mission.attempts is None

    def test_mission_attempted_has_passed_and_attempts(self) -> None:
        """CAND-001 day 7 was attempted — should have passed=True and attempts>=1."""
        candidate = get_candidate_by_id("CAND-001", path=CANDIDATES_PATH)
        attempted = [m for m in candidate.missions if m.passed is not None]
        assert len(attempted) > 0
        for mission in attempted:
            assert mission.attempts is not None
            assert mission.attempts >= 1

    def test_failed_mission_has_passed_false(self) -> None:
        """CAND-010 day 8 was failed — passed should be False."""
        candidate = get_candidate_by_id("CAND-010", path=CANDIDATES_PATH)
        day8 = next(m for m in candidate.missions if m.day == 8)
        assert day8.passed is False


# ===========================================================================
# Error handling tests (missing files, invalid JSON, validation errors)
# ===========================================================================

class TestMissingFileHandling:
    """Tests for handling missing data files."""

    def test_missing_curriculum_file_raises(self, tmp_path: Path) -> None:
        missing = tmp_path / "nonexistent.json"
        with pytest.raises(DataFileNotFoundError) as exc_info:
            load_and_validate(missing, Curriculum)
        assert "nonexistent.json" in str(exc_info.value.path)

    def test_missing_candidates_file_raises(self, tmp_path: Path) -> None:
        missing = tmp_path / "no_candidates.json"
        with pytest.raises(DataFileNotFoundError):
            load_and_validate(missing, CandidateData)


class TestInvalidJsonHandling:
    """Tests for handling files with invalid JSON syntax."""

    def test_invalid_json_raises_parse_error(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{invalid json content", encoding="utf-8")
        with pytest.raises(DataFileParseError) as exc_info:
            load_and_validate(bad_file, Curriculum)
        assert "bad.json" in str(exc_info.value.path)

    def test_empty_file_raises_parse_error(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty.json"
        empty.write_text("", encoding="utf-8")
        with pytest.raises(DataFileParseError):
            load_and_validate(empty, Curriculum)


class TestValidationErrorHandling:
    """Tests for handling data that is valid JSON but fails Pydantic validation."""

    def test_curriculum_missing_required_field_raises(self, tmp_path: Path) -> None:
        """A JSON object missing the 'modules' key should fail validation."""
        bad_file = tmp_path / "bad_curriculum.json"
        bad_file.write_text(
            json.dumps({"cohort": "test", "days": []}),
            encoding="utf-8",
        )
        with pytest.raises(DataValidationError) as exc_info:
            load_and_validate(bad_file, Curriculum)
        assert "bad_curriculum.json" in str(exc_info.value.path)

    def test_candidates_wrong_type_raises(self, tmp_path: Path) -> None:
        """A candidates file where 'candidates' is a string, not a list."""
        bad_file = tmp_path / "bad_candidates.json"
        bad_file.write_text(
            json.dumps({"candidates": "not-a-list"}),
            encoding="utf-8",
        )
        with pytest.raises(DataValidationError):
            load_and_validate(bad_file, CandidateData)

    def test_candidate_missing_member_raises(self, tmp_path: Path) -> None:
        """A candidate object missing the 'member' key."""
        bad_file = tmp_path / "bad_candidate.json"
        bad_file.write_text(
            json.dumps({"candidates": [{"missions": [], "signals": {"commitDays": 0, "missionsCompleted": 0, "missionsFirstTry": 0}}]}),
            encoding="utf-8",
        )
        with pytest.raises(DataValidationError):
            load_and_validate(bad_file, CandidateData)

    def test_module_wrong_type_for_n_raises(self, tmp_path: Path) -> None:
        """A module where 'n' is a string instead of an int."""
        bad_file = tmp_path / "bad_module.json"
        bad_file.write_text(
            json.dumps({"cohort": "test", "modules": [{"n": "one", "title": "T", "days": [1, 2]}], "days": []}),
            encoding="utf-8",
        )
        with pytest.raises(DataValidationError):
            load_and_validate(bad_file, Curriculum)
