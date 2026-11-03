"""
metabosim.models.tef
=======================

Thermic Effect of Food (TEF) model strategies.

  - ``base``                    -- ``TEFModel``, the common strategy
    interface.
  - ``macronutrient_specific``  -- ``MacronutrientSpecificTEF``;
    weights each macronutrient's own thermic cost fraction (Jequier &
    Tappy, 1999). Preferred when a macronutrient breakdown is known.
  - ``fixed_percentage``        -- ``FixedPercentageTEF``; flat ~10%
    of total energy intake (IOM, 2005). Preferred when only total
    intake is known, or as a fast diet-agnostic estimate.
  - ``registry``                -- runtime lookup of TEF models by
    string ID.

Important: see ``metabosim.models.tef.base`` module docstring for a
documented caveat about combining this phase's TEF output with the
Phase 5 PAL-multiplier TDEE model -- their published multipliers
already implicitly bundle an average TEF, so naively adding both would
double-count food-processing energy cost. Full integration is planned
for a later phase; see ``docs/phase_notes/phase_06.md``.

Example
-------
>>> from metabosim.domain import MacronutrientGrams
>>> from metabosim.models.tef import get_model
>>> macros = MacronutrientGrams(
...     protein_g=150, carbohydrate_g=300, fat_g=80, fiber_g=30,
... )
>>> model = get_model("macronutrient_specific")
>>> round(model.calculate(macros), 1)
258.9
"""

from metabosim.models.tef.base import TEFModel
from metabosim.models.tef.fixed_percentage import (
    FIXED_TEF_FRACTION,
    FixedPercentageTEF,
)
from metabosim.models.tef.macronutrient_specific import (
    THERMIC_FRACTION_ALCOHOL,
    THERMIC_FRACTION_CARBOHYDRATE,
    THERMIC_FRACTION_FAT,
    THERMIC_FRACTION_PROTEIN,
    MacronutrientSpecificTEF,
)
from metabosim.models.tef.registry import get_model, list_models, register_model

__all__ = [
    "FIXED_TEF_FRACTION",
    "THERMIC_FRACTION_ALCOHOL",
    "THERMIC_FRACTION_CARBOHYDRATE",
    "THERMIC_FRACTION_FAT",
    "THERMIC_FRACTION_PROTEIN",
    "FixedPercentageTEF",
    "MacronutrientSpecificTEF",
    "TEFModel",
    "get_model",
    "list_models",
    "register_model",
]
