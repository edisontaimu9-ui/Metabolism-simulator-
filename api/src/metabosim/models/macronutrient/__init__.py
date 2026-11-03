"""
metabosim.models.macronutrient
==================================

Macronutrient-level metabolic dynamics: short-term glycogen (and its
associated water) fluctuation.

  - ``glycogen`` -- carbohydrate mass-balance functions
    (``max_glycogen_g``, ``glycogen_and_water_kg``,
    ``step_glycogen_g``, ``step_reference_carbohydrate_intake_g``).

Unlike every other model family in this project, there is no registry
here: the hydration coefficient (2.7 g water per g glycogen) and
storage-capacity relationship are physical/chemical facts cited
directly from Chow & Hall (2008), not competing scientific hypotheses
with plausible named alternatives -- see
``metabosim.models.macronutrient.glycogen`` module docstring for the
full explanation of this deliberate departure from the Strategy
pattern used elsewhere.

This module fills in exactly the short-term ("a few days") transient
that Phases 8-11's fat/lean-only simulation deliberately -- and, per
Chow & Hall's own justification, correctly -- ignores for anything
beyond that window. See ``metabosim.simulation.stepper`` for how the
two layers combine without double-counting.

Example
-------
>>> from metabosim.models.macronutrient.glycogen import (
...     max_glycogen_g, glycogen_and_water_kg,
... )
>>> round(max_glycogen_g(70.0), 1)
500.0
>>> round(glycogen_and_water_kg(500.0), 2)
1.85
"""

from metabosim.models.macronutrient.glycogen import (
    DEFAULT_OXIDATION_TIME_CONSTANT_DAYS,
    GLYCOGEN_WATER_RATIO,
    REFERENCE_MAX_GLYCOGEN_G,
    REFERENCE_WEIGHT_KG,
    glycogen_and_water_kg,
    max_glycogen_g,
    step_glycogen_g,
    step_reference_carbohydrate_intake_g,
)

__all__ = [
    "DEFAULT_OXIDATION_TIME_CONSTANT_DAYS",
    "GLYCOGEN_WATER_RATIO",
    "REFERENCE_MAX_GLYCOGEN_G",
    "REFERENCE_WEIGHT_KG",
    "glycogen_and_water_kg",
    "max_glycogen_g",
    "step_glycogen_g",
    "step_reference_carbohydrate_intake_g",
]
