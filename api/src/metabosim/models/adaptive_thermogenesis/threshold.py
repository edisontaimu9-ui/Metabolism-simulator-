"""
metabosim.models.adaptive_thermogenesis.threshold
=====================================================

The threshold adaptive thermogenesis model: a fixed degree of
adaptation activates once the fraction of body weight changed from
baseline exceeds a threshold, with no further change beyond that
point.

    weight_change_fraction = (current_weight_kg - baseline_weight_kg)
                              / baseline_weight_kg

    if |weight_change_fraction| < threshold_fraction:
        adjustment_kcal = 0
    elif weight_change_fraction >= threshold_fraction:
        adjustment_kcal = +adaptation_fraction * reference_expenditure_kcal
    else:  # weight_change_fraction <= -threshold_fraction
        adjustment_kcal = -adaptation_fraction * reference_expenditure_kcal

This is Model 2 in Rosenbaum & Leibel's three-model framework -- see
``metabosim.models.adaptive_thermogenesis.base`` module docstring for
the full framework citation. Rosenbaum & Leibel (2016) describe this
archetype as: "reduction of body energy stores below a threshold
induces adaptive thermogenesis resulting in a decline in EE but there
is no further increase in adaptive thermogenesis following more
weight loss below the threshold."

Calibration
-------------
Both default parameters are calibrated to the same Leibel et al.
(1995) / Goldsmith et al. (2010) finding used in
``metabosim.models.adaptive_thermogenesis.proportional``: a 10%
weight change activates approximately a 15% adaptive adjustment.
Here, that pairing is treated as the threshold-and-magnitude itself,
rather than as a slope: ``threshold_fraction = 0.10``,
``adaptation_fraction = 0.15``, with the adjustment staying flat at
15% for any weight change at or beyond 10%, in contrast to the
proportional model's continuously-scaling adjustment.
"""

from __future__ import annotations

from metabosim.models.adaptive_thermogenesis.base import AdaptiveThermogenesisModel

#: Default weight-change fraction at which adaptation activates. See
#: module docstring for the citation.
DEFAULT_THRESHOLD_FRACTION: float = 0.10

#: Default fixed adaptation magnitude, as a fraction of reference
#: expenditure, applied once the threshold is reached. See module
#: docstring for the citation.
DEFAULT_ADAPTATION_FRACTION: float = 0.15


class ThresholdAdaptiveThermogenesisModel(AdaptiveThermogenesisModel):
    """Adaptation that activates at a fixed magnitude once weight
    change exceeds a threshold, with no further scaling beyond that
    point. See module docstring for the model and its calibration.

    Parameters
    ----------
    threshold_fraction:
        The weight-change fraction (as an absolute value) at which
        adaptation activates. Defaults to 0.10. Must be positive.
    adaptation_fraction:
        The fixed adjustment magnitude, as a fraction of reference
        expenditure, applied once the threshold is reached. Defaults
        to 0.15. Must be non-negative.
    """

    name = "Threshold (Rosenbaum & Leibel Model 2)"

    def __init__(
        self,
        threshold_fraction: float = DEFAULT_THRESHOLD_FRACTION,
        adaptation_fraction: float = DEFAULT_ADAPTATION_FRACTION,
    ) -> None:
        if threshold_fraction <= 0.0:
            raise ValueError(
                f"threshold_fraction must be positive; received {threshold_fraction!r}."
            )
        if adaptation_fraction < 0.0:
            raise ValueError(
                "adaptation_fraction must be non-negative; received "
                f"{adaptation_fraction!r}."
            )
        self.threshold_fraction = threshold_fraction
        self.adaptation_fraction = adaptation_fraction

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

        if weight_change_fraction >= self.threshold_fraction:
            return self.adaptation_fraction * reference_expenditure_kcal
        if weight_change_fraction <= -self.threshold_fraction:
            return -self.adaptation_fraction * reference_expenditure_kcal
        return 0.0
