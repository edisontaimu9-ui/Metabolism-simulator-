"""Unit tests for metabosim.visualization.energy."""

import matplotlib.pyplot as plt
import pytest

from metabosim.domain.simulation_state import SimulationState
from metabosim.visualization.energy import (
    plot_energy_balance,
    plot_energy_intake_vs_expenditure,
)


@pytest.mark.unit
class TestPlotEnergyIntakeVsExpenditure:
    def test_returns_axes_with_two_lines(
        self, weight_only_states: list[SimulationState]
    ) -> None:
        ax = plot_energy_intake_vs_expenditure(weight_only_states)
        assert len(ax.get_lines()) == 2

    def test_plots_correct_data(
        self, weight_only_states: list[SimulationState]
    ) -> None:
        ax = plot_energy_intake_vs_expenditure(weight_only_states)
        intake_line, expenditure_line = ax.get_lines()
        _, intake_y = intake_line.get_data()
        _, expenditure_y = expenditure_line.get_data()
        assert list(intake_y) == pytest.approx(
            [s.energy_intake_kcal for s in weight_only_states]
        )
        assert list(expenditure_y) == pytest.approx(
            [s.energy_expenditure_kcal for s in weight_only_states]
        )

    def test_uses_provided_axes(
        self, weight_only_states: list[SimulationState]
    ) -> None:
        _, ax = plt.subplots()
        returned = plot_energy_intake_vs_expenditure(weight_only_states, ax=ax)
        assert returned is ax

    def test_empty_states_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            plot_energy_intake_vs_expenditure([])


@pytest.mark.unit
class TestPlotEnergyBalance:
    def test_returns_axes_with_bars(
        self, weight_only_states: list[SimulationState]
    ) -> None:
        ax = plot_energy_balance(weight_only_states)
        assert len(ax.patches) == len(weight_only_states)

    def test_bar_heights_match_energy_balance(
        self, weight_only_states: list[SimulationState]
    ) -> None:
        ax = plot_energy_balance(weight_only_states)
        heights = [bar.get_height() for bar in ax.patches]
        assert heights == pytest.approx(
            [s.energy_balance_kcal for s in weight_only_states]
        )

    def test_smoothing_window_adds_a_line(
        self, weight_only_states: list[SimulationState]
    ) -> None:
        # Without smoothing, only the zero-reference axhline is a
        # Line2D (1 line); with smoothing, the moving-average overlay
        # adds a second.
        ax_without = plot_energy_balance(weight_only_states)
        ax_with = plot_energy_balance(weight_only_states, smoothing_window=3)
        assert len(ax_without.get_lines()) == 1
        assert len(ax_with.get_lines()) == 2

    def test_smoothing_window_line_matches_moving_average(
        self, weight_only_states: list[SimulationState]
    ) -> None:
        from metabosim.analysis.series import (
            energy_balance_series_kcal,
            moving_average,
        )

        ax = plot_energy_balance(weight_only_states, smoothing_window=3)
        # The moving-average line is added after the zero-reference
        # axhline, so it's the last Line2D on the axes.
        _, line_y = ax.get_lines()[-1].get_data()
        expected = moving_average(energy_balance_series_kcal(weight_only_states), 3)
        assert list(line_y) == pytest.approx(expected)

    def test_zero_reference_line_present(
        self, weight_only_states: list[SimulationState]
    ) -> None:
        ax = plot_energy_balance(weight_only_states)
        horizontal_lines = ax.get_lines()
        # axhline is drawn as a Line2D
        assert any(
            all(y == 0.0 for y in line.get_data()[1]) for line in horizontal_lines
        )

    def test_empty_states_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            plot_energy_balance([])

    def test_uses_provided_axes(
        self, weight_only_states: list[SimulationState]
    ) -> None:
        _, ax = plt.subplots()
        returned = plot_energy_balance(weight_only_states, ax=ax)
        assert returned is ax
