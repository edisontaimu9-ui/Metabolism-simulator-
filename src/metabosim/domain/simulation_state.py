"""
metabosim.domain.simulation_state
====================================

Defines ``SimulationState``: a single time-point snapshot produced by
the (future, Phase 8-9) simulation engine. A completed simulation run
is represented as an ordered sequence of ``SimulationState`` objects --
this is the single artifact that ``metabosim.analysis``,
``metabosim.visualization``, and ``metabosim.reports`` consume
downstream (see docs/architecture.md, section 2 "Data flow").

This module defines the *shape* of that data only. No simulation logic
(how one state transitions to the next) lives here -- that belongs to
``metabosim.simulation.stepper`` (Phase 8+).
"""

from __future__ import annotations

from datetime import date as date_type

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

#: Absolute tolerance (kg) permitted between weight_kg and the sum of
#: fat_mass_kg + lean_mass_kg, when both composition fields are
#: provided. Nonzero to absorb floating-point drift and legitimately
#: untracked minor compartments (e.g. bone mineral content nuances)
#: without being loose enough to hide real modeling bugs.
_COMPOSITION_SUM_TOLERANCE_KG: float = 0.05


class SimulationState(BaseModel):
    """A single day's (or single timestep's) simulation snapshot.

    Attributes
    ----------
    day_index:
        Zero-based integer index of this state within a simulation run
        (day 0 = initial state, before any simulated time has passed).
    date:
        Optional calendar date corresponding to this state, useful for
        report readability when a simulation is anchored to a real
        start date.
    weight_kg:
        Total body weight at this timestep.
    fat_mass_kg, lean_mass_kg:
        Body composition partition at this timestep. Both optional
        (populated once ``metabosim.models.body_composition`` exists,
        Phase 10) but when both are present they must sum to
        approximately ``weight_kg`` (see validator below).
    glycogen_g:
        Total body glycogen store, in grams. Populated by
        ``metabosim.models.macronutrient`` (Phase 12).
    total_body_water_kg:
        The glycogen-associated component of total body water, in
        kilograms (NOT whole-body water/hydration status, which
        remains out of scope -- see
        ``metabosim.models.macronutrient.glycogen`` module docstring).
        Following Chow CC, Hall KD. "The Dynamics of Human Body
        Weight Change." *PLoS Comput Biol.* 2008;4(3):e1000045,
        glycogen and its associated water are, by definition, part of
        fat-free/lean mass -- so ``glycogen_g`` and
        ``total_body_water_kg`` are informational *breakdowns of what
        is already included in* ``lean_mass_kg``, not separate
        additive terms. ``fat_mass_kg + lean_mass_kg`` still sums to
        ``weight_kg`` exactly (see validator below); these two fields
        exist to explain *why* lean mass moved on short timescales
        (glycogen/water shifts) versus longer ones (structural tissue
        change).
    energy_intake_kcal:
        Total energy consumed during this timestep.
    energy_expenditure_kcal:
        Total energy expended during this timestep (i.e. TDEE for that
        period, inclusive of any adaptive thermogenesis adjustment).
    bmr_kcal, tdee_kcal:
        The BMR and TDEE components underlying
        ``energy_expenditure_kcal``, retained individually so reports
        can show the breakdown rather than only the total.
    adaptive_thermogenesis_kcal:
        The portion of ``energy_expenditure_kcal`` attributable to
        metabolic adaptation beyond what body-mass change alone would
        predict (Phase 11). Signed: negative values represent the
        commonly-observed adaptive *decrease* in expenditure during
        sustained energy deficit; defaults to 0.0 (no adaptation
        modeled yet).
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    day_index: int = Field(..., ge=0)
    date: date_type | None = None

    weight_kg: float = Field(..., gt=0.0)
    fat_mass_kg: float | None = Field(default=None, ge=0.0)
    lean_mass_kg: float | None = Field(default=None, ge=0.0)
    glycogen_g: float | None = Field(default=None, ge=0.0)
    total_body_water_kg: float | None = Field(default=None, ge=0.0)

    energy_intake_kcal: float = Field(..., ge=0.0)
    energy_expenditure_kcal: float = Field(..., ge=0.0)
    bmr_kcal: float | None = Field(default=None, ge=0.0)
    tdee_kcal: float | None = Field(default=None, ge=0.0)
    adaptive_thermogenesis_kcal: float = Field(default=0.0)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def energy_balance_kcal(self) -> float:
        """Net energy balance for this timestep.

        Positive values indicate a caloric surplus (intake exceeds
        expenditure); negative values indicate a deficit. This is the
        primary driver consumed by ``metabosim.models.energy_balance``
        (Phase 8) to compute the *next* state's mass change.
        """
        return self.energy_intake_kcal - self.energy_expenditure_kcal

    @model_validator(mode="after")
    def _check_composition_sums_to_weight(self) -> SimulationState:
        """When both ``fat_mass_kg`` and ``lean_mass_kg`` are provided,
        they must sum to ``weight_kg`` within
        ``_COMPOSITION_SUM_TOLERANCE_KG``. This catches a common and
        dangerous class of bug: a body-composition model and the
        weight-tracking model silently drifting out of sync over a
        multi-week simulation.
        """
        if self.fat_mass_kg is not None and self.lean_mass_kg is not None:
            implied_weight = self.fat_mass_kg + self.lean_mass_kg
            if abs(implied_weight - self.weight_kg) > _COMPOSITION_SUM_TOLERANCE_KG:
                raise ValueError(
                    "fat_mass_kg + lean_mass_kg "
                    f"({implied_weight:.3f} kg) does not match weight_kg "
                    f"({self.weight_kg:.3f} kg) within "
                    f"{_COMPOSITION_SUM_TOLERANCE_KG} kg tolerance."
                )
        return self
