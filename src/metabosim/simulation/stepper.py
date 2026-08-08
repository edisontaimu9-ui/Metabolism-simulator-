"""
metabosim.simulation.stepper
===============================

The single-timestep state transition: given a subject's current
weight, a day's diet + activity plan, and a ``SimulationConfig``,
compute that day's ``SimulationState`` plus the mass-change rate to
apply to obtain tomorrow's weight.

This is a pure function, independent of ``metabosim.simulation.engine``,
so it can be unit-tested in complete isolation from the day-by-day
looping logic -- per this project's "every module must be
independently testable" standard.
"""

from __future__ import annotations

from datetime import date as date_type

from metabosim.domain.person import Person
from metabosim.domain.simulation_state import SimulationState
from metabosim.models.energy_balance.registry import (
    get_model as get_energy_balance_model,
)
from metabosim.models.tdee.calculator import calculate_tdee_from_components
from metabosim.simulation.config import DailyPlan, SimulationConfig


def step(
    current_weight_kg: float,
    baseline_weight_kg: float,
    person_template: Person,
    day_index: int,
    plan: DailyPlan,
    config: SimulationConfig,
    state_date: date_type | None = None,
) -> tuple[SimulationState, float]:
    """Compute one day's ``SimulationState`` and the mass-change rate
    to apply to reach the next day's weight.

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
        etc.). Its ``weight_kg`` is overridden with
        ``current_weight_kg`` for this day's BMR calculation; every
        other field is used as-is.
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

    Returns
    -------
    tuple[SimulationState, float]
        The computed state for this day, and the mass-change rate
        (kg/day) to add to ``current_weight_kg`` to obtain the next
        day's starting weight.

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

    current_person = person_template.model_copy(update={"weight_kg": current_weight_kg})

    tdee_result = calculate_tdee_from_components(
        current_person,
        plan.macros,
        bmr_model_id=config.bmr_model_id,
        activity_model_kwargs={"entries": plan.activity_entries},
        tef_model_id=config.tef_model_id,
    )

    intake_kcal = plan.macros.energy_kcal
    balance_kcal = intake_kcal - tdee_result.tdee_kcal

    state = SimulationState(
        day_index=day_index,
        date=state_date,
        weight_kg=current_weight_kg,
        energy_intake_kcal=intake_kcal,
        energy_expenditure_kcal=tdee_result.tdee_kcal,
        bmr_kcal=tdee_result.bmr_kcal,
        tdee_kcal=tdee_result.tdee_kcal,
    )

    excess_weight_kg = current_weight_kg - baseline_weight_kg
    rate_kg_per_day = energy_balance_model.mass_change_rate_kg_per_day(
        balance_kcal, excess_weight_kg
    )

    return state, rate_kg_per_day
