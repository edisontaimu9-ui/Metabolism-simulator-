"""
metabosim.analysis
=====================

Read-only, post-hoc analysis of completed simulation output. Operates
only on the ``list[SimulationState]`` history produced by
``metabosim.simulation``; never mutates it. Contains no scientific
modeling of its own (no citations apply to this package) -- only
straightforward numeric extraction and summary statistics, built as
supporting infrastructure for ``metabosim.visualization`` (Phase 15).
See ``metabosim.analysis.series`` module docstring for the scope note
on why this package exists without its own numbered roadmap phase.

  - ``series``  -- pure extraction functions (weight, fat/lean mass,
    glycogen, energy intake/expenditure/balance) plus a simple moving
    average for smoothing short-term noise (e.g. Phase 12's glycogen
    transients) when plotting longer-run trends.
  - ``summary`` -- ``summarize()`` / ``SimulationSummary``: headline
    statistics (total change, average daily rate, tracked-features
    flags) for a completed run.

Example
-------
>>> from metabosim.analysis import summarize, weight_series_kg
>>> # `states` would normally come from Simulator(...).run()
"""

from metabosim.analysis.series import (
    day_indices,
    energy_balance_series_kcal,
    energy_expenditure_series_kcal,
    energy_intake_series_kcal,
    fat_mass_series_kg,
    glycogen_series_g,
    lean_mass_series_kg,
    moving_average,
    weight_series_kg,
)
from metabosim.analysis.summary import SimulationSummary, summarize

__all__ = [
    "SimulationSummary",
    "day_indices",
    "energy_balance_series_kcal",
    "energy_expenditure_series_kcal",
    "energy_intake_series_kcal",
    "fat_mass_series_kg",
    "glycogen_series_g",
    "lean_mass_series_kg",
    "moving_average",
    "summarize",
    "weight_series_kg",
]
