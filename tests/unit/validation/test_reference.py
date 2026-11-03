"""Unit tests for metabosim.validation.reference.

The curves here are SYNTHETIC test fixtures, not published data.
"""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from metabosim.domain.diet import MacronutrientGrams
from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.domain.simulation_state import SimulationState
from metabosim.simulation.config import DailyPlan, SimulationConfig
from metabosim.simulation.engine import Simulator
from metabosim.validation.reference import (
    ReferenceCurve,
    check_value,
    compare_curve,
    load_curve,
)


def _curve(**overrides: object) -> ReferenceCurve:
    fields: dict[str, object] = {
        "id": "synthetic",
        "description": "test fixture",
        "citation": "none",
        "extraction_note": "synthetic",
        "days": [0, 5, 10],
        "weight_kg": [80.0, 80.5, 81.0],
    }
    fields.update(overrides)
    return ReferenceCurve.model_validate(fields)


@pytest.fixture
def states() -> list[SimulationState]:
    person = Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)
    plan = DailyPlan(
        macros=MacronutrientGrams(protein_g=150, carbohydrate_g=300, fat_g=70)
    )
    return Simulator(person, SimulationConfig(days=10), plan).run()


@pytest.mark.unit
class TestReferenceCurve:
    def test_valid(self) -> None:
        assert _curve().days == [0, 5, 10]

    def test_length_mismatch(self) -> None:
        with pytest.raises(ValidationError, match="same length"):
            _curve(weight_kg=[80.0])

    def test_negative_day(self) -> None:
        with pytest.raises(ValidationError, match="non-negative"):
            _curve(days=[-1, 5, 10])

    def test_days_must_increase(self) -> None:
        with pytest.raises(ValidationError, match="strictly increasing"):
            _curve(days=[0, 5, 5])

    def test_citation_required(self) -> None:
        with pytest.raises(ValidationError):
            _curve(citation="")

    def test_extraction_note_required(self) -> None:
        with pytest.raises(ValidationError):
            _curve(extraction_note="")


@pytest.mark.unit
class TestLoadCurve:
    def test_round_trip(self, tmp_path: Path) -> None:
        path = tmp_path / "c.json"
        path.write_text(json.dumps(_curve().model_dump()), encoding="utf-8")
        assert load_curve(path) == _curve()

    def test_invalid_file_rejected(self, tmp_path: Path) -> None:
        path = tmp_path / "bad.json"
        path.write_text(json.dumps({"id": "x"}), encoding="utf-8")
        with pytest.raises(ValidationError):
            load_curve(path)


@pytest.mark.unit
class TestCompareCurve:
    def test_exact_match_passes(self, states: list[SimulationState]) -> None:
        weights = [states[d].weight_kg for d in (0, 5, 10)]
        result = compare_curve(states, _curve(weight_kg=weights), 0.01)
        assert result.passed
        assert result.rmse == pytest.approx(0.0)
        assert result.max_abs_error == pytest.approx(0.0)

    def test_large_error_fails(self, states: list[SimulationState]) -> None:
        result = compare_curve(states, _curve(weight_kg=[90.0, 90.0, 90.0]), 1.0)
        assert not result.passed
        assert result.mean_bias is not None and result.mean_bias < 0

    def test_curve_longer_than_simulation_rejected(
        self, states: list[SimulationState]
    ) -> None:
        with pytest.raises(ValueError, match="only reaches day 10"):
            compare_curve(states, _curve(days=[0, 5, 50]), 1.0)

    def test_tolerance_must_be_positive(self, states: list[SimulationState]) -> None:
        with pytest.raises(ValueError, match="positive"):
            compare_curve(states, _curve(), 0.0)


@pytest.mark.unit
class TestCheckValue:
    def test_within_tolerance(self) -> None:
        result = check_value("n", 74.0, 75.0, 2.0, "kg", "d")
        assert result.passed and result.observed == 74.0 and result.expected == 75.0

    def test_outside_tolerance(self) -> None:
        assert not check_value("n", 70.0, 75.0, 2.0, "kg", "d").passed

    def test_boundary_passes(self) -> None:
        assert check_value("n", 73.0, 75.0, 2.0, "kg", "d").passed

    def test_tolerance_must_be_positive(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            check_value("n", 1.0, 1.0, 0.0, "kg", "d")
