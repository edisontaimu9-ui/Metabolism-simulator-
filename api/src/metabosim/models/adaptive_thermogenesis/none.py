"""
metabosim.models.adaptive_thermogenesis.none
================================================

The "no adaptation" model: assumes a constant relationship between
energy expenditure and metabolic mass, with no additional
compensatory adjustment beyond what real BMR/TDEE recomputation
already captures.

This is Model 1 in Rosenbaum & Leibel's three-model framework (see
``metabosim.models.adaptive_thermogenesis.base`` module docstring),
and is the default strategy in
``metabosim.simulation.config.SimulationConfig`` -- not because it is
believed to be the most physiologically accurate, but because the
magnitude and dynamics of real adaptive thermogenesis are genuinely
less settled in the literature than every other component this
project models, and defaulting to an unadjusted prediction is more
defensible than silently assuming one of the contested alternative
magnitudes.
"""

from __future__ import annotations

from metabosim.models.adaptive_thermogenesis.base import AdaptiveThermogenesisModel


class NoAdaptiveThermogenesisModel(AdaptiveThermogenesisModel):
    """Always returns zero adjustment. See module docstring."""

    name = "No Adaptation (Rosenbaum & Leibel Model 1)"

    def calculate_adjustment_kcal(
        self,
        baseline_weight_kg: float,
        current_weight_kg: float,
        reference_expenditure_kcal: float,
    ) -> float:
        del baseline_weight_kg, current_weight_kg, reference_expenditure_kcal
        return 0.0
