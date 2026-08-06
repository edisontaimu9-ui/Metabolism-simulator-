"""
metabosim.models.bmr
=======================

BMR (Basal Metabolic Rate) / RMR (Resting Metabolic Rate) model
strategies.

Four equations are implemented, each in its own module with a full
citation and documented limitations:

  - ``mifflin_st_jeor`` -- Mifflin-St Jeor (1990); weight-based, no
    body composition required.
  - ``harris_benedict``  -- Harris-Benedict (1919, rev. 1984);
    weight-based, no body composition required.
  - ``katch_mcardle``    -- Katch-McArdle; lean-mass-based, **requires**
    ``Person.body_fat_percent``.
  - ``cunningham``       -- Cunningham (1980); lean-mass-based,
    **requires** ``Person.body_fat_percent``.

All four implement the common ``BMRModel`` interface (``base.py``) and
are selectable at runtime by string ID via ``registry.get_model()``.

Example
-------
>>> from metabosim.domain import Person, Sex
>>> from metabosim.models.bmr import get_model
>>> person = Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)
>>> model = get_model("mifflin_st_jeor")
>>> round(model.calculate(person), 1)
1780.0
"""

from metabosim.models.bmr.base import BMRModel
from metabosim.models.bmr.cunningham import CunninghamBMR
from metabosim.models.bmr.harris_benedict import HarrisBenedictBMR
from metabosim.models.bmr.katch_mcardle import KatchMcArdleBMR
from metabosim.models.bmr.mifflin_st_jeor import MifflinStJeorBMR
from metabosim.models.bmr.registry import get_model, list_models, register_model

__all__ = [
    "BMRModel",
    "CunninghamBMR",
    "HarrisBenedictBMR",
    "KatchMcArdleBMR",
    "MifflinStJeorBMR",
    "get_model",
    "list_models",
    "register_model",
]
