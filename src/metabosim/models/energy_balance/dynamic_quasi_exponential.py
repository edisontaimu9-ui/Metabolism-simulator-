"""
metabosim.models.energy_balance.dynamic_quasi_exponential
==============================================================

A reduced-form dynamic energy balance model that captures the single
most important piece of physiology missing from the static 3500
kcal/lb rule (``metabosim.models.energy_balance.static_rule``):
energy expenditure increases as body mass increases (and decreases as
it decreases), creating negative feedback that drives body weight
toward a new, *bounded* steady state under a sustained caloric
change, rather than changing linearly and unboundedly forever.

Model
-----
Let ``excess_weight_kg`` (denoted ``W`` below) be weight change
already accumulated relative to an initial baseline, and
``daily_energy_balance_kcal`` (denoted ``E`` below) be the *initial*
sustained dietary change relative to baseline-weight maintenance
energy (i.e. new intake minus the ORIGINAL maintenance TDEE, held
constant -- not a value that itself already reflects today's updated
body weight). Then:

    dW/dt = (E - gamma * W) / rho

whose closed-form solution, starting from W(0) = 0, is:

    W(t) = (E / gamma) * (1 - exp(-gamma * t / rho))

which approaches a bounded steady state ``W_steady = E / gamma`` as
``t -> infinity``, with time constant ``tau = rho / gamma``.

This is a reduced, single-compartment approximation of the full
two-compartment (fat mass / fat-free mass) dynamic model in
Hall KD, Sacks G, Chandramohan D, et al. "Quantification of the effect
of energy imbalance on bodyweight." *Lancet.* 2011;378(9793):826-837,
in the same spirit as the explicitly reduced-form model presented in
Hall KD, Jordan PN. "Modeling weight-loss maintenance to help prevent
body weight regain." *Am J Clin Nutr.* 2008;88(6):1495-1503.

Parameters and how they were chosen
---------------------------------------------------------------------
- ``rho`` (tissue energy density, kcal/kg): defaults to the same
  blended value as
  ``metabosim.models.energy_balance.tissue_energy_density`` (7380
  kcal/kg; see that module for the full citation).
- ``gamma`` (expenditure-per-kg-of-accumulated-change slope,
  kcal/kg/day): defaults to 20.0. This value was back-derived (not
  taken as a verbatim published parameter) from a widely-cited
  illustrative example -- a 100 kg sedentary male sustaining a 500
  kcal/day deficit is reported to approach a new steady-state weight
  of roughly 75 kg (i.e. -25 kg) under Hall's full dynamic model; see
  Yoo S. "Dynamic Energy Balance and Obesity Prevention."
  *J Obes Metab Syndr.* 2018;27(4):203-212, citing Hall's model.
  Since this reduced model's steady state is ``E / gamma``, matching
  that reported -25 kg outcome for a -500 kcal/day deficit implies
  ``gamma = 500 / 25 = 20`` kcal/kg/day. **This is a back-of-envelope
  calibration against one illustrative published example, not a
  formally re-fitted parameter from primary data** -- treat it as a
  documented, literature-informed default, adjustable via the
  constructor, not as an exactly-validated constant.

How well the reduced model matches the illustrative example
---------------------------------------------------------------------
With the defaults above, this model predicts, for the same -500
kcal/day scenario:

::

    1 year:   -15.7 kg  (~63% of steady state)
    3 years:  -23.7 kg  (~95% of steady state)
    10 years: -25.0 kg  (steady state, within rounding)

Yoo (2018) reports that Hall's full nonlinear model predicts roughly
half the total loss within the first year and about 95% within three
years for a comparable scenario. This reduced model's 3-year figure
(~95%) lines up well; its 1-year figure (~63%) is higher than the
~50% reported for the full model, which is an expected consequence of
approximating a genuinely nonlinear, two-compartment system with a
single linear ODE. This discrepancy is disclosed here rather than
smoothed over, and is revisited in ``docs/phase_notes/phase_08.md``.

Why this model must NOT be combined with a real per-day BMR recompute
---------------------------------------------------------------------
``includes_weight_dependent_feedback = True`` here: the ``gamma`` term
IS this model's approximation of the same weight-dependent expenditure
feedback that a real BMR/TDEE recomputation (Phase 9, using
``metabosim.models.bmr`` / ``metabosim.models.tdee`` at the subject's
*current*, updated weight each simulated day) would supply directly
from actual physiology. Using both together would double-count that
feedback -- use
``metabosim.models.energy_balance.tissue_energy_density.TissueEnergyDensityModel``
instead inside any simulation that already recomputes real BMR/TDEE
per day. This model is intended for fast, standalone projections when
you do NOT want to run a full day-by-day simulation.
"""

from __future__ import annotations

import math

from metabosim.models.energy_balance.base import EnergyBalanceModel
from metabosim.models.energy_balance.tissue_energy_density import (
    FAT_ENERGY_DENSITY_KCAL_PER_KG,
    FFM_ENERGY_DENSITY_KCAL_PER_KG,
)

#: Default blended tissue energy density (kcal/kg), matching
#: ``TissueEnergyDensityModel``'s default 0.25 FFM / 0.75 fat split.
#: 0.25 * 1020 + 0.75 * 9500 = 7380.0
DEFAULT_ENERGY_DENSITY_KCAL_PER_KG: float = (
    0.25 * FFM_ENERGY_DENSITY_KCAL_PER_KG + 0.75 * FAT_ENERGY_DENSITY_KCAL_PER_KG
)

#: Default expenditure-feedback slope (kcal/kg/day). See module
#: docstring for the back-derivation and its documented caveat.
DEFAULT_EXPENDITURE_SLOPE_KCAL_PER_KG_PER_DAY: float = 20.0


class DynamicQuasiExponentialModel(EnergyBalanceModel):
    """Reduced-form dynamic energy balance model with a bounded,
    asymptotic steady-state response to sustained energy imbalance.
    See module docstring for the model, its parameters, and the
    crucial caveat about not combining it with a real per-day BMR
    recompute.

    Parameters
    ----------
    tissue_energy_density_kcal_per_kg:
        ``rho`` in the module docstring's equations. Defaults to 7380
        kcal/kg.
    expenditure_slope_kcal_per_kg_per_day:
        ``gamma`` in the module docstring's equations. Defaults to
        20.0 kcal/kg/day. Must be strictly positive (a zero or
        negative slope would remove or invert the stabilizing
        feedback this model exists to capture).
    """

    name = "Dynamic Quasi-Exponential Model (reduced from Hall & Jordan, 2008)"
    includes_weight_dependent_feedback = True

    def __init__(
        self,
        tissue_energy_density_kcal_per_kg: float = DEFAULT_ENERGY_DENSITY_KCAL_PER_KG,
        expenditure_slope_kcal_per_kg_per_day: float = (
            DEFAULT_EXPENDITURE_SLOPE_KCAL_PER_KG_PER_DAY
        ),
    ) -> None:
        if tissue_energy_density_kcal_per_kg <= 0.0:
            raise ValueError(
                "tissue_energy_density_kcal_per_kg must be positive; "
                f"received {tissue_energy_density_kcal_per_kg!r}."
            )
        if expenditure_slope_kcal_per_kg_per_day <= 0.0:
            raise ValueError(
                "expenditure_slope_kcal_per_kg_per_day must be positive; "
                f"received {expenditure_slope_kcal_per_kg_per_day!r}."
            )
        self.rho = tissue_energy_density_kcal_per_kg
        self.gamma = expenditure_slope_kcal_per_kg_per_day

    @property
    def time_constant_days(self) -> float:
        """The model's time constant, ``tau = rho / gamma``, in days:
        the time to reach roughly 63% of the eventual steady-state
        weight change."""
        return self.rho / self.gamma

    def steady_state_weight_change_kg(self, daily_energy_balance_kcal: float) -> float:
        """The bounded steady-state weight change, ``E / gamma``, that
        this model predicts as ``t -> infinity`` for a given constant
        sustained ``daily_energy_balance_kcal``."""
        return daily_energy_balance_kcal / self.gamma

    def mass_change_rate_kg_per_day(
        self,
        daily_energy_balance_kcal: float,
        excess_weight_kg: float = 0.0,
    ) -> float:
        return (daily_energy_balance_kcal - self.gamma * excess_weight_kg) / self.rho

    def project_weight_change_kg(
        self,
        daily_energy_balance_kcal: float,
        days: float,
    ) -> float:
        if days < 0:
            raise ValueError(f"days must be non-negative; received {days!r}.")
        steady_state = self.steady_state_weight_change_kg(daily_energy_balance_kcal)
        return steady_state * (1.0 - math.exp(-self.gamma * days / self.rho))
