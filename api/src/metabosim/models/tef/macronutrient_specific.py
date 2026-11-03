"""
metabosim.models.tef.macronutrient_specific
===============================================

Macronutrient-specific Thermic Effect of Food model.

TEF is calculated as a weighted sum: each macronutrient's own energy
contribution multiplied by that macronutrient's own thermic cost
fraction, rather than applying one blanket percentage to total energy
intake (contrast with ``metabosim.models.tef.fixed_percentage``).

    TEF = protein_energy_kcal   * 0.25
        + carb_energy_kcal      * 0.075
        + fat_energy_kcal       * 0.02
        + alcohol_energy_kcal   * 0.20

Reference
---------
Jequier E, Tappy L. "Regulation of body weight in humans."
*Physiol Rev.* 1999;79(2):451-480. This review reports the commonly
cited ranges for macronutrient-specific thermic cost:

::

    Protein         20-30% of the energy consumed as protein
    Carbohydrate     5-10% of the energy consumed as carbohydrate
    Fat               0-3% of the energy consumed as fat
    Alcohol         10-30% of the energy consumed as alcohol
                    (unusually high inter-individual variability)

This model uses the midpoint of each published range (25% / 7.5% /
2% / 20%) as a single point estimate. A more advanced future model
could expose the full range as a confidence interval rather than a
point estimate -- noted as a possible extension, not implemented here.

Known limitations
------------------
- **Fiber** is not separately characterized in the cited literature's
  macronutrient breakdown. This model applies the *carbohydrate*
  thermic fraction (7.5%) to fiber's Atwater energy contribution as a
  simplifying assumption, on the basis that fiber is chemically a
  carbohydrate. This likely somewhat overstates fiber's true thermic
  cost, since a substantial fraction of fiber's Atwater-counted energy
  arises from colonic fermentation rather than the same
  digestion/absorption pathway as available carbohydrate -- flagged
  here rather than silently baked in.
- Point estimates only; real individual TEF varies substantially
  (per Jequier & Tappy) with body composition, insulin sensitivity,
  and meal size/frequency, none of which this model accounts for.
- Not validated against measured indirect-calorimetry TEF data in this
  codebase yet -- that comparison belongs to Phase 17 (validation
  against published literature).
"""

from __future__ import annotations

from metabosim.domain.constants import (
    ATWATER_KCAL_PER_G_ALCOHOL,
    ATWATER_KCAL_PER_G_CARBOHYDRATE,
    ATWATER_KCAL_PER_G_FAT,
    ATWATER_KCAL_PER_G_FIBER,
    ATWATER_KCAL_PER_G_PROTEIN,
)
from metabosim.domain.diet import MacronutrientGrams
from metabosim.models.tef.base import TEFModel

#: Thermic cost fraction per macronutrient category, as a fraction of
#: that macronutrient's own Atwater energy contribution. Midpoints of
#: the ranges reported in Jequier & Tappy (1999) -- see module
#: docstring for the full citation and per-range values.
THERMIC_FRACTION_PROTEIN: float = 0.25
THERMIC_FRACTION_CARBOHYDRATE: float = 0.075
THERMIC_FRACTION_FAT: float = 0.02
THERMIC_FRACTION_ALCOHOL: float = 0.20


class MacronutrientSpecificTEF(TEFModel):
    """Weighted, macronutrient-specific Thermic Effect of Food model.

    See module docstring for the full equation, citation, and
    documented limitations (notably the fiber simplifying assumption).
    """

    name = "Macronutrient-Specific (Jequier & Tappy, 1999)"

    def calculate(self, macros: MacronutrientGrams) -> float:
        protein_energy = macros.protein_g * ATWATER_KCAL_PER_G_PROTEIN
        carbohydrate_energy = macros.carbohydrate_g * ATWATER_KCAL_PER_G_CARBOHYDRATE
        fiber_energy = macros.fiber_g * ATWATER_KCAL_PER_G_FIBER
        fat_energy = macros.fat_g * ATWATER_KCAL_PER_G_FAT
        alcohol_energy = macros.alcohol_g * ATWATER_KCAL_PER_G_ALCOHOL

        return (
            protein_energy * THERMIC_FRACTION_PROTEIN
            + (carbohydrate_energy + fiber_energy) * THERMIC_FRACTION_CARBOHYDRATE
            + fat_energy * THERMIC_FRACTION_FAT
            + alcohol_energy * THERMIC_FRACTION_ALCOHOL
        )
