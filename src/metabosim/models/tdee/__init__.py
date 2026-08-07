"""
metabosim.models.tdee
========================

TDEE (Total Daily Energy Expenditure) model strategies, plus two
composition "engines" that wire chosen component models together.

  - ``base``          -- ``TDEEModel``, the common strategy interface
    for BMR-to-TDEE scaling.
  - ``pal_multiplier`` -- ``PALMultiplierTDEE``; scales BMR by a
    traditional five-tier clinical activity multiplier (1.2-1.9).
    Bundles an average TEF implicitly -- see its module docstring.
  - ``registry``      -- runtime lookup of TDEE (scaling) models by
    string ID.
  - ``calculator``    -- two entry points:

    - ``calculate_tdee()`` -- ``Person`` in, fully-explained
      ``TDEEResult`` out, using a single bundled BMR-to-TDEE
      multiplier (Phase 5 approach).
    - ``calculate_tdee_from_components()`` -- ``Person`` + diet +
      activity log in, fully-explained ``ComponentTDEEResult`` out,
      summing independently-computed BMR + Activity Energy
      Expenditure + Thermic Effect of Food (Phase 6/7 approach). This
      is the composition that correctly avoids double-counting TEF,
      by requiring a MET-based (not PAL-ratio-based) activity model --
      see ``metabosim.models.activity.base`` for why.

Example
-------
>>> from metabosim.domain import ActivityLevel, Person, Sex
>>> from metabosim.models.tdee import calculate_tdee
>>> person = Person(
...     sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80,
...     activity_level=ActivityLevel.MODERATE,
... )
>>> result = calculate_tdee(person)
>>> round(result.tdee_kcal, 1)
2759.0
"""

from metabosim.models.tdee.base import TDEEModel
from metabosim.models.tdee.calculator import (
    DEFAULT_ACTIVITY_MODEL_ID,
    DEFAULT_BMR_MODEL_ID,
    DEFAULT_TDEE_MODEL_ID,
    DEFAULT_TEF_MODEL_ID,
    ComponentTDEEResult,
    TDEEResult,
    calculate_tdee,
    calculate_tdee_from_components,
)
from metabosim.models.tdee.pal_multiplier import (
    PALMultiplierTDEE,
    get_activity_multiplier,
)
from metabosim.models.tdee.registry import get_model, list_models, register_model

__all__ = [
    "DEFAULT_ACTIVITY_MODEL_ID",
    "DEFAULT_BMR_MODEL_ID",
    "DEFAULT_TDEE_MODEL_ID",
    "DEFAULT_TEF_MODEL_ID",
    "ComponentTDEEResult",
    "PALMultiplierTDEE",
    "TDEEModel",
    "TDEEResult",
    "calculate_tdee",
    "calculate_tdee_from_components",
    "get_activity_multiplier",
    "get_model",
    "list_models",
    "register_model",
]
