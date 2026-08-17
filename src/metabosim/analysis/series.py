"""
metabosim.analysis.series
============================

Read-only extraction of plain numeric time series from a
``list[SimulationState]`` history, for consumption by
``metabosim.visualization`` (and, later, ``metabosim.reports``).

Scope note
------------
``docs/architecture.md``'s original Phase 1 folder plan described an
``analysis/`` package ("post-hoc statistics on simulation output") as
part of the project's layered design, but the 18-phase roadmap itself
has no dedicated numbered phase for it -- Phase 15 (Visualization)
depends on it directly, so this minimal support module is built now,
as infrastructure for that phase, rather than as its own phase. It
contains no scientific modeling of any kind (no citations apply) --
only straightforward numeric extraction and a simple moving average,
consistent with the "produces figures only, no calculation logic"
boundary ``docs/architecture.md`` draws for ``visualization`` itself:
the *data* transformations needed to make good charts live here, one
layer below the plotting code.

This package never mutates the ``SimulationState`` history it reads;
all functions here are pure functions of their inputs.
"""

from __future__ import annotations

from metabosim.domain.simulation_state import SimulationState


def day_indices(states: list[SimulationState]) -> list[int]:
    """Extract the ``day_index`` of each state, in order."""
    return [state.day_index for state in states]


def weight_series_kg(states: list[SimulationState]) -> list[float]:
    """Extract ``weight_kg`` from each state, in order."""
    return [state.weight_kg for state in states]


def fat_mass_series_kg(states: list[SimulationState]) -> list[float | None]:
    """Extract ``fat_mass_kg`` from each state, in order. Entries are
    ``None`` for any state where body composition wasn't tracked."""
    return [state.fat_mass_kg for state in states]


def lean_mass_series_kg(states: list[SimulationState]) -> list[float | None]:
    """Extract ``lean_mass_kg`` from each state, in order. Entries are
    ``None`` for any state where body composition wasn't tracked."""
    return [state.lean_mass_kg for state in states]


def glycogen_series_g(states: list[SimulationState]) -> list[float | None]:
    """Extract ``glycogen_g`` from each state, in order. Entries are
    ``None`` for any state where glycogen wasn't tracked."""
    return [state.glycogen_g for state in states]


def energy_intake_series_kcal(states: list[SimulationState]) -> list[float]:
    """Extract ``energy_intake_kcal`` from each state, in order."""
    return [state.energy_intake_kcal for state in states]


def energy_expenditure_series_kcal(states: list[SimulationState]) -> list[float]:
    """Extract ``energy_expenditure_kcal`` from each state, in order."""
    return [state.energy_expenditure_kcal for state in states]


def energy_balance_series_kcal(states: list[SimulationState]) -> list[float]:
    """Extract the computed ``energy_balance_kcal`` from each state,
    in order (positive = surplus, negative = deficit)."""
    return [state.energy_balance_kcal for state in states]


def moving_average(values: list[float], window: int) -> list[float]:
    """A simple trailing moving average.

    Each output element ``i`` is the mean of
    ``values[max(0, i-window+1):i+1]`` -- i.e. it uses fewer than
    ``window`` points near the start of the series rather than
    producing ``NaN`` or truncating the output's length, so the
    returned list is always the same length as ``values``.

    Parameters
    ----------
    values:
        The series to smooth.
    window:
        The trailing window size. Must be a positive integer.

    Returns
    -------
    list[float]
        The smoothed series, same length as ``values``.

    Raises
    ------
    ValueError
        If ``window`` is not a positive integer.
    """
    if window <= 0:
        raise ValueError(f"window must be a positive integer; received {window!r}.")
    result: list[float] = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        chunk = values[start : i + 1]
        result.append(sum(chunk) / len(chunk))
    return result
