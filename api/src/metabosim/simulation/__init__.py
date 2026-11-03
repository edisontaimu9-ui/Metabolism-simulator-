"""
metabosim.simulation
=======================

Orchestration layer: the day-by-day body weight simulation engine.

  - ``config``  -- ``DailyPlan`` (one day's diet + logged activity) and
    ``SimulationConfig`` (which model strategies to use, how many
    days to run). ``SimulationConfig`` validates eagerly at
    construction time that the chosen energy balance model won't
    double-count weight-dependent expenditure feedback against this
    engine's own real per-day BMR recompute.
  - ``stepper`` -- ``step()``, the pure single-timestep transition
    function: current weight + a day's plan + config -> that day's
    ``SimulationState`` + the mass-change rate to apply next.
  - ``engine``  -- ``Simulator``, which repeatedly calls ``step()`` to
    produce a full ``list[SimulationState]`` history.

This module finally assembles the components built in Phases 4-8
(BMR, TDEE, TEF, Activity, Energy Balance) into an actual time-varying
simulation, recomputing real BMR/TDEE at each day's updated weight --
which is what supplies weight-dependent expenditure feedback from
genuine physiology, rather than an approximated constant. See
``metabosim.models.energy_balance.base`` and
``metabosim.simulation.config`` module docstrings for why this
matters and how double-counting is prevented.

Example
-------
>>> from metabosim.domain import MacronutrientGrams, Person, Sex
>>> from metabosim.models.activity import ActivityEntry
>>> from metabosim.simulation import DailyPlan, Simulator, SimulationConfig
>>> person = Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=80)
>>> macros = MacronutrientGrams(
...     protein_g=150, carbohydrate_g=300, fat_g=80, fiber_g=30,
... )
>>> entries = [ActivityEntry(met=6.0, duration_hours=1.0)]
>>> plan = DailyPlan(macros=macros, activity_entries=entries)
>>> config = SimulationConfig(days=30)
>>> states = Simulator(person, config, plan).run()
>>> len(states)
31
>>> round(states[0].weight_kg, 2)
80.0
>>> states[-1].weight_kg > states[0].weight_kg
True
"""

from metabosim.simulation.config import (
    DEFAULT_ENERGY_BALANCE_MODEL_ID,
    DailyPlan,
    SimulationConfig,
)
from metabosim.simulation.engine import Simulator
from metabosim.simulation.stepper import step

__all__ = [
    "DEFAULT_ENERGY_BALANCE_MODEL_ID",
    "DailyPlan",
    "SimulationConfig",
    "Simulator",
    "step",
]
