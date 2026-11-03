"""
metabosim.validation.yoo2018
===============================

Plausibility check against the published worked example in Yoo S.
"Dynamic Energy Balance and Obesity Prevention." J Obes Metab Syndr.
2018;27(4):203-212: a 100 kg sedentary male at a sustained deficit of
500 kcal/day approaches a steady-state weight of about 75 kg.

What this check does and does not show
---------------------------------------------------------------------
The source specifies only the starting weight, sex, activity category,
and the deficit. Age, height, and the actual activity energy are NOT
specified, and the simulator needs them. This module therefore
*assumes* a scenario (a 40 year old, 175 cm male with 3 MET for 4
hours of logged activity per day, giving a maintenance expenditure of
roughly 2900 kcal/day) and checks that the long-run steady state lands
within a wide band around 75 kg.

That makes this a plausibility check, not a precise fit: it would catch
a model whose weight-dependent expenditure feedback is badly wrong
(for example, one that never plateaus, or plateaus far from 75 kg), but
it cannot distinguish small differences. The band (plus or minus 5 kg)
reflects that unspecified-input uncertainty. Note also that without
logged activity the same deficit drives this simulator to a much lower
weight, because activity energy is the main weight-proportional
expenditure term besides BMR; the logged-activity assumption matters.

Contains no model logic of its own; only runs the existing simulator.
"""

from __future__ import annotations

from metabosim.domain.diet import MacronutrientGrams
from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.models.activity.met_based import ActivityEntry
from metabosim.simulation.config import DailyPlan, SimulationConfig
from metabosim.simulation.engine import Simulator
from metabosim.validation.reference import ValidationResult, check_value

CITATION: str = (
    'Yoo S. "Dynamic Energy Balance and Obesity Prevention." J Obes Metab '
    "Syndr. 2018;27(4):203-212."
)
EXPECTED_STEADY_STATE_KG: float = 75.0
TOLERANCE_KG: float = 5.0
DEFICIT_KCAL: float = 500.0
SIMULATED_DAYS: int = 3650
#: A trajectory counts as settled if weight moved less than this over
#: the final year.
SETTLED_CHANGE_KG: float = 0.5

_ASSUMED_PERSON = Person(sex=Sex.MALE, age_years=40, height_cm=175, weight_kg=100)
_ASSUMED_ACTIVITY = [ActivityEntry(met=3.0, duration_hours=4.0)]
_BASE_MACROS = MacronutrientGrams(protein_g=100, carbohydrate_g=250, fat_g=80)


def _plan_for_intake(intake_kcal: float) -> DailyPlan:
    """The base macronutrient mix, scaled to the requested intake."""
    scale = intake_kcal / _BASE_MACROS.energy_kcal
    macros = MacronutrientGrams(
        protein_g=_BASE_MACROS.protein_g * scale,
        carbohydrate_g=_BASE_MACROS.carbohydrate_g * scale,
        fat_g=_BASE_MACROS.fat_g * scale,
    )
    return DailyPlan(macros=macros, activity_entries=list(_ASSUMED_ACTIVITY))


def run_yoo_2018_check(days: int = SIMULATED_DAYS) -> list[ValidationResult]:
    """Run the Yoo (2018) plausibility check.

    Maintenance expenditure is measured from a one-day run at the
    starting weight, then intake is set 500 kcal below it and the
    simulation is run for ``days``. Returns two results: whether the
    final weight is within the band around 75 kg, and whether the
    trajectory had settled (changed by less than ``SETTLED_CHANGE_KG``
    over the final year).

    Raises
    ------
    ValueError
        If ``days`` is shorter than 730 (a settled check needs at
        least a year of trajectory after the first year).
    """
    if days < 730:
        raise ValueError("days must be at least 730 for a steady-state check.")

    probe = Simulator(
        _ASSUMED_PERSON, SimulationConfig(days=1), _plan_for_intake(2500.0)
    ).run()[0]
    maintenance_kcal = probe.energy_expenditure_kcal

    states = Simulator(
        _ASSUMED_PERSON,
        SimulationConfig(days=days),
        _plan_for_intake(maintenance_kcal - DEFICIT_KCAL),
    ).run()

    final_weight = states[-1].weight_kg
    last_year_change = abs(states[-1].weight_kg - states[-366].weight_kg)
    scenario = (
        f"Assumed scenario: 40 y male, 175 cm, 100 kg, maintenance "
        f"{maintenance_kcal:.0f} kcal/day, intake {DEFICIT_KCAL:.0f} kcal "
        "below it. Source: " + CITATION
    )
    return [
        check_value(
            name="yoo_2018_steady_state_weight",
            observed=final_weight,
            expected=EXPECTED_STEADY_STATE_KG,
            tolerance=TOLERANCE_KG,
            unit="kg",
            detail=scenario,
        ),
        check_value(
            name="yoo_2018_trajectory_settled",
            observed=last_year_change,
            expected=0.0,
            tolerance=SETTLED_CHANGE_KG,
            unit="kg change over final year",
            detail="Weight should plateau, not keep falling.",
        ),
    ]
