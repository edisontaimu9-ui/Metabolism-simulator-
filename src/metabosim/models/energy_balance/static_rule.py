"""
metabosim.models.energy_balance.static_rule
==============================================

The static "3500 kcal per pound" rule -- included in this codebase
for comparison and teaching purposes, NOT recommended for actual
projections. See the warning in the class docstring.

    mass_change_rate_kg_per_day = daily_energy_balance_kcal / rho

where ``rho`` is a fixed energy density (kcal/kg) with no dependence
on accumulated weight change, current body composition, or time.

Reference
---------
Wishnofsky M. "Caloric equivalents of gained or lost weight."
*Am J Clin Nutr.* 1958;6(5):542-546. Wishnofsky estimated that a
pound of adipose tissue stores approximately 3500 kcal, based on the
chemical composition of human fat tissue known at the time.

Why this is wrong, precisely
------------------------------
Hall KD, Chow CC. "Why is the 3500 kcal per pound weight loss rule
wrong?" *Int J Obes (Lond).* 2013;37(12):1614. Two independent
problems, both absent from this model:

1. **The energy density of tissue actually gained or lost is not a
   universal constant.** Wishnofsky's figure assumed pure adipose
   tissue; real weight change is a mix of fat and fat-free mass whose
   ratio itself varies with the size and duration of the energy
   imbalance (Forbes' rule -- see
   ``metabosim.models.energy_balance.tissue_energy_density`` for a
   documented, cited blended estimate, and
   ``metabosim.models.body_composition``, Phase 10, for a full
   dynamic treatment).
2. **This model predicts unbounded, perpetual linear weight change**
   for any sustained energy imbalance. A 500 kcal/day deficit
   maintained for one year predicts roughly 23.7 kg lost under this
   rule -- consistent with the ~22 kg/year figure reported for this
   same scenario in Yoo S. "Dynamic Energy Balance and Obesity
   Prevention." *J Obes Metab Syndr.* 2018;27(4):203-212; extending
   the same sustained deficit to 10 years predicts an obviously
   impossible ~236 kg lost, with no plateau, ever. Real physiology
   does not behave this way: energy expenditure rises as body mass
   increases (or falls as it decreases), creating a negative feedback
   loop that drives body weight toward a new, *bounded* steady state
   instead. See
   ``metabosim.models.energy_balance.dynamic_quasi_exponential`` for
   a model that captures this feedback, and the illustrative
   real-world comparison in that module's docstring.

This model is retained in the registry specifically so it can be used
as an explicit baseline for demonstrating how far a widely-taught rule
of thumb diverges from validated dynamic physiology -- not because it
is a good choice for any actual projection.
"""

from __future__ import annotations

from metabosim.domain.constants import KG_PER_LB
from metabosim.models.energy_balance.base import EnergyBalanceModel

#: Wishnofsky's (1958) estimate of the energy content of one pound of
#: adipose tissue. See module docstring.
WISHNOFSKY_KCAL_PER_LB: float = 3500.0

#: The same energy density expressed per kilogram, using the exact
#: pound-to-kilogram conversion (see
#: ``metabosim.domain.constants.KG_PER_LB``). Approximately 7716
#: kcal/kg.
ENERGY_DENSITY_KCAL_PER_KG: float = WISHNOFSKY_KCAL_PER_LB / KG_PER_LB


class StaticEnergyBalanceModel(EnergyBalanceModel):
    """The static 3500 kcal/lb rule (Wishnofsky, 1958).

    .. warning::
        This model is scientifically outdated and is included only for
        comparison against
        ``metabosim.models.energy_balance.dynamic_quasi_exponential``
        and for teaching why the "3500 kcal rule" fails to predict
        real weight-loss plateaus. Do not use it for actual clinical
        or research projections -- see module docstring for the
        specific, cited critique.
    """

    name = "Static 3500 kcal/lb Rule (Wishnofsky, 1958) -- NOT RECOMMENDED"
    includes_weight_dependent_feedback = False

    def mass_change_rate_kg_per_day(
        self,
        daily_energy_balance_kcal: float,
        excess_weight_kg: float = 0.0,
    ) -> float:
        del excess_weight_kg  # unused: this model has no feedback term.
        return daily_energy_balance_kcal / ENERGY_DENSITY_KCAL_PER_KG

    def project_weight_change_kg(
        self,
        daily_energy_balance_kcal: float,
        days: float,
    ) -> float:
        if days < 0:
            raise ValueError(f"days must be non-negative; received {days!r}.")
        return self.mass_change_rate_kg_per_day(daily_energy_balance_kcal) * days
