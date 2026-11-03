"""
metabosim.models.energy_balance
==================================

Energy Balance model strategies: converting a net daily energy
balance (kcal/day) into a rate of body mass change (kg/day).

  - ``base``                     -- ``EnergyBalanceModel``, the common
    strategy interface. Read this module's docstring first: it
    explains why the naive "3500 kcal/lb" rule is scientifically
    wrong, and documents the ``includes_weight_dependent_feedback``
    flag that governs safe composition with a real per-day BMR
    recompute (Phase 9).
  - ``static_rule``               -- ``StaticEnergyBalanceModel``; the
    3500 kcal/lb rule (Wishnofsky, 1958). Retained ONLY for comparison
    and teaching -- not recommended for real projections.
  - ``tissue_energy_density``     -- ``TissueEnergyDensityModel``; the
    minimal, composable primitive intended for use inside a real
    day-by-day simulation that recomputes BMR/TDEE itself.
  - ``dynamic_quasi_exponential`` -- ``DynamicQuasiExponentialModel``;
    a standalone reduced-form model (after Hall & Jordan, 2008) with a
    bounded steady-state response, for fast projections when a full
    day-by-day simulation isn't needed. Do NOT combine with a real
    per-day BMR recompute -- see its module docstring.
  - ``registry``                  -- runtime lookup of Energy Balance
    models by string ID.

Example
-------
>>> from metabosim.models.energy_balance import get_model
>>> static = get_model("static_rule")
>>> dynamic = get_model("dynamic_quasi_exponential")
>>> round(static.project_weight_change_kg(-500, 365), 1)
-23.7
>>> round(dynamic.project_weight_change_kg(-500, 365), 1)
-15.7
"""

from metabosim.models.energy_balance.base import EnergyBalanceModel
from metabosim.models.energy_balance.dynamic_quasi_exponential import (
    DEFAULT_ENERGY_DENSITY_KCAL_PER_KG,
    DEFAULT_EXPENDITURE_SLOPE_KCAL_PER_KG_PER_DAY,
    DynamicQuasiExponentialModel,
)
from metabosim.models.energy_balance.registry import (
    get_model,
    list_models,
    register_model,
)
from metabosim.models.energy_balance.static_rule import (
    ENERGY_DENSITY_KCAL_PER_KG,
    WISHNOFSKY_KCAL_PER_LB,
    StaticEnergyBalanceModel,
)
from metabosim.models.energy_balance.tissue_energy_density import (
    DEFAULT_FFM_FRACTION,
    FAT_ENERGY_DENSITY_KCAL_PER_KG,
    FFM_ENERGY_DENSITY_KCAL_PER_KG,
    TissueEnergyDensityModel,
)

__all__ = [
    "DEFAULT_ENERGY_DENSITY_KCAL_PER_KG",
    "DEFAULT_EXPENDITURE_SLOPE_KCAL_PER_KG_PER_DAY",
    "DEFAULT_FFM_FRACTION",
    "ENERGY_DENSITY_KCAL_PER_KG",
    "FAT_ENERGY_DENSITY_KCAL_PER_KG",
    "FFM_ENERGY_DENSITY_KCAL_PER_KG",
    "WISHNOFSKY_KCAL_PER_LB",
    "DynamicQuasiExponentialModel",
    "EnergyBalanceModel",
    "StaticEnergyBalanceModel",
    "TissueEnergyDensityModel",
    "get_model",
    "list_models",
    "register_model",
]
