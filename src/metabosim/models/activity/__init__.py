"""
metabosim.models.activity
============================

Activity Energy Expenditure (AEE) model strategies.

  - ``base``      -- ``ActivityModel``, the common strategy interface.
    Read this module's docstring first: it documents the critical
    distinction between MET-based (TEF-safe) and PAL-ratio-based
    (TEF-inclusive) strategies before combining either with a
    separately-computed TEF figure.
  - ``met_based`` -- ``METBasedActivityModel`` + ``ActivityEntry``;
    bottom-up estimate from a logged activity diary
    (Ainsworth Compendium MET values). Safe to add to a separate TEF
    figure without double-counting.
  - ``iom_pal``   -- ``IOMPALActivityModel``; top-down estimate from
    only a qualitative ``ActivityLevel`` category, using this
    project's 5-tier interpolation of IOM (2005) PAL bands. Already
    implicitly includes an average TEF -- do NOT add a separate TEF
    figure on top of this one.
  - ``registry``  -- runtime lookup of Activity models by string ID.
    Unlike other model registries, ``get_model`` here forwards
    ``**kwargs`` to the model constructor (``met_based`` requires
    ``entries=[...]``).

Example
-------
>>> from metabosim.domain import ActivityLevel, Person, Sex
>>> from metabosim.models.activity import ActivityEntry, get_model
>>> person = Person(
...     sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80,
...     activity_level=ActivityLevel.MODERATE,
... )
>>> entries = [ActivityEntry(met=6.0, duration_hours=1.0, label="jogging")]
>>> model = get_model("met_based", entries=entries)
>>> round(model.calculate(person, bmr_kcal=1780.0), 1)
400.0
"""

from metabosim.models.activity.base import ActivityModel
from metabosim.models.activity.iom_pal import IOMPALActivityModel, get_pal_value
from metabosim.models.activity.met_based import ActivityEntry, METBasedActivityModel
from metabosim.models.activity.registry import get_model, list_models, register_model

__all__ = [
    "ActivityEntry",
    "ActivityModel",
    "IOMPALActivityModel",
    "METBasedActivityModel",
    "get_model",
    "get_pal_value",
    "list_models",
    "register_model",
]
