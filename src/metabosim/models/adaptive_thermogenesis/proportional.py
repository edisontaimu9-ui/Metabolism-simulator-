"""
metabosim.models.adaptive_thermogenesis.proportional
========================================================

The proportional ("spring-loading") adaptive thermogenesis model:
adaptation scales continuously with the fraction of body weight
changed from baseline.

    weight_change_fraction = (current_weight_kg - baseline_weight_kg)
                              / baseline_weight_kg

    adjustment_kcal = k * clamp(weight_change_fraction, -limit, +limit)
                      * reference_expenditure_kcal

This is Model 3 in Rosenbaum & Leibel's three-model framework -- see
``metabosim.models.adaptive_thermogenesis.base`` module docstring for
the full framework citation.

Calibration
-------------
Goldsmith R, Joanisse DR, Gallagher D, et al. "Effects of experimental
weight perturbation on skeletal muscle work efficiency, fuel
utilization, and biochemistry in human subjects." *Am J Physiol Regul
Integr Comp Physiol.* 2010;298(1):R79-88, citing the original Leibel
RL, Rosenbaum M, Hirsch J. *N Engl J Med.* 1995 experiments, reports
that a 10% experimental weight change produces an expenditure change
of approximately 15% relative to that predicted from body composition
alone -- symmetrically, for both weight loss and weight gain. This
gives the default proportionality constant:

    k = 0.15 / 0.10 = 1.5

so that ``weight_change_fraction = -0.10`` (a 10% weight loss)
produces ``adjustment_kcal = -0.15 * reference_expenditure_kcal`` (a
15% suppression), matching the cited finding exactly.

Why the fraction is clamped
------------------------------
Leibel's experimental protocol tested weight changes up to
approximately 20% (the most extreme condition studied). This model's
linear extrapolation beyond that point is an assumption *built into*
the proportional model's own definition (adaptation scales linearly
with the fraction, by construction), not an independently measured
data point -- there is no direct experimental confirmation that, say,
a 40% weight change produces exactly 60% adaptation. To avoid
extrapolating into physiologically implausible territory (a
sufficiently large clamp-free fraction could in principle predict an
adjustment exceeding the reference expenditure itself), the fraction
is clamped to Leibel's tested range by default
(``max_weight_change_fraction = 0.20``) before scaling.
"""

from __future__ import annotations

from metabosim.models.adaptive_thermogenesis.base import AdaptiveThermogenesisModel

#: Default proportionality constant, calibrated so that a 10% weight
#: change produces a 15% expenditure adjustment (0.15 / 0.10 = 1.5).
#: See module docstring for the citation.
DEFAULT_ADAPTATION_SLOPE: float = 1.5

#: Default clamp on the weight-change fraction, matching the most
#: extreme condition tested in Leibel et al. (1995) (~20% weight
#: change). See module docstring.
DEFAULT_MAX_WEIGHT_CHANGE_FRACTION: float = 0.20


class ProportionalAdaptiveThermogenesisModel(AdaptiveThermogenesisModel):
    """Adaptation that scales continuously with the fraction of body
    weight changed from baseline, clamped to the empirically tested
    range. See module docstring for the model, its calibration, and
    the clamping rationale.

    Parameters
    ----------
    adaptation_slope:
        ``k`` in the module docstring's equation. Defaults to 1.5.
    max_weight_change_fraction:
        The clamp applied to the weight-change fraction before
        scaling. Defaults to 0.20. Must be positive.
    """

    name = "Proportional / Spring-Loading (Rosenbaum & Leibel Model 3)"

    def __init__(
        self,
        adaptation_slope: float = DEFAULT_ADAPTATION_SLOPE,
        max_weight_change_fraction: float = DEFAULT_MAX_WEIGHT_CHANGE_FRACTION,
    ) -> None:
        if max_weight_change_fraction <= 0.0:
            raise ValueError(
                "max_weight_change_fraction must be positive; received "
                f"{max_weight_change_fraction!r}."
            )
        self.adaptation_slope = adaptation_slope
        self.max_weight_change_fraction = max_weight_change_fraction

    def calculate_adjustment_kcal(
        self,
        baseline_weight_kg: float,
        current_weight_kg: float,
        reference_expenditure_kcal: float,
    ) -> float:
        if baseline_weight_kg <= 0.0:
            raise ValueError(
                "baseline_weight_kg must be positive; received "
                f"{baseline_weight_kg!r}."
            )
        weight_change_fraction = (
            current_weight_kg - baseline_weight_kg
        ) / baseline_weight_kg
        clamped_fraction = max(
            -self.max_weight_change_fraction,
            min(self.max_weight_change_fraction, weight_change_fraction),
        )
        return self.adaptation_slope * clamped_fraction * reference_expenditure_kcal
