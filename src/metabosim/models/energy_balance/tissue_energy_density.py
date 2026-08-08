"""
metabosim.models.energy_balance.tissue_energy_density
=========================================================

The "pure conversion" energy balance model: converts a *given* net
daily energy balance directly into a mass-change rate using a blended
tissue energy density, with no weight-dependent feedback term of its
own.

    mass_change_rate_kg_per_day = daily_energy_balance_kcal / rho

This is deliberately the minimal, composable primitive intended for
use inside a real day-by-day simulation (Phase 9), which will
recompute actual BMR/TDEE at each day's *current* weight using
``metabosim.models.bmr`` / ``metabosim.models.tdee``. That recomputation
already supplies the weight-dependent expenditure feedback directly
from real physiology (a heavier ``Person`` has a higher Mifflin-St
Jeor BMR, for instance) -- so this model must NOT add a second,
approximate feedback term on top, or the feedback would be
double-counted. This is why
``includes_weight_dependent_feedback = False`` here, and why the
alternative standalone model,
``metabosim.models.energy_balance.dynamic_quasi_exponential``, is
explicitly documented as NOT safe to combine with a real per-day BMR
recompute for the same reason.

Tissue energy density
------------------------
Rather than one universal constant (contrast with the discredited
3500 kcal/lb rule -- see
``metabosim.models.energy_balance.static_rule``), this model computes
a blended energy density from the two tissue compartments' individual
energy densities and an assumed fraction of the weight change that is
fat-free mass (FFM):

    rho = ffm_fraction * FFM_ENERGY_DENSITY_KCAL_PER_KG
          + (1 - ffm_fraction) * FAT_ENERGY_DENSITY_KCAL_PER_KG

Reference
---------
Heymsfield SB, Gonzalez MCC, Shen W, Redman L, Thomas D. "Weight loss
composition is one-fourth fat-free mass: a critical review and
critique of this widely cited rule." *Obes Rev.* 2014;15(4):310-321.
This review is the source of both the individual tissue energy
densities used here (from chemical tissue composition analysis) and
the "Quarter FFM Rule" default fraction:

::

    Fat-free mass (FFM) energy density    ~1020 kcal/kg
    Fat mass energy density               ~9500 kcal/kg
    Typical FFM fraction of weight change  ~0.25 (i.e. ~75% fat)

Default blended density: 0.25 x 1020 + 0.75 x 9500 = 7380 kcal/kg.

Known limitation
------------------
The 0.25 FFM fraction is itself a population-level average, not a
per-subject prediction -- Heymsfield et al. (2014) document that it
varies with initial body fat, sex, age, and the size/duration of the
energy imbalance (via the Forbes curve). This model accepts
``ffm_fraction`` as a constructor parameter specifically so that
Phase 10's body-composition model can later supply a dynamically
computed, subject-specific fraction instead of this static default,
without requiring any change to this model's interface.
"""

from __future__ import annotations

from metabosim.models.energy_balance.base import EnergyBalanceModel

#: Energy density of fat-free mass, in kcal/kg, from chemical tissue
#: composition analysis. See module docstring for citation.
FFM_ENERGY_DENSITY_KCAL_PER_KG: float = 1020.0

#: Energy density of fat mass, in kcal/kg, from chemical tissue
#: composition analysis. See module docstring for citation.
FAT_ENERGY_DENSITY_KCAL_PER_KG: float = 9500.0

#: Default assumed fraction of weight change that is fat-free mass
#: (the "Quarter FFM Rule"). See module docstring for citation and its
#: documented limitation.
DEFAULT_FFM_FRACTION: float = 0.25


class TissueEnergyDensityModel(EnergyBalanceModel):
    """Converts a given daily energy balance to a mass-change rate
    using a blended fat/fat-free-mass tissue energy density.

    Parameters
    ----------
    ffm_fraction:
        Assumed fraction of weight change that is fat-free mass, in
        [0, 1]. Defaults to 0.25 (the "Quarter FFM Rule" -- see module
        docstring). Override with a subject-specific value once
        available (e.g. from Phase 10's body-composition model).
    """

    name = "Tissue Energy Density (blended FFM/fat, Heymsfield et al., 2014)"
    includes_weight_dependent_feedback = False

    def __init__(self, ffm_fraction: float = DEFAULT_FFM_FRACTION) -> None:
        if not 0.0 <= ffm_fraction <= 1.0:
            raise ValueError(
                f"ffm_fraction must be in [0, 1]; received {ffm_fraction!r}."
            )
        self.ffm_fraction = ffm_fraction

    @property
    def energy_density_kcal_per_kg(self) -> float:
        """The blended tissue energy density implied by
        ``ffm_fraction``, in kcal/kg."""
        return (
            self.ffm_fraction * FFM_ENERGY_DENSITY_KCAL_PER_KG
            + (1.0 - self.ffm_fraction) * FAT_ENERGY_DENSITY_KCAL_PER_KG
        )

    def mass_change_rate_kg_per_day(
        self,
        daily_energy_balance_kcal: float,
        excess_weight_kg: float = 0.0,
    ) -> float:
        del excess_weight_kg  # unused: feedback is expected to come
        # from the caller recomputing real BMR/TDEE each day (Phase 9)
        # -- see module docstring.
        return daily_energy_balance_kcal / self.energy_density_kcal_per_kg

    def project_weight_change_kg(
        self,
        daily_energy_balance_kcal: float,
        days: float,
    ) -> float:
        if days < 0:
            raise ValueError(f"days must be non-negative; received {days!r}.")
        return self.mass_change_rate_kg_per_day(daily_energy_balance_kcal) * days
