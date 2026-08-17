"""
metabosim.visualization.trajectory
======================================

Matplotlib plotting of simulation time series: weight, body
composition (fat/lean mass), and glycogen trajectories over the
course of a simulation run.

Design conventions used throughout ``metabosim.visualization``
---------------------------------------------------------------------
Every plotting function in this package follows the same signature
pattern:

    def plot_x(..., ax: Axes | None = None, **kwargs) -> Axes:

If ``ax`` is provided, the function draws onto it and returns it
unchanged -- letting a caller compose multiple plots into one figure
via ``matplotlib.pyplot.subplots``. If ``ax`` is omitted, the function
creates its own ``Figure``/``Axes`` pair. Either way, the caller is
responsible for calling ``fig.savefig(...)``, ``plt.show()``, or
embedding the figure elsewhere -- **no function in this package calls
``plt.show()`` or otherwise assumes a display is available**, since
this is a reusable library, not a script; the accompanying test suite
runs entirely with Matplotlib's non-interactive ``Agg`` backend to
confirm this.

No scientific modeling lives here (or anywhere in
``metabosim.visualization``) -- every number plotted was already
computed by ``metabosim.simulation`` and extracted by
``metabosim.analysis``; this package only draws it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

from metabosim.analysis.series import (
    day_indices,
    fat_mass_series_kg,
    glycogen_series_g,
    lean_mass_series_kg,
    weight_series_kg,
)
from metabosim.domain.simulation_state import SimulationState

if TYPE_CHECKING:
    from matplotlib.axes import Axes


def _assert_all_present(values: list[float | None], context: str) -> list[float]:
    """Narrow a ``list[float | None]`` to ``list[float]`` at runtime,
    for series already known (via an earlier activation check) to
    have no ``None`` entries. Raises if that precondition is somehow
    violated, rather than silently plotting a gap."""
    if any(v is None for v in values):
        raise ValueError(
            f"{context} contains a None entry despite tracking being "
            "active on the first state -- this indicates inconsistent "
            "SimulationState data, not a normal untracked-series case."
        )
    return [v for v in values if v is not None]


def plot_weight_trajectory(
    states: list[SimulationState],
    ax: Axes | None = None,
    label: str = "Weight",
) -> Axes:
    """Plot body weight (kg) over simulated days.

    Parameters
    ----------
    states:
        A completed simulation's state history (``Simulator.run()``
        output).
    ax:
        An existing Matplotlib ``Axes`` to draw onto; a new
        ``Figure``/``Axes`` pair is created if omitted.
    label:
        Legend label for the plotted line.

    Returns
    -------
    Axes
        The axes the trajectory was drawn on.

    Raises
    ------
    ValueError
        If ``states`` is empty.
    """
    if not states:
        raise ValueError("states must contain at least one SimulationState.")
    if ax is None:
        _, ax = plt.subplots()

    ax.plot(day_indices(states), weight_series_kg(states), label=label)
    ax.set_xlabel("Day")
    ax.set_ylabel("Weight (kg)")
    ax.set_title("Body Weight Over Time")
    ax.legend()
    return ax


def plot_body_composition_trajectory(
    states: list[SimulationState],
    ax: Axes | None = None,
) -> Axes:
    """Plot fat mass and lean mass (kg) over simulated days.

    Parameters
    ----------
    states:
        A completed simulation's state history. Must have body
        composition tracking active (``fat_mass_kg``/``lean_mass_kg``
        populated) -- see ``metabosim.simulation.config`` module
        docstring for the activation rule.
    ax:
        An existing Matplotlib ``Axes`` to draw onto; a new
        ``Figure``/``Axes`` pair is created if omitted.

    Returns
    -------
    Axes
        The axes the trajectories were drawn on.

    Raises
    ------
    ValueError
        If ``states`` is empty, or if body composition wasn't tracked
        (``fat_mass_kg`` is ``None`` on the first state).
    """
    if not states:
        raise ValueError("states must contain at least one SimulationState.")
    if states[0].fat_mass_kg is None:
        raise ValueError(
            "states does not have body composition tracking active "
            "(fat_mass_kg is None) -- pass a Person with "
            "body_fat_percent set to metabosim.simulation.Simulator to "
            "enable it. See metabosim.simulation.config module docstring."
        )
    if ax is None:
        _, ax = plt.subplots()

    days = day_indices(states)
    ax.plot(
        days,
        _assert_all_present(fat_mass_series_kg(states), "fat_mass_series_kg"),
        label="Fat mass",
    )
    ax.plot(
        days,
        _assert_all_present(lean_mass_series_kg(states), "lean_mass_series_kg"),
        label="Lean mass",
    )
    ax.set_xlabel("Day")
    ax.set_ylabel("Mass (kg)")
    ax.set_title("Body Composition Over Time")
    ax.legend()
    return ax


def plot_glycogen_trajectory(
    states: list[SimulationState],
    ax: Axes | None = None,
) -> Axes:
    """Plot the glycogen store (grams) over simulated days -- useful
    for visualizing the short-term "water weight" transient described
    in ``metabosim.models.macronutrient.glycogen``.

    Parameters
    ----------
    states:
        A completed simulation's state history. Must have glycogen
        tracking active (``glycogen_g`` populated).
    ax:
        An existing Matplotlib ``Axes`` to draw onto; a new
        ``Figure``/``Axes`` pair is created if omitted.

    Returns
    -------
    Axes
        The axes the trajectory was drawn on.

    Raises
    ------
    ValueError
        If ``states`` is empty, or if glycogen wasn't tracked
        (``glycogen_g`` is ``None`` on the first state).
    """
    if not states:
        raise ValueError("states must contain at least one SimulationState.")
    if states[0].glycogen_g is None:
        raise ValueError(
            "states does not have glycogen tracking active (glycogen_g "
            "is None) -- pass initial_glycogen_g to "
            "metabosim.simulation.Simulator to enable it."
        )
    if ax is None:
        _, ax = plt.subplots()

    ax.plot(
        day_indices(states),
        _assert_all_present(glycogen_series_g(states), "glycogen_series_g"),
        label="Glycogen",
    )
    ax.set_xlabel("Day")
    ax.set_ylabel("Glycogen (g)")
    ax.set_title("Glycogen Store Over Time")
    ax.legend()
    return ax
