"""
metabosim.models.disease.thyroid
====================================

Models the effect of thyroid dysfunction on BMR as a percentage
adjustment, graded by clinical severity.

Thyroid hormone (T3/T4) is a primary regulator of basal metabolic
rate; hypothyroidism suppresses BMR, hyperthyroidism elevates it. This
has been clinically exploited since long before modern thyroid
hormone assays existed -- BMR itself, expressed as a percentage
deviation from a predicted normal value, was historically used as a
*diagnostic test* for thyroid disease.

Reference and calibration
-----------------------------
McCullagh EP. "Some clinical considerations of basal metabolism."
*Cleve Clin J Med.* 1938;5(2):108-115. Documents the classical
clinical BMR-percentage framework directly: overt hypothyroidism
(myxedema) is characteristically associated with BMR **below -20%**
of predicted; goiter/hyperthyroidism cases typically range from
**+14% to +22%**, sometimes higher.

This module extends that classical framework into named severity
tiers, since modern practice categorizes thyroid dysfunction by
severity (subclinical vs. overt, mild vs. severe) rather than reading
a single continuous BMR percentage off an indirect calorimetry trace.
The specific tier boundaries chosen here (10% / 20% / 35% for
hypothyroidism, 15% / 30% / 50% for hyperthyroidism) are consistent
with -- but not verbatim lifted from -- McCullagh's cited ranges: they
interpolate and extrapolate a plausible mild/moderate/severe
progression anchored at his documented values (particularly the -20%
myxedema threshold and the +14-22% typical hyperthyroid range), and
should be treated as a reasonable clinical approximation rather than
individually re-derived experimental measurements for each tier.

Known limitation
------------------
This model does not use actual thyroid hormone lab values (T3, T4,
TSH) -- only a named severity category. A more precise model would
relate BMR adjustment continuously to free T4/T3 concentration; that
would require a dose-response dataset this module does not have
verified access to, and is noted here as a plausible future
refinement rather than implemented speculatively.
"""

from __future__ import annotations

from enum import StrEnum

from metabosim.domain.person import Person
from metabosim.models.disease.base import DiseaseModifier


class ThyroidStatus(StrEnum):
    """Clinical thyroid function category. See module docstring for
    the BMR adjustment associated with each tier."""

    EUTHYROID = "euthyroid"
    MILD_HYPOTHYROID = "mild_hypothyroid"
    MODERATE_HYPOTHYROID = "moderate_hypothyroid"
    SEVERE_HYPOTHYROID = "severe_hypothyroid"
    MILD_HYPERTHYROID = "mild_hyperthyroid"
    MODERATE_HYPERTHYROID = "moderate_hyperthyroid"
    SEVERE_HYPERTHYROID = "severe_hyperthyroid"


#: BMR adjustment fraction per thyroid status tier. See module
#: docstring for the citation and calibration rationale.
THYROID_BMR_ADJUSTMENT_FRACTION: dict[ThyroidStatus, float] = {
    ThyroidStatus.EUTHYROID: 0.0,
    ThyroidStatus.MILD_HYPOTHYROID: -0.10,
    ThyroidStatus.MODERATE_HYPOTHYROID: -0.20,
    ThyroidStatus.SEVERE_HYPOTHYROID: -0.35,
    ThyroidStatus.MILD_HYPERTHYROID: 0.15,
    ThyroidStatus.MODERATE_HYPERTHYROID: 0.30,
    ThyroidStatus.SEVERE_HYPERTHYROID: 0.50,
}


class ThyroidModifier(DiseaseModifier):
    """Adjusts BMR by a percentage determined by clinical thyroid
    status. See module docstring for the model and its calibration.

    Parameters
    ----------
    status:
        The subject's thyroid function category. Defaults to
        ``ThyroidStatus.EUTHYROID`` (zero adjustment).
    """

    def __init__(self, status: ThyroidStatus = ThyroidStatus.EUTHYROID) -> None:
        self.status = status
        self.name = f"Thyroid Dysfunction ({status.value})"

    def apply_to_bmr_kcal(self, base_bmr_kcal: float, person: Person) -> float:
        if base_bmr_kcal <= 0.0:
            raise ValueError(
                f"base_bmr_kcal must be positive; received {base_bmr_kcal!r}."
            )
        fraction = THYROID_BMR_ADJUSTMENT_FRACTION[self.status]
        return base_bmr_kcal * (1.0 + fraction)
