"""
metabosim.models.organ
==========================

Organ-level metabolic contribution modeling: decomposes whole-body
BMR into per-organ/tissue contributions (brain, liver, heart,
kidneys, residual lean tissue, adipose tissue).

  - ``elia`` -- ``calculate_organ_bmr_breakdown_kcal`` and
    ``OrganBMRBreakdown``, built on Elia's (1992) specific metabolic
    rates. Like ``metabosim.models.macronutrient.glycogen``, this has
    no registry: Elia's Ki table is a cited dataset, not a competing
    hypothesis with named alternatives.

This module is exposed as a selectable BMR strategy via
``metabosim.models.bmr.elia_organ_based`` (registered as
``"elia_organ_based"`` in ``metabosim.models.bmr.registry``), so it
can be used anywhere an equation-based BMR model can -- including
directly in ``metabosim.simulation.SimulationConfig.bmr_model_id`` --
and cross-validated against the regression-based equations from
Phase 4.

Example
-------
>>> from metabosim.models.organ.elia import calculate_organ_bmr_breakdown_kcal
>>> breakdown = calculate_organ_bmr_breakdown_kcal(fat_mass_kg=16.0, lean_mass_kg=64.0)
>>> round(breakdown.total_kcal, 1)
1726.7
"""

from metabosim.models.organ.elia import (
    AGE_ADJUSTMENT_THRESHOLD_YEARS,
    KI_ADIPOSE,
    KI_BRAIN,
    KI_HEART,
    KI_KIDNEYS,
    KI_LIVER,
    KI_RESIDUAL,
    KI_RESIDUAL_LEAN,
    KI_SKELETAL_MUSCLE,
    REFERENCE_BRAIN_KG,
    REFERENCE_HEART_KG,
    REFERENCE_KIDNEYS_KG,
    REFERENCE_LIVER_KG,
    OrganBMRBreakdown,
    calculate_organ_bmr_breakdown_kcal,
)

__all__ = [
    "AGE_ADJUSTMENT_THRESHOLD_YEARS",
    "KI_ADIPOSE",
    "KI_BRAIN",
    "KI_HEART",
    "KI_KIDNEYS",
    "KI_LIVER",
    "KI_RESIDUAL",
    "KI_RESIDUAL_LEAN",
    "KI_SKELETAL_MUSCLE",
    "REFERENCE_BRAIN_KG",
    "REFERENCE_HEART_KG",
    "REFERENCE_KIDNEYS_KG",
    "REFERENCE_LIVER_KG",
    "OrganBMRBreakdown",
    "calculate_organ_bmr_breakdown_kcal",
]
