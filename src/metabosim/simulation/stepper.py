"""
metabosim.simulation.stepper
===============================

The single-timestep state transition: given a subject's current
weight (and, optionally, current fat mass), a day's diet + activity
plan, and a ``SimulationConfig``, compute that day's
``SimulationState`` plus the mass-change rate (and, if tracking body
composition, the next fat/lean mass split) to apply to obtain
tomorrow's state.

This is a pure function, independent of ``metabosim.simulation.engine``,
so it can be unit-tested in complete isolation from the day-by-day
looping logic -- per this project's "every module must be
independently testable" standard.

Body composition tracking (Phase 10)
---------------------------------------------------------------------
Whether this step tracks fat/lean mass is determined entirely by
whether the caller passes ``current_fat_mass_kg`` (not ``None``) --
see ``metabosim.simulation.config`` module docstring for the full
rationale and the exact activation rule used by
``metabosim.simulation.engine.Simulator``. When tracking:

1. The ``Person`` copy used for this day's BMR calculation gets an
   updated ``body_fat_percent`` (derived from ``current_fat_mass_kg``
   and ``current_weight_kg``), not just an updated ``weight_kg`` --
   so body-composition-aware BMR equations (Katch-McArdle, Cunningham)
   reflect the subject's *current* composition, not their initial one.
2. The energy balance calculation uses a fresh
   ``TissueEnergyDensityModel`` constructed with an
   ``ffm_fraction`` computed *for this day's current fat mass* via
   ``metabosim.models.body_composition``, instead of that model's
   static 0.25 default -- this only applies when
   ``config.energy_balance_model_id == "tissue_energy_density"``,
   since the other registered energy balance models have no
   ``ffm_fraction`` concept to override.
3. The day's total mass change is itself partitioned into fat and lean
   components (via the same body composition model, guaranteeing
   consistency with step 2's fraction), producing the next day's fat
   and lean mass.

Adaptive thermogenesis (Phase 11)
---------------------------------------------------------------------
After computing the naive predicted TDEE (real BMR + activity + TEF,
via ``calculate_tdee_from_components``), this step applies
``config.adaptive_thermogenesis_model_id``'s adjustment on top of it:

    effective_expenditure_kcal = tdee_result.tdee_kcal + adaptation_kcal

``SimulationState.tdee_kcal`` retains the *naive* (unadjusted)
prediction for transparency/comparison; ``energy_expenditure_kcal``
(which drives the day's actual energy balance and mass change) and
``adaptive_thermogenesis_kcal`` both reflect the adjustment -- this is
exactly the relationship anticipated by
``metabosim.domain.simulation_state.SimulationState``'s field
docstrings since Phase 3. The default model (``"none"``) always
returns zero, so ``energy_expenditure_kcal`` equals ``tdee_kcal``
unless a different model is explicitly configured.
"""

from __future__ import annotations

from datetime import date as date_type
from typing import NamedTuple

from metabosim.domain.person import Person
from metabosim.domain.simulation_state import SimulationState
from metabosim.models.adaptive_thermogenesis.registry import (
    get_model as get_adaptive_thermogenesis_model,
)
from metabosim.models.body_composition.registry import (
    get_model as get_body_composition_model,
)
from metabosim.models.energy_balance.registry import (
    get_model as get_energy_balance_model,
)
from metabosim.models.energy_balance.tissue_energy_density import (
    TissueEnergyDensityModel,
)
from metabosim.models.tdee.calculator import calculate_tdee_from_components
from metabosim.simulation.config import DailyPlan, SimulationConfig


class StepResult(NamedTuple):
    """The output of a single call to :func:`step`.

    Attributes
    ----------
    state:
        This day's computed ``SimulationState``.
    mass_change_rate_kg_per_day:
        The total mass-change rate (kg/day) to add to the current
        weight to obtain the next day's starting weight.
    next_fat_mass_kg, next_lean_mass_kg:
        The next day's fat mass and lean mass, if body composition is
        being tracked (see module docstring); both ``None`` otherwise.
        When not ``None``, they always sum to
        ``current_weight_kg + mass_change_rate_kg_per_day`` (up to
        floating-point rounding).
    """

    state: SimulationState
    mass_change_rate_kg_per_day: float
    next_fat_mass_kg: float | None
    next_lean_mass_kg: float | None


def step(
    current_weight_kg: float,
    baseline_weight_kg: float,
    person_template: Person,
    day_index: int,
    plan: DailyPlan,
    config: SimulationConfig,
    state_date: date_type | None = None,
    current_fat_mass_kg: float | None = None,
) -> StepResult:
    """Compute one day's ``SimulationState`` and the information
    needed to advance to the next day.

    Parameters
    ----------
    current_weight_kg:
        The subject's weight at the start of this simulated day.
    baseline_weight_kg:
        The subject's weight at day 0 of the overall simulation (used
        only to compute ``excess_weight_kg`` for energy balance models
        whose rate depends on accumulated change; the default
        ``"tissue_energy_density"`` model ignores it -- see
        ``metabosim.models.energy_balance.tissue_energy_density``).
    person_template:
        The subject's profile (sex, age, height, activity_level,
        etc.). Its ``weight_kg`` (and, if tracking body composition,
        ``body_fat_percent``) is overridden for this day's BMR
        calculation; every other field is used as-is.
        Note: ``person_template.activity_level`` is NOT consulted --
        see ``metabosim.simulation.config`` module docstring.
    day_index:
        This day's zero-based index within the overall simulation.
    plan:
        This day's diet and logged activity.
    config:
        The simulation's model-selection configuration.
    state_date:
        Optional calendar date to embed in the returned state.
    current_fat_mass_kg:
        The subject's fat mass at the start of this simulated day, if
        body composition is being tracked; ``None`` otherwise (the
        Phase 9 behavior). See module docstring.

    Returns
    -------
    StepResult
        This day's state, the mass-change rate, and (if tracking body
        composition) the next day's fat/lean mass split.

    Raises
    ------
    ValueError
        If ``config.energy_balance_model_id`` resolves to a model with
        ``includes_weight_dependent_feedback = True`` (would
        double-count the feedback this stepper's real per-day BMR
        recompute already supplies). In normal use this is caught
        earlier, at ``SimulationConfig`` construction time; this check
        is defense-in-depth for callers who bypass that validation.
    KeyError
        If any configured model ID is not registered.
    """
    energy_balance_model = get_energy_balance_model(config.energy_balance_model_id)
    if energy_balance_model.includes_weight_dependent_feedback:
        raise ValueError(
            f"Energy balance model {energy_balance_model.name!r} already "
            "implicitly includes weight-dependent expenditure feedback "
            "(its includes_weight_dependent_feedback attribute is True). "
            "This simulator recomputes real BMR/TDEE at each day's "
            "updated weight, which already supplies that feedback from "
            "actual physiology -- combining both would double-count it. "
            "Use energy_balance_model_id='tissue_energy_density' instead."
        )

    track_composition = current_fat_mass_kg is not None

    person_updates: dict[str, float] = {"weight_kg": current_weight_kg}
    current_lean_mass_kg: float | None = None
    if track_composition:
        assert current_fat_mass_kg is not None  # narrows type for mypy
        current_lean_mass_kg = current_weight_kg - current_fat_mass_kg
        person_updates["body_fat_percent"] = (
            current_fat_mass_kg / current_weight_kg
        ) * 100.0

    current_person = person_template.model_copy(update=person_updates)

    tdee_result = calculate_tdee_from_components(
        current_person,
        plan.macros,
        bmr_model_id=config.bmr_model_id,
        activity_model_kwargs={"entries": plan.activity_entries},
        tef_model_id=config.tef_model_id,
    )

    # Adaptive thermogenesis (Phase 11): an additional adjustment to
    # expenditure, beyond what real BMR recompute already captures,
    # scaled against the naive predicted TDEE (tdee_result.tdee_kcal)
    # -- see metabosim.models.adaptive_thermogenesis.base for the
    # three-model framework and metabosim.simulation.config for why
    # "none" (zero adjustment) is the default.
    adaptive_thermogenesis_model = get_adaptive_thermogenesis_model(
        config.adaptive_thermogenesis_model_id
    )
    adaptive_thermogenesis_kcal = (
        adaptive_thermogenesis_model.calculate_adjustment_kcal(
            baseline_weight_kg, current_weight_kg, tdee_result.tdee_kcal
        )
    )
    effective_expenditure_kcal = tdee_result.tdee_kcal + adaptive_thermogenesis_kcal

    intake_kcal = plan.macros.energy_kcal
    balance_kcal = intake_kcal - effective_expenditure_kcal

    state = SimulationState(
        day_index=day_index,
        date=state_date,
        weight_kg=current_weight_kg,
        fat_mass_kg=current_fat_mass_kg,
        lean_mass_kg=current_lean_mass_kg,
        energy_intake_kcal=intake_kcal,
        energy_expenditure_kcal=effective_expenditure_kcal,
        bmr_kcal=tdee_result.bmr_kcal,
        tdee_kcal=tdee_result.tdee_kcal,
        adaptive_thermogenesis_kcal=adaptive_thermogenesis_kcal,
    )

    excess_weight_kg = current_weight_kg - baseline_weight_kg

    # Use a dynamically-parameterized TissueEnergyDensityModel when
    # tracking body composition and the configured energy balance
    # model actually has an ffm_fraction concept to override -- see
    # module docstring, point 2.
    rate_energy_balance_model = energy_balance_model
    body_composition_model = None
    if track_composition and config.energy_balance_model_id == "tissue_energy_density":
        assert current_fat_mass_kg is not None  # narrows type for mypy
        body_composition_model = get_body_composition_model(
            config.body_composition_model_id
        )
        ffm_fraction = body_composition_model.ffm_fraction_of_change(
            current_fat_mass_kg, current_person.sex
        )
        rate_energy_balance_model = TissueEnergyDensityModel(ffm_fraction=ffm_fraction)

    rate_kg_per_day = rate_energy_balance_model.mass_change_rate_kg_per_day(
        balance_kcal, excess_weight_kg
    )

    next_fat_mass_kg: float | None = None
    next_lean_mass_kg: float | None = None
    if track_composition:
        assert current_fat_mass_kg is not None  # narrows type for mypy
        assert current_lean_mass_kg is not None
        if body_composition_model is None:
            body_composition_model = get_body_composition_model(
                config.body_composition_model_id
            )
        delta_fat_kg, delta_lean_kg = body_composition_model.partition_mass_change_kg(
            rate_kg_per_day, current_fat_mass_kg, current_person.sex
        )
        next_fat_mass_kg = current_fat_mass_kg + delta_fat_kg
        next_lean_mass_kg = current_lean_mass_kg + delta_lean_kg

    return StepResult(
        state=state,
        mass_change_rate_kg_per_day=rate_kg_per_day,
        next_fat_mass_kg=next_fat_mass_kg,
        next_lean_mass_kg=next_lean_mass_kg,
    )
