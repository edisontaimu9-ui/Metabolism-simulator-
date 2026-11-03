"""
metabosim.models.energy_balance.base
=======================================

Defines ``EnergyBalanceModel``, the common interface for strategies
that convert a net daily energy balance (kcal/day surplus or deficit)
into a rate of body mass change (kg/day).

Why this is a genuine "engine," not a lookup table
------------------------------------------------------
The naive, still widely-taught approach ("3500 kcal = 1 lb") treats
mass change as *linear and unbounded*: a sustained 500 kcal/day
deficit is claimed to produce the same 1 lb/week loss forever, with no
plateau. This is empirically false and has been directly refuted:
Hall KD, Chow CC. "Why is the 3500 kcal per pound weight loss rule
wrong?" *Int J Obes (Lond).* 2013;37(12):1614. Real body weight
approaches a new, *bounded* steady state under sustained caloric
change, because energy expenditure itself increases with body mass
(a heavier body has more metabolically active tissue and costs more
to move) -- a negative feedback loop entirely absent from the static
rule. See Hall KD, Sacks G, Chandramohan D, et al. "Quantification of
the effect of energy imbalance on bodyweight." *Lancet.*
2011;378(9793):826-837 for the foundational dynamic modeling work this
package draws on.

Two parameters that matter, and the flag that tracks them
---------------------------------------------------------------------
Every concrete model in this package must declare
``includes_weight_dependent_feedback: bool``, mirroring the
``includes_average_tef`` flag introduced in
``metabosim.models.activity.base`` for the same reason: some models
(``metabosim.models.energy_balance.dynamic_quasi_exponential``) build
the weight-dependent expenditure feedback loop directly into their own
closed-form solution, while others
(``metabosim.models.energy_balance.tissue_energy_density``)
deliberately do NOT, because they are intended to be composed inside a
day-by-day simulation (Phase 9) that recomputes real BMR/TDEE at each
day's updated weight -- which already supplies that feedback via the
actual physiology (a heavier person has a higher Mifflin-St Jeor BMR,
for instance). Combining a model that already has the feedback baked
in with a caller that ALSO recomputes real BMR each day would
double-count the feedback, the same class of error resolved for
TEF/Activity in Phase 7.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class EnergyBalanceModel(ABC):
    """Abstract base class for energy-balance-to-mass-change strategies.

    Subclasses must set ``name`` and
    ``includes_weight_dependent_feedback``, and implement both
    ``mass_change_rate_kg_per_day`` and ``project_weight_change_kg``.
    """

    #: Short, human-readable name of the strategy, used in reports and
    #: error messages. Overridden by every concrete subclass.
    name: str = "Unnamed Energy Balance Model"

    #: Whether this strategy's own calculation already accounts for
    #: energy expenditure increasing with body mass (True), or assumes
    #: that feedback will be supplied externally -- e.g. by a caller
    #: recomputing real BMR/TDEE at the updated weight each simulated
    #: day (False). No default is given, so that a subclass which
    #: forgets to declare this raises a loud ``AttributeError`` rather
    #: than silently risking a double-counted or feedback-free
    #: simulation. See module docstring.
    includes_weight_dependent_feedback: bool

    @abstractmethod
    def mass_change_rate_kg_per_day(
        self,
        daily_energy_balance_kcal: float,
        excess_weight_kg: float = 0.0,
    ) -> float:
        """Instantaneous rate of body mass change, dW/dt, in kg/day.

        Parameters
        ----------
        daily_energy_balance_kcal:
            Net energy balance for the day being evaluated (energy
            intake minus energy expenditure), in kcal. Positive for a
            surplus, negative for a deficit.
        excess_weight_kg:
            The subject's weight change *already accumulated* relative
            to their original baseline weight at the start of the
            scenario being modeled (NOT their absolute body weight).
            Used by models whose own feedback term scales with
            accumulated weight change
            (``includes_weight_dependent_feedback = True``); ignored
            by models that don't model that feedback themselves.
            Defaults to 0.0 for a subject still at their baseline
            weight.

        Returns
        -------
        float
            Rate of body mass change, in kg/day. Positive for weight
            gain, negative for weight loss.
        """
        raise NotImplementedError

    @abstractmethod
    def project_weight_change_kg(
        self,
        daily_energy_balance_kcal: float,
        days: float,
    ) -> float:
        """Closed-form projected total weight CHANGE, in kilograms,
        after ``days`` days of a *sustained, constant*
        ``daily_energy_balance_kcal``, starting from zero excess
        weight.

        This is the definite integral of
        ``mass_change_rate_kg_per_day`` over time for a constant
        energy-balance input. It exists as a fast, direct-computation
        convenience for constant-conditions scenarios and for
        validating the rate function against a known closed-form
        solution; it is not what a day-by-day, time-varying simulation
        (Phase 9) will use once built -- that will call
        ``mass_change_rate_kg_per_day`` once per simulated day instead.

        Parameters
        ----------
        daily_energy_balance_kcal:
            The constant net energy balance sustained for the entire
            period, in kcal/day.
        days:
            Number of days the energy balance is sustained for. Must
            be non-negative.

        Returns
        -------
        float
            Total projected weight change, in kilograms, over the
            given period. Positive for weight gain, negative for
            weight loss.
        """
        raise NotImplementedError

    def __call__(
        self, daily_energy_balance_kcal: float, excess_weight_kg: float = 0.0
    ) -> float:
        """Convenience alias for ``mass_change_rate_kg_per_day``."""
        return self.mass_change_rate_kg_per_day(
            daily_energy_balance_kcal, excess_weight_kg
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
