"""
metabosim.models.tdee
========================

TDEE (Total Daily Energy Expenditure) model strategies, plus the
composition "engine" that wires a chosen BMR model together with a
chosen TDEE model.

  - ``base``          -- ``TDEEModel``, the common strategy interface.
  - ``pal_multiplier`` -- ``PALMultiplierTDEE``; scales BMR by a
    traditional five-tier clinical activity multiplier (1.2-1.9).
    Currently the only registered strategy; see its module docstring
    for important caveats around TEF double-counting once Phase 6
    introduces an explicit TEF model.
  - ``registry``      -- runtime lookup of TDEE models by string ID.
  - ``calculator``    -- ``calculate_tdee()``, the primary public
    entry point: ``Person`` in, fully-explained ``TDEEResult`` out.

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
    DEFAULT_BMR_MODEL_ID,
    DEFAULT_TDEE_MODEL_ID,
    TDEEResult,
    calculate_tdee,
)
from metabosim.models.tdee.pal_multiplier import (
    PALMultiplierTDEE,
    get_activity_multiplier,
)
from metabosim.models.tdee.registry import get_model, list_models, register_model

__all__ = [
    "DEFAULT_BMR_MODEL_ID",
    "DEFAULT_TDEE_MODEL_ID",
    "PALMultiplierTDEE",
    "TDEEModel",
    "TDEEResult",
    "calculate_tdee",
    "get_activity_multiplier",
    "get_model",
    "list_models",
    "register_model",
]
