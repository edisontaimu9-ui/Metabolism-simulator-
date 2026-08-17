"""Unit tests for metabosim.analysis.series."""

import pytest

from metabosim.analysis.series import (
    day_indices,
    energy_balance_series_kcal,
    energy_expenditure_series_kcal,
    energy_intake_series_kcal,
    fat_mass_series_kg,
    glycogen_series_g,
    lean_mass_series_kg,
    moving_average,
    weight_series_kg,
)
from metabosim.domain.simulation_state import SimulationState


@pytest.fixture
def simple_states() -> list[SimulationState]:
    return [
        SimulationState(
            day_index=i,
            weight_kg=80.0 + i * 0.1,
            energy_intake_kcal=2500.0,
            energy_expenditure_kcal=2400.0 + i,
        )
        for i in range(5)
    ]


@pytest.fixture
def composition_states() -> list[SimulationState]:
    return [
        SimulationState(
            day_index=i,
            weight_kg=80.0,
            fat_mass_kg=16.0,
            lean_mass_kg=64.0,
            glycogen_g=300.0,
            energy_intake_kcal=2500.0,
            energy_expenditure_kcal=2400.0,
        )
        for i in range(3)
    ]


@pytest.mark.unit
class TestSeriesExtraction:
    def test_day_indices(self, simple_states: list[SimulationState]) -> None:
        assert day_indices(simple_states) == [0, 1, 2, 3, 4]

    def test_weight_series_kg(self, simple_states: list[SimulationState]) -> None:
        result = weight_series_kg(simple_states)
        assert result == pytest.approx([80.0, 80.1, 80.2, 80.3, 80.4])

    def test_energy_intake_series_kcal(
        self, simple_states: list[SimulationState]
    ) -> None:
        assert energy_intake_series_kcal(simple_states) == [2500.0] * 5

    def test_energy_expenditure_series_kcal(
        self, simple_states: list[SimulationState]
    ) -> None:
        result = energy_expenditure_series_kcal(simple_states)
        assert result == pytest.approx([2400.0, 2401.0, 2402.0, 2403.0, 2404.0])

    def test_energy_balance_series_kcal(
        self, simple_states: list[SimulationState]
    ) -> None:
        result = energy_balance_series_kcal(simple_states)
        assert result == pytest.approx([100.0, 99.0, 98.0, 97.0, 96.0])

    def test_fat_mass_series_returns_none_when_untracked(
        self, simple_states: list[SimulationState]
    ) -> None:
        assert fat_mass_series_kg(simple_states) == [None] * 5

    def test_fat_mass_series_when_tracked(
        self, composition_states: list[SimulationState]
    ) -> None:
        assert fat_mass_series_kg(composition_states) == [16.0, 16.0, 16.0]

    def test_lean_mass_series_when_tracked(
        self, composition_states: list[SimulationState]
    ) -> None:
        assert lean_mass_series_kg(composition_states) == [64.0, 64.0, 64.0]

    def test_glycogen_series_when_tracked(
        self, composition_states: list[SimulationState]
    ) -> None:
        assert glycogen_series_g(composition_states) == [300.0, 300.0, 300.0]

    def test_empty_states_give_empty_series(self) -> None:
        assert weight_series_kg([]) == []
        assert day_indices([]) == []


@pytest.mark.unit
class TestMovingAverage:
    def test_window_one_returns_original_series(self) -> None:
        values = [1.0, 2.0, 3.0, 4.0]
        assert moving_average(values, window=1) == pytest.approx(values)

    def test_window_larger_than_series_averages_everything_available(self) -> None:
        values = [1.0, 2.0, 3.0]
        result = moving_average(values, window=10)
        # index 0: mean([1]) = 1
        # index 1: mean([1,2]) = 1.5
        # index 2: mean([1,2,3]) = 2.0
        assert result == pytest.approx([1.0, 1.5, 2.0])

    def test_reference_calculation(self) -> None:
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        result = moving_average(values, window=3)
        # idx0: [10] -> 10
        # idx1: [10,20] -> 15
        # idx2: [10,20,30] -> 20
        # idx3: [20,30,40] -> 30
        # idx4: [30,40,50] -> 40
        assert result == pytest.approx([10.0, 15.0, 20.0, 30.0, 40.0])

    def test_output_length_matches_input_length(self) -> None:
        values = [float(i) for i in range(20)]
        result = moving_average(values, window=5)
        assert len(result) == len(values)

    def test_constant_series_smooths_to_itself(self) -> None:
        values = [5.0] * 10
        result = moving_average(values, window=4)
        assert result == pytest.approx(values)

    def test_empty_series_returns_empty(self) -> None:
        assert moving_average([], window=3) == []

    def test_non_positive_window_rejected(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            moving_average([1.0, 2.0], window=0)
        with pytest.raises(ValueError, match="positive"):
            moving_average([1.0, 2.0], window=-1)
