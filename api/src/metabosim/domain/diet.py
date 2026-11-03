"""
metabosim.domain.diet
=======================

Defines dietary intake data structures: ``MacronutrientGrams`` (a
single day's -- or single meal's -- macronutrient breakdown) and
``DietPlan`` (a prescribed/target intake used to drive a simulation).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, computed_field

from metabosim.domain.constants import (
    ATWATER_KCAL_PER_G_ALCOHOL,
    ATWATER_KCAL_PER_G_CARBOHYDRATE,
    ATWATER_KCAL_PER_G_FAT,
    ATWATER_KCAL_PER_G_FIBER,
    ATWATER_KCAL_PER_G_PROTEIN,
)


class MacronutrientGrams(BaseModel):
    """Macronutrient composition of an intake, in grams.

    ``carbohydrate_g`` is *available* carbohydrate (i.e. excludes
    fiber), consistent with FAO (2003) general Atwater factor usage --
    fiber is tracked and energy-counted separately via ``fiber_g``.

    Attributes
    ----------
    protein_g, carbohydrate_g, fat_g:
        Macronutrient masses in grams. Must be non-negative.
    fiber_g:
        Dietary fiber in grams. Must not exceed ``carbohydrate_g`` +
        ``fiber_g`` in any physiologically sensible sense is not
        enforced here (fiber is a distinct nutrient class), but fiber
        cannot be negative.
    alcohol_g:
        Ethanol mass in grams, if relevant to the scenario being
        modeled. Defaults to 0.
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    protein_g: float = Field(..., ge=0.0)
    carbohydrate_g: float = Field(..., ge=0.0)
    fat_g: float = Field(..., ge=0.0)
    fiber_g: float = Field(default=0.0, ge=0.0)
    alcohol_g: float = Field(default=0.0, ge=0.0)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def energy_kcal(self) -> float:
        """Total energy content via general Atwater factors.

        energy_kcal = 4*protein_g + 4*carbohydrate_g + 9*fat_g
                       + 2*fiber_g + 7*alcohol_g

        Source: FAO (2003), "Food energy -- methods of analysis and
        conversion factors," FAO Food and Nutrition Paper 77. See
        ``metabosim.domain.constants`` for the individual factors and
        full citation.

        This is a fixed accounting identity, not a metabolic model --
        it does NOT represent the thermic effect of food (net
        metabolizable energy after digestion cost), which is modeled
        separately in ``metabosim.models.tef`` (Phase 6).
        """
        return (
            self.protein_g * ATWATER_KCAL_PER_G_PROTEIN
            + self.carbohydrate_g * ATWATER_KCAL_PER_G_CARBOHYDRATE
            + self.fat_g * ATWATER_KCAL_PER_G_FAT
            + self.fiber_g * ATWATER_KCAL_PER_G_FIBER
            + self.alcohol_g * ATWATER_KCAL_PER_G_ALCOHOL
        )

    @classmethod
    def zero(cls) -> MacronutrientGrams:
        """Convenience constructor for a zero-intake instance (e.g. a
        fasting day, or as a default/placeholder before a diet plan is
        specified)."""
        return cls(protein_g=0.0, carbohydrate_g=0.0, fat_g=0.0)


class DietPlan(BaseModel):
    """A prescribed dietary intake used to drive a simulation.

    Attributes
    ----------
    macros:
        The macronutrient breakdown for a representative day under
        this plan.
    meal_frequency:
        Optional number of meals/eating occasions per day. Not used by
        any Phase 3-11 model directly, but retained for future
        chrono-nutrition extensions and for report readability.
    label:
        Optional human-readable name for the plan (e.g. "Baseline",
        "20% deficit", "Post-op Day 3"), used in reports and when
        comparing multiple plans in a single simulation run.
    notes:
        Free-text clinical/contextual notes.
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    macros: MacronutrientGrams
    meal_frequency: int | None = Field(default=None, ge=1, le=12)
    label: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=2000)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def energy_kcal(self) -> float:
        """Total prescribed daily energy, derived from ``macros``.

        Exposed at the ``DietPlan`` level for convenience so callers
        don't need to reach into ``.macros.energy_kcal``.
        """
        return self.macros.energy_kcal
