"""
metabosim.models.disease
============================

Disease-specific modifiers: the Decorator extensibility point
promised by ``docs/architecture.md`` since Phase 1 ("New diseases:
add a decorator in models/disease/, compose over any base model
without modifying that base model").

  - ``base``             -- ``DiseaseModifier`` (the adjustment-logic
    interface) and ``DiseaseModifiedBMRModel`` (the actual Decorator,
    composing a base ``BMRModel`` with one or more modifiers into a
    single, fully substitutable ``BMRModel``).
  - ``thyroid``           -- ``ThyroidModifier`` + ``ThyroidStatus``;
    severity-graded BMR adjustment for hypo-/hyperthyroidism
    (McCullagh, 1938).
  - ``body_temperature``  -- ``BodyTemperatureModifier``; BMR
    adjustment for fever/hypothermia, ~13% per degree Celsius
    (DuBois, 1937).
  - ``registry``          -- runtime lookup of Disease Modifiers by
    string ID, forwarding constructor kwargs (mirrors
    ``metabosim.models.activity.registry``).

Because ``DiseaseModifiedBMRModel`` implements the standard
``BMRModel`` interface, it composes with *any* BMR strategy in this
project (including ``EliaOrganBasedBMR`` from Phase 13) with zero
changes to ``metabosim.models.bmr`` itself, and is usable directly by
``metabosim.models.tdee.calculator.calculate_tdee_from_components``,
which now accepts a pre-built ``BMRModel`` instance as well as a
registry string ID -- see that module's docstring.

Example
-------
>>> from metabosim.domain import Person, Sex
>>> from metabosim.models.bmr import MifflinStJeorBMR
>>> from metabosim.models.disease import (
...     DiseaseModifiedBMRModel, ThyroidModifier, ThyroidStatus,
... )
>>> person = Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)
>>> modifier = ThyroidModifier(status=ThyroidStatus.MODERATE_HYPOTHYROID)
>>> adjusted = DiseaseModifiedBMRModel(MifflinStJeorBMR(), [modifier])
>>> round(adjusted.calculate(person), 1)
1424.0
"""

from metabosim.models.disease.base import DiseaseModifiedBMRModel, DiseaseModifier
from metabosim.models.disease.body_temperature import (
    KI_PER_CELSIUS,
    NORMAL_BODY_TEMPERATURE_C,
    BodyTemperatureModifier,
)
from metabosim.models.disease.registry import get_model, list_models, register_model
from metabosim.models.disease.thyroid import (
    THYROID_BMR_ADJUSTMENT_FRACTION,
    ThyroidModifier,
    ThyroidStatus,
)

__all__ = [
    "KI_PER_CELSIUS",
    "NORMAL_BODY_TEMPERATURE_C",
    "THYROID_BMR_ADJUSTMENT_FRACTION",
    "BodyTemperatureModifier",
    "DiseaseModifiedBMRModel",
    "DiseaseModifier",
    "ThyroidModifier",
    "ThyroidStatus",
    "get_model",
    "list_models",
    "register_model",
]
