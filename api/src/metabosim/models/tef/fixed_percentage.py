"""
metabosim.models.tef.fixed_percentage
=========================================

Fixed-percentage Thermic Effect of Food model: the common simplified
clinical approximation that TEF is roughly 10% of total energy intake,
regardless of macronutrient composition.

    TEF = total_energy_kcal * 0.10

Reference
---------
Institute of Medicine (US). *Dietary Reference Intakes for Energy,
Carbohydrate, Fiber, Fat, Fatty Acids, Cholesterol, Protein, and Amino
Acids.* National Academies Press; 2005. TEF is discussed there as
commonly approximated at about 10% of energy intake for a mixed diet,
a simplification frequently used in clinical practice when a detailed
macronutrient breakdown of intake isn't available.

When to use this vs. ``MacronutrientSpecificTEF``
-----------------------------------------------------
Use this model when only total energy intake is known (no
macronutrient breakdown available) or when a fast, diet-composition-
agnostic estimate is acceptable. Use
``metabosim.models.tef.macronutrient_specific.MacronutrientSpecificTEF``
whenever the macronutrient breakdown is known and diet composition
matters to the question being asked (e.g. comparing a high-protein vs.
high-fat diet at matched calories) -- the two diets would receive
identical TEF under this fixed-percentage model, which is precisely
the scenario where that would be scientifically misleading.
"""

from __future__ import annotations

from metabosim.domain.diet import MacronutrientGrams
from metabosim.models.tef.base import TEFModel

#: Fraction of total energy intake attributed to TEF under this
#: simplified model. See module docstring for citation.
FIXED_TEF_FRACTION: float = 0.10


class FixedPercentageTEF(TEFModel):
    """Approximates TEF as a flat fraction of total energy intake,
    independent of macronutrient composition. See module docstring.
    """

    name = "Fixed Percentage (~10% of intake, IOM 2005)"

    def calculate(self, macros: MacronutrientGrams) -> float:
        return macros.energy_kcal * FIXED_TEF_FRACTION
