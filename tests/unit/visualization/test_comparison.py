"""Unit tests for metabosim.visualization.comparison."""

import matplotlib.pyplot as plt
import pytest

from metabosim.domain.person import Person
from metabosim.models.bmr.registry import list_models
from metabosim.models.organ.elia import calculate_organ_bmr_breakdown_kcal
from metabosim.visualization.comparison import (
    plot_bmr_model_comparison,
    plot_organ_bmr_breakdown,
)


@pytest.mark.unit
class TestPlotOrganBmrBreakdown:
    def test_returns_axes_with_six_bars(self) -> None:
        breakdown = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=64.0
        )
        ax = plot_organ_bmr_breakdown(breakdown)
        assert len(ax.patches) == 6

    def test_bar_values_match_breakdown_components(self) -> None:
        breakdown = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=64.0
        )
        ax = plot_organ_bmr_breakdown(breakdown)
        bar_widths = sorted(bar.get_width() for bar in ax.patches)
        expected = sorted(
            [
                breakdown.brain_kcal,
                breakdown.liver_kcal,
                breakdown.heart_kcal,
                breakdown.kidneys_kcal,
                breakdown.residual_lean_kcal,
                breakdown.adipose_kcal,
            ]
        )
        assert bar_widths == pytest.approx(expected)

    def test_title_includes_total(self) -> None:
        breakdown = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=64.0
        )
        ax = plot_organ_bmr_breakdown(breakdown)
        assert f"{breakdown.total_kcal:.0f}" in ax.get_title()

    def test_uses_provided_axes(self) -> None:
        breakdown = calculate_organ_bmr_breakdown_kcal(
            fat_mass_kg=16.0, lean_mass_kg=64.0
        )
        _, ax = plt.subplots()
        returned = plot_organ_bmr_breakdown(breakdown, ax=ax)
        assert returned is ax


@pytest.mark.unit
class TestPlotBmrModelComparison:
    def test_with_body_fat_includes_all_five_models(
        self, person_with_bf: Person
    ) -> None:
        ax = plot_bmr_model_comparison(person_with_bf)
        assert len(ax.patches) == len(list_models())

    def test_without_body_fat_skips_lean_mass_models(
        self, person_without_bf: Person
    ) -> None:
        ax = plot_bmr_model_comparison(person_without_bf)
        # Only the two weight-independent equations (Mifflin-St Jeor,
        # Harris-Benedict) should be plotted.
        assert len(ax.patches) == 2

    def test_bar_values_are_positive_bmr_estimates(
        self, person_with_bf: Person
    ) -> None:
        ax = plot_bmr_model_comparison(person_with_bf)
        widths = [bar.get_width() for bar in ax.patches]
        assert all(w > 0 for w in widths)

    def test_uses_provided_axes(self, person_with_bf: Person) -> None:
        _, ax = plt.subplots()
        returned = plot_bmr_model_comparison(person_with_bf, ax=ax)
        assert returned is ax

    def test_title_set(self, person_with_bf: Person) -> None:
        ax = plot_bmr_model_comparison(person_with_bf)
        assert ax.get_title() == "BMR Model Comparison"

    def test_empty_registry_raises_clear_error(
        self, person_with_bf: Person, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Defensive guard: with the built-in registry this branch is
        # unreachable (Mifflin-St Jeor/Harris-Benedict never require
        # body fat), so simulate an empty registry via monkeypatching
        # to confirm the guard actually fires when it should.
        import metabosim.visualization.comparison as comparison_module

        monkeypatch.setattr(comparison_module, "list_models", lambda: [])
        with pytest.raises(ValueError, match="No registered BMR model"):
            plot_bmr_model_comparison(person_with_bf)
