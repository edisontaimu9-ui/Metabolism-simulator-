"""
metabosim.domain.person
=========================

Defines ``Person``, the canonical subject/patient profile used across
every model strategy and the simulation engine.

All fields are stored in canonical clinical units (kilograms,
centimeters, years) regardless of the subject's ``unit_system``
display preference -- see ``metabosim.domain.enums.UnitSystem``.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, computed_field

from metabosim.domain.constants import (
    MAX_AGE_YEARS,
    MAX_BODY_FAT_PERCENT,
    MAX_HEIGHT_CM,
    MAX_WEIGHT_KG,
    MIN_AGE_YEARS,
    MIN_BODY_FAT_PERCENT,
    MIN_HEIGHT_CM,
    MIN_WEIGHT_KG,
)
from metabosim.domain.enums import ActivityLevel, Sex, UnitSystem


class Person(BaseModel):
    """A simulation subject's static/slowly-changing profile.

    This is deliberately a *snapshot* -- ``weight_kg`` and
    ``body_fat_percent`` represent the subject's state at the start of
    a simulation. Time-varying trajectories (weight over the course of
    a simulation) are represented by sequences of
    ``metabosim.domain.simulation_state.SimulationState``, not by
    mutating a ``Person`` in place.

    Attributes
    ----------
    name:
        Optional display name / identifier. Not used in any
        calculation; purely for reports and human readability.
    sex:
        Biological sex, required by every BMR equation implemented in
        ``metabosim.models.bmr`` (Phase 4).
    age_years:
        Age in years. Accepts fractional values (e.g. ``0.5`` for a
        6-month-old infant) to support pediatric use cases.
    height_cm:
        Standing (or recumbent, for infants) height in centimeters.
    weight_kg:
        Body mass in kilograms.
    body_fat_percent:
        Optional body fat percentage (0-100 scale, e.g. ``22.5`` for
        22.5%). Required by body-composition-aware BMR equations
        (e.g. Katch-McArdle, Cunningham) and by
        ``metabosim.models.body_composition``. Left ``None`` when
        unknown; models that require it must raise a clear error
        rather than silently guessing.
    activity_level:
        Habitual activity category (IOM, 2005 qualitative tiers).
        Numeric PAL mapping happens in ``metabosim.models.activity``.
    unit_system:
        Display/input unit preference only; does not affect how values
        are stored (see module docstring).
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    name: str | None = Field(default=None, max_length=200)
    sex: Sex
    age_years: float = Field(..., ge=MIN_AGE_YEARS, le=MAX_AGE_YEARS)
    height_cm: float = Field(..., ge=MIN_HEIGHT_CM, le=MAX_HEIGHT_CM)
    weight_kg: float = Field(..., ge=MIN_WEIGHT_KG, le=MAX_WEIGHT_KG)
    body_fat_percent: float | None = Field(
        default=None, ge=MIN_BODY_FAT_PERCENT, le=MAX_BODY_FAT_PERCENT
    )
    activity_level: ActivityLevel = ActivityLevel.SEDENTARY
    unit_system: UnitSystem = UnitSystem.METRIC

    @computed_field  # type: ignore[prop-decorator]
    @property
    def bmi(self) -> float:
        """Body Mass Index, kg/m^2 (Quetelet, 1832).

        BMI is a screening heuristic, not a diagnostic or metabolic
        quantity -- it is exposed here purely as a commonly-expected
        derived field, and is never used internally by any BMR/TDEE
        model in ``metabosim.models``.
        """
        height_m = self.height_cm / 100.0
        return self.weight_kg / (height_m**2)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def fat_mass_kg(self) -> float | None:
        """Fat mass in kilograms, derived from ``body_fat_percent``.

        Returns ``None`` if ``body_fat_percent`` was not provided --
        this is a deliberate choice over defaulting to a population
        average, since a silently-assumed body fat percentage would
        propagate an unstated assumption into every downstream
        calculation (e.g. Katch-McArdle BMR, body composition
        partitioning).
        """
        if self.body_fat_percent is None:
            return None
        return self.weight_kg * (self.body_fat_percent / 100.0)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def lean_mass_kg(self) -> float | None:
        """Fat-free (lean) mass in kilograms.

        ``None`` under the same condition as ``fat_mass_kg``.
        """
        if self.body_fat_percent is None:
            return None
        return self.weight_kg - self.fat_mass_kg  # type: ignore[operator]

    # NOTE: No cross-field validator is needed to guard against
    # "fat mass exceeding total body weight" -- body_fat_percent is
    # already bounded to [MIN_BODY_FAT_PERCENT, MAX_BODY_FAT_PERCENT]
    # (<= 75%) by its field constraint above, so fat_mass_kg can never
    # exceed weight_kg by construction. An additional check here would
    # be unreachable dead code.
