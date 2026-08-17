"""Unit tests for metabosim.visualization.trajectory."""

import matplotlib.pyplot as plt
import pytest

from metabosim.domain.simulation_state import SimulationState
from metabosim.visualization.trajectory import (
    plot_body_composition_trajectory,
    plot_glycogen_trajectory,
    plot_weight_trajectory,
)


@pytest.mark.unit
class TestPlotWeightTrajectory:
    def test_returns_axes(self, weight_only_states: list[SimulationState]) -> None:
        ax = plot_weight_trajectory(weight_only_states)
        assert ax is not None

    def test_plots_correct_data(
        self, weight_only_states: list[SimulationState]
    ) -> None:
        ax = plot_weight_trajectory(weight_only_states)
        line = ax.get_lines()[0]
        x_data, y_data = line.get_data()
        assert list(x_data) == [s.day_index for s in weight_only_states]
        assert list(y_data) == pytest.approx([s.weight_kg for s in weight_only_states])

    def test_uses_provided_axes(
        self, weight_only_states: list[SimulationState]
    ) -> None:
        _, ax = plt.subplots()
        returned = plot_weight_trajectory(weight_only_states, ax=ax)
        assert returned is ax

    def test_sets_labels_and_title(
        self, weight_only_states: list[SimulationState]
    ) -> None:
        ax = plot_weight_trajectory(weight_only_states)
        assert ax.get_xlabel() == "Day"
        assert ax.get_ylabel() == "Weight (kg)"
        assert ax.get_title() == "Body Weight Over Time"

    def test_custom_label_appears_in_legend(
        self, weight_only_states: list[SimulationState]
    ) -> None:
        ax = plot_weight_trajectory(weight_only_states, label="Custom Label")
        legend = ax.get_legend()
        assert legend is not None
        legend_texts = [t.get_text() for t in legend.get_texts()]
        assert "Custom Label" in legend_texts

    def test_empty_states_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            plot_weight_trajectory([])


@pytest.mark.unit
class TestPlotBodyCompositionTrajectory:
    def test_returns_axes_with_two_lines(
        self, full_tracking_states: list[SimulationState]
    ) -> None:
        ax = plot_body_composition_trajectory(full_tracking_states)
        assert len(ax.get_lines()) == 2

    def test_plots_correct_fat_and_lean_data(
        self, full_tracking_states: list[SimulationState]
    ) -> None:
        ax = plot_body_composition_trajectory(full_tracking_states)
        fat_line, lean_line = ax.get_lines()
        _, fat_y = fat_line.get_data()
        _, lean_y = lean_line.get_data()
        assert list(fat_y) == pytest.approx(
            [s.fat_mass_kg for s in full_tracking_states]
        )
        assert list(lean_y) == pytest.approx(
            [s.lean_mass_kg for s in full_tracking_states]
        )

    def test_untracked_composition_raises_clear_error(
        self, weight_only_states: list[SimulationState]
    ) -> None:
        with pytest.raises(ValueError, match="body composition tracking"):
            plot_body_composition_trajectory(weight_only_states)

    def test_inconsistent_composition_data_raises_clear_error(self) -> None:
        # Defensive guard: if fat_mass_kg is set on the first state
        # but None on a later one (data that Simulator itself would
        # never produce, but which a hand-constructed list could),
        # the internal consistency check must raise rather than
        # silently plot a gap.
        states = [
            SimulationState(
                day_index=0,
                weight_kg=80.0,
                fat_mass_kg=16.0,
                lean_mass_kg=64.0,
                energy_intake_kcal=2500.0,
                energy_expenditure_kcal=2400.0,
            ),
            SimulationState(
                day_index=1,
                weight_kg=80.0,
                fat_mass_kg=None,
                lean_mass_kg=None,
                energy_intake_kcal=2500.0,
                energy_expenditure_kcal=2400.0,
            ),
        ]
        with pytest.raises(ValueError, match="inconsistent"):
            plot_body_composition_trajectory(states)

    def test_empty_states_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            plot_body_composition_trajectory([])

    def test_sets_title(self, full_tracking_states: list[SimulationState]) -> None:
        ax = plot_body_composition_trajectory(full_tracking_states)
        assert ax.get_title() == "Body Composition Over Time"


@pytest.mark.unit
class TestPlotGlycogenTrajectory:
    def test_returns_axes(self, full_tracking_states: list[SimulationState]) -> None:
        ax = plot_glycogen_trajectory(full_tracking_states)
        assert len(ax.get_lines()) == 1

    def test_plots_correct_data(
        self, full_tracking_states: list[SimulationState]
    ) -> None:
        ax = plot_glycogen_trajectory(full_tracking_states)
        _, y_data = ax.get_lines()[0].get_data()
        assert list(y_data) == pytest.approx(
            [s.glycogen_g for s in full_tracking_states]
        )

    def test_untracked_glycogen_raises_clear_error(
        self, weight_only_states: list[SimulationState]
    ) -> None:
        with pytest.raises(ValueError, match="glycogen tracking"):
            plot_glycogen_trajectory(weight_only_states)

    def test_empty_states_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            plot_glycogen_trajectory([])
