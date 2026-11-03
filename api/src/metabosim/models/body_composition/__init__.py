"""
metabosim.models.body_composition
=====================================

Body composition partitioning strategies: splitting a total body mass
change into fat mass (FM) and fat-free/lean mass (FFM) components.

  - ``base``     -- ``BodyCompositionModel``, the common strategy
    interface. Implements ``partition_mass_change_kg`` once, as a
    template method over the abstract ``ffm_fraction_of_change``, so
    every concrete subclass automatically produces a fat/lean split
    consistent with whatever fraction it reports.
  - ``forbes``   -- ``ForbesPartitionModel``; the fraction of an
    incremental mass change that is fat-free mass depends only on
    current fat mass: ``dFFM/dBW = C / (C + FM)`` (Forbes, 1987/2000;
    Hall, 2007), with sex-specific constants.
  - ``registry`` -- runtime lookup of Body Composition models by
    string ID.

This is the dynamic replacement for the static 0.25 FFM-fraction
default in
``metabosim.models.energy_balance.tissue_energy_density.TissueEnergyDensityModel``,
which that module's Phase 8 docstring explicitly anticipated: "Override
with a subject-specific value once available (e.g. from Phase 10's
body-composition model)." ``metabosim.simulation`` now uses this
package to compute a fresh, current-fat-mass-dependent fraction every
simulated day, whenever the subject's ``body_fat_percent`` is known.

Example
-------
>>> from metabosim.domain import Sex
>>> from metabosim.models.body_composition import get_model
>>> model = get_model("forbes")
>>> model.ffm_fraction_of_change(10.4, Sex.FEMALE)
0.5
>>> round(model.ffm_fraction_of_change(50.0, Sex.FEMALE), 3)
0.172
"""

from metabosim.models.body_composition.base import BodyCompositionModel
from metabosim.models.body_composition.forbes import (
    FORBES_CONSTANT_FEMALE_KG,
    FORBES_CONSTANT_MALE_KG,
    ForbesPartitionModel,
)
from metabosim.models.body_composition.registry import (
    get_model,
    list_models,
    register_model,
)

__all__ = [
    "FORBES_CONSTANT_FEMALE_KG",
    "FORBES_CONSTANT_MALE_KG",
    "BodyCompositionModel",
    "ForbesPartitionModel",
    "get_model",
    "list_models",
    "register_model",
]
