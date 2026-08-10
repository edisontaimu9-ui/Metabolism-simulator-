"""
metabosim.models.adaptive_thermogenesis.base
================================================

Defines ``AdaptiveThermogenesisModel``, the common interface for
strategies that estimate metabolic adaptation: the change in energy
expenditure observed to occur *beyond* what body-mass (and
composition) change alone predicts, during sustained caloric
restriction or overfeeding.

What this is, precisely
--------------------------
Every prior phase's real per-day BMR recompute (Phase 9) already
captures the expenditure change *directly explained* by a lighter or
heavier body (a lighter body has a lower Mifflin-St Jeor BMR, for
instance). Adaptive thermogenesis is the *additional*, separately
documented phenomenon where measured energy expenditure moves further
still -- lower than mass change alone predicts during weight loss,
higher than it predicts during weight gain -- as a compensatory
response that opposes whatever direction body weight is moving.

Reference
---------
Leibel RL, Rosenbaum M, Hirsch J. "Changes in energy expenditure
resulting from altered body weight." *N Engl J Med.*
1995;332(10):621-628. The foundational experimental demonstration:
maintaining a 10% (or more) reduced or elevated body weight produces
compensatory expenditure changes beyond those predicted by body
composition.

Goldsmith R, Joanisse DR, Gallagher D, et al. "Effects of experimental
weight perturbation on skeletal muscle work efficiency, fuel
utilization, and biochemistry in human subjects." *Am J Physiol Regul
Integr Comp Physiol.* 2010;298(1):R79-88. States the quantitative
finding directly: experimentally altering energy stores by ~10%
lowers (or raises) energy expenditure per unit metabolic mass by
"~15% below or above, respectively, that predicted based on changes
in body weight and composition" -- the calibration point used by
``metabosim.models.adaptive_thermogenesis.proportional`` and
``metabosim.models.adaptive_thermogenesis.threshold``.

Three competing models, not one
----------------------------------
Rosenbaum M, Leibel RL. "Models of energy homeostasis in response to
maintenance of reduced body weight." *Obesity (Silver Spring).*
2016;24(8):1620-1629. This paper explicitly frames and tests three
competing model archetypes for how adaptation relates to the degree
of weight change, which this package implements directly as three
separate, separately-selectable strategies:

1. **No adaptation** (constant relationship between expenditure and
   metabolic mass) --
   ``metabosim.models.adaptive_thermogenesis.none.NoAdaptiveThermogenesisModel``.
2. **Threshold** (a fixed degree of adaptation activates once weight
   change exceeds a threshold, with no further change beyond it) --
   ``metabosim.models.adaptive_thermogenesis.threshold.ThresholdAdaptiveThermogenesisModel``.
3. **Proportional / "spring-loading"** (adaptation scales
   continuously with the magnitude of sustained weight change) --
   ``metabosim.models.adaptive_thermogenesis.proportional.ProportionalAdaptiveThermogenesisModel``.

None of the three is presented as definitively correct -- this is a
genuinely less settled area than BMR/TDEE/TEF/activity/energy-balance/
body-composition (see e.g. Martins C, Roekenes J, Salamati S, et al.
"Metabolic adaptation is an illusion, only present when participants
are in negative energy balance." *Am J Clin Nutr.* 2020, which argues
much of the *apparent* adaptation reported acutely after weight loss
resolves once weight stabilizes). Accordingly,
``metabosim.simulation.config.SimulationConfig`` defaults to the
explicit "no adaptation" model rather than assuming one of the
contested alternatives -- see that module's docstring.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class AdaptiveThermogenesisModel(ABC):
    """Abstract base class for metabolic adaptation strategies.

    Subclasses must set ``name`` and implement
    ``calculate_adjustment_kcal``.
    """

    #: Short, human-readable name of the strategy, used in reports and
    #: error messages. Overridden by every concrete subclass.
    name: str = "Unnamed Adaptive Thermogenesis Model"

    @abstractmethod
    def calculate_adjustment_kcal(
        self,
        baseline_weight_kg: float,
        current_weight_kg: float,
        reference_expenditure_kcal: float,
    ) -> float:
        """Calculate the adaptive thermogenesis adjustment, in
        kcal/day, to add to a naive (mass-change-only) predicted
        expenditure figure.

        Parameters
        ----------
        baseline_weight_kg:
            The subject's weight at the start of the scenario being
            evaluated (the "usual"/reference weight against which
            adaptation is measured, per Leibel et al., 1995).
        current_weight_kg:
            The subject's current weight.
        reference_expenditure_kcal:
            The naive predicted expenditure (typically TDEE from
            ``metabosim.models.tdee``, computed from real BMR +
            activity + TEF at the current weight, *before* any
            adaptation adjustment) that the returned adjustment scales
            against.

        Returns
        -------
        float
            The adjustment, in kcal/day. Negative during sustained
            weight loss (adaptive suppression: real expenditure is
            lower than mass change alone predicts); positive during
            sustained weight gain (adaptive increase: real expenditure
            is higher than mass change alone predicts); zero at
            ``current_weight_kg == baseline_weight_kg``.
        """
        raise NotImplementedError

    def __call__(
        self,
        baseline_weight_kg: float,
        current_weight_kg: float,
        reference_expenditure_kcal: float,
    ) -> float:
        """Convenience alias for ``calculate_adjustment_kcal``."""
        return self.calculate_adjustment_kcal(
            baseline_weight_kg, current_weight_kg, reference_expenditure_kcal
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
