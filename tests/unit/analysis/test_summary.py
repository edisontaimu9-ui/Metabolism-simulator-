"""Unit tests for metabosim.analysis.summary."""

import pytest

from metabosim.analysis.summary import summarize
from metabosim.domain.simulation_state import SimulationState


def _make_states(
    weights: list[float],
    fat_mass: list[float | None] | None = None,
    glycogen: list[float | None] | None = None,
) -> list[SimulationState]:
    fat_mass = fat_mass or [None] * len(weights)
    glycogen = glycogen or [None] * len(weights)
    lean_mass = [
        (w - f) if f is not None else None
        for w, f in zip(weights, fat_mass, strict=True)
    ]
    return [
        SimulationState(
            day_index=i,
            weight_kg=w,
            fat_mass_kg=f,
            lean_mass_kg=lean_mass[i],
            glycogen_g=glycogen[i],
            energy_intake_kcal=2500.0,
            energy_expenditure_kcal=2400.0,
        )
        for i, (w, f) in enumerate(zip(weights, fat_mass, strict=True))
    ]


@pytest.mark.unit
class TestSummarize:
    def test_empty_states_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            summarize([])

    def test_single_state_gives_zero_days_and_zero_rate(self) -> None:
        states = _make_states([80.0])
        summary = summarize(states)
        assert summary.days_simulated == 0
        assert summary.total_weight_change_kg == pytest.approx(0.0)
        assert summary.average_daily_rate_kg == pytest.approx(0.0)

    def test_days_simulated_is_len_minus_one(self) -> None:
        states = _make_states([80.0, 80.1, 80.2, 80.3])
        summary = summarize(states)
        assert summary.days_simulated == 3

    def test_starting_and_ending_weight(self) -> None:
        states = _make_states([80.0, 80.5, 81.0])
        summary = summarize(states)
        assert summary.starting_weight_kg == pytest.approx(80.0)
        assert summary.ending_weight_kg == pytest.approx(81.0)

    def test_total_weight_change_reference_value(self) -> None:
        states = _make_states([80.0, 79.5, 79.0, 78.5])
        summary = summarize(states)
        assert summary.total_weight_change_kg == pytest.approx(-1.5)

    def test_average_daily_rate_reference_value(self) -> None:
        # -1.5 kg over 3 days -> -0.5 kg/day
        states = _make_states([80.0, 79.5, 79.0, 78.5])
        summary = summarize(states)
        assert summary.average_daily_rate_kg == pytest.approx(-0.5)

    def test_positive_change_for_weight_gain(self) -> None:
        states = _make_states([80.0, 80.5, 81.0])
        summary = summarize(states)
        assert summary.total_weight_change_kg > 0.0
        assert summary.average_daily_rate_kg > 0.0

    def test_average_daily_energy_balance_excludes_final_state(self) -> None:
        # 3 states -> 2 simulated days (indices 0, 1); the final
        # state (index 2) is report-only and must not skew the
        # average.
        states = [
            SimulationState(
                day_index=0,
                weight_kg=80.0,
                energy_intake_kcal=2600.0,
                energy_expenditure_kcal=2400.0,  # balance +200
            ),
            SimulationState(
                day_index=1,
                weight_kg=80.02,
                energy_intake_kcal=2600.0,
                energy_expenditure_kcal=2400.0,  # balance +200
            ),
            SimulationState(
                day_index=2,
                weight_kg=80.04,
                energy_intake_kcal=1000.0,
                energy_expenditure_kcal=1000.0,  # balance 0 -- report-only
            ),
        ]
        summary = summarize(states)
        # Average of +200 and +200 (excluding the report-only 0) = 200
        assert summary.average_daily_energy_balance_kcal == pytest.approx(200.0)

    def test_tracked_body_composition_false_when_untracked(self) -> None:
        states = _make_states([80.0, 80.1])
        summary = summarize(states)
        assert summary.tracked_body_composition is False

    def test_tracked_body_composition_true_when_tracked(self) -> None:
        states = _make_states([80.0, 80.1], fat_mass=[16.0, 16.05])
        summary = summarize(states)
        assert summary.tracked_body_composition is True

    def test_tracked_glycogen_false_when_untracked(self) -> None:
        states = _make_states([80.0, 80.1])
        summary = summarize(states)
        assert summary.tracked_glycogen is False

    def test_tracked_glycogen_true_when_tracked(self) -> None:
        states = _make_states([80.0, 80.1], glycogen=[300.0, 295.0])
        summary = summarize(states)
        assert summary.tracked_glycogen is True

    def test_summary_is_frozen(self) -> None:
        from pydantic import ValidationError

        states = _make_states([80.0, 80.1])
        summary = summarize(states)
        with pytest.raises(ValidationError):
            summary.days_simulated = 999  # type: ignore[misc]
