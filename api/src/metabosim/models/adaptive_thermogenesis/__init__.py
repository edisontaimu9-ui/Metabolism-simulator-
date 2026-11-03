"""
metabosim.models.adaptive_thermogenesis
===========================================

Adaptive thermogenesis (metabolic adaptation) model strategies: the
change in energy expenditure observed beyond what body-mass and
composition change alone predict, during sustained caloric
restriction or overfeeding.

  - ``base``          -- ``AdaptiveThermogenesisModel``, the common
    strategy interface. Read this module's docstring first: it
    explains the three-model framework (Rosenbaum & Leibel, 2016) this
    package implements directly, and why none of the three is treated
    as definitively correct.
  - ``none``          -- ``NoAdaptiveThermogenesisModel`` (Model 1);
    the default used by ``metabosim.simulation``.
  - ``threshold``      -- ``ThresholdAdaptiveThermogenesisModel``
    (Model 2); a fixed adjustment activates once weight change exceeds
    a threshold.
  - ``proportional``   -- ``ProportionalAdaptiveThermogenesisModel``
    (Model 3); adjustment scales continuously with weight change.
  - ``registry``       -- runtime lookup of Adaptive Thermogenesis
    models by string ID.

Both ``threshold`` and ``proportional`` are calibrated to the same
finding: a 10% experimental weight change produces an expenditure
change of approximately 15% relative to that predicted from body
composition alone (Leibel et al., 1995; Goldsmith et al., 2010).

Example
-------
>>> from metabosim.models.adaptive_thermogenesis import get_model
>>> model = get_model("proportional")
>>> # 10% weight loss from 100kg baseline, 2500 kcal reference TDEE
>>> round(model.calculate_adjustment_kcal(100.0, 90.0, 2500.0), 1)
-375.0
"""

from metabosim.models.adaptive_thermogenesis.base import AdaptiveThermogenesisModel
from metabosim.models.adaptive_thermogenesis.none import NoAdaptiveThermogenesisModel
from metabosim.models.adaptive_thermogenesis.proportional import (
    DEFAULT_ADAPTATION_SLOPE,
    DEFAULT_MAX_WEIGHT_CHANGE_FRACTION,
    ProportionalAdaptiveThermogenesisModel,
)
from metabosim.models.adaptive_thermogenesis.registry import (
    get_model,
    list_models,
    register_model,
)
from metabosim.models.adaptive_thermogenesis.threshold import (
    DEFAULT_ADAPTATION_FRACTION,
    DEFAULT_THRESHOLD_FRACTION,
    ThresholdAdaptiveThermogenesisModel,
)

__all__ = [
    "DEFAULT_ADAPTATION_FRACTION",
    "DEFAULT_ADAPTATION_SLOPE",
    "DEFAULT_MAX_WEIGHT_CHANGE_FRACTION",
    "DEFAULT_THRESHOLD_FRACTION",
    "AdaptiveThermogenesisModel",
    "NoAdaptiveThermogenesisModel",
    "ProportionalAdaptiveThermogenesisModel",
    "ThresholdAdaptiveThermogenesisModel",
    "get_model",
    "list_models",
    "register_model",
]
