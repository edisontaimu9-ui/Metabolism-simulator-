"""
metabosim.domain.units
========================

Pure, stateless unit-conversion helpers.

All domain models store canonical values internally (kilograms,
centimeters, kilocalories) -- see the module docstring in
``metabosim.domain.enums.UnitSystem``. These helpers exist purely for
*presentation-layer* convenience (CLI/GUI input parsing and output
formatting in later phases); nothing in ``metabosim.models`` or
``metabosim.simulation`` should ever need to call these, since internal
calculations always operate on canonical units.

Every function is a simple, exact multiplication/division against a
named constant in ``metabosim.domain.constants`` -- no magic numbers.
"""

from __future__ import annotations

from metabosim.domain.constants import CM_PER_INCH, KCAL_TO_KJ, KG_PER_LB


def kg_to_lb(kg: float) -> float:
    """Convert kilograms to pounds."""
    return kg / KG_PER_LB


def lb_to_kg(lb: float) -> float:
    """Convert pounds to kilograms."""
    return lb * KG_PER_LB


def cm_to_in(cm: float) -> float:
    """Convert centimeters to inches."""
    return cm / CM_PER_INCH


def in_to_cm(inches: float) -> float:
    """Convert inches to centimeters."""
    return inches * CM_PER_INCH


def cm_to_ft_in(cm: float) -> tuple[int, float]:
    """Convert centimeters to a (feet, inches) tuple.

    Returns
    -------
    tuple[int, float]
        ``(feet, inches)`` where ``feet`` is truncated to an integer
        and ``inches`` is the remainder (0 <= inches < 12).
    """
    total_inches = cm_to_in(cm)
    feet = int(total_inches // 12)
    remaining_inches = total_inches - (feet * 12)
    return feet, remaining_inches


def ft_in_to_cm(feet: float, inches: float) -> float:
    """Convert a feet + inches height to centimeters."""
    return in_to_cm((feet * 12) + inches)


def kcal_to_kj(kcal: float) -> float:
    """Convert kilocalories to kilojoules."""
    return kcal * KCAL_TO_KJ


def kj_to_kcal(kj: float) -> float:
    """Convert kilojoules to kilocalories."""
    return kj / KCAL_TO_KJ
