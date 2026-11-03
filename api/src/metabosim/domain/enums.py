"""
metabosim.domain.enums
========================

Enumerations used throughout the domain layer and beyond. Kept as
plain ``str``-subclassed enums so they:

  - serialize to/from JSON as plain strings (Pydantic-friendly),
  - compare equal to their string value (``Sex.MALE == "male"``),
  - are usable directly as dict keys in model registries
    (``metabosim.models.*.registry``) in later phases.

Design note: ``ActivityLevel`` intentionally stores only *category
labels*, not numeric Physical Activity Level (PAL) factors. The
mapping from category to PAL multiplier is a scientific modeling
choice (several competing PAL tables exist) and therefore belongs in
``metabosim.models.activity`` (Phase 7), not in this dependency-free
domain layer.
"""

from __future__ import annotations

from enum import StrEnum


class Sex(StrEnum):
    """Biological sex, as required by every BMR/RMR equation in the
    literature (Mifflin-St Jeor, Harris-Benedict, Katch-McArdle, etc.
    all have sex-specific coefficients or terms).

    Note: this models a two-category biological input variable required
    by the cited metabolic equations, not a broader demographic
    classification.
    """

    MALE = "male"
    FEMALE = "female"


class ActivityLevel(StrEnum):
    """Physical activity level category.

    Categories follow the qualitative scheme used by the Institute of
    Medicine's Dietary Reference Intakes (IOM, 2005), which groups
    habitual activity into named tiers. The numeric PAL (Physical
    Activity Level) ranges associated with each tier are defined where
    they are actually used -- ``metabosim.models.activity`` -- since
    more than one published PAL table exists and the mapping must
    remain swappable.
    """

    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"


class UnitSystem(StrEnum):
    """Preferred unit system for *display/input convenience only*.

    All quantities are stored canonically in SI-derived clinical units
    internally (kilograms, centimeters, kilocalories) regardless of this
    setting -- see ``metabosim.domain.constants`` for conversion
    factors and ``metabosim.domain.units`` for conversion helpers. This
    enum exists so that future CLI/GUI layers know which units to
    display to the user, without the domain model itself ever storing
    ambiguous units.
    """

    METRIC = "metric"
    IMPERIAL = "imperial"
