"""
metabosim.visualization.energy
==================================

Matplotlib plotting of energy intake, expenditure, and balance over
the course of a simulation run. See
``metabosim.visualization.trajectory`` module docstring for the
shared ``ax=None`` composability convention used throughout this
package.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

from metabosim.analysis.series import (
    day_indices,
    energy_balance_series_kcal,
    energy_expenditure_series_kcal,
    energy_intake_series_kcal,
    moving_average,
)
from metabosim.domain.simulation_state import SimulationState

if TYPE_CHECKING:
    from matplotlib.axes import Axes


def plot_energy_intake_vs_expenditure(
    states: list[SimulationState],
    ax: Axes | None = None,
) -> Axes:
    """Plot daily energy intake and expenditure (kcal) over simulated
    days, on the same axes for direct visual comparison.

    Parameters
    ----------
    states:
        A completed simulation's state history.
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
        If ``states`` is empty.
    """
    if not states:
        raise ValueError("states must contain at least one SimulationState.")
    if ax is None:
        _, ax = plt.subplots()

    days = day_indices(states)
    ax.plot(days, energy_intake_series_kcal(states), label="Intake")
    ax.plot(days, energy_expenditure_series_kcal(states), label="Expenditure")
    ax.set_xlabel("Day")
    ax.set_ylabel("Energy (kcal/day)")
    ax.set_title("Energy Intake vs. Expenditure")
    ax.legend()
    return ax


def plot_energy_balance(
    states: list[SimulationState],
    ax: Axes | None = None,
    smoothing_window: int | None = None,
) -> Axes:
    """Plot net daily energy balance (kcal, intake minus expenditure)
    over simulated days, as a bar chart with a zero reference line.

    Parameters
    ----------
    states:
        A completed simulation's state history.
    ax:
        An existing Matplotlib ``Axes`` to draw onto; a new
        ``Figure``/``Axes`` pair is created if omitted.
    smoothing_window:
        If provided, also overlay a trailing moving average (see
        ``metabosim.analysis.series.moving_average``) with this
        window size -- useful for seeing the underlying trend through
        short-term noise (e.g. a Phase 12 glycogen transient) without
        losing the raw daily bars.

    Returns
    -------
    Axes
        The axes the chart was drawn on.

    Raises
    ------
    ValueError
        If ``states`` is empty, or if ``smoothing_window`` is not a
        positive integer (when provided).
    """
    if not states:
        raise ValueError("states must contain at least one SimulationState.")
    if ax is None:
        _, ax = plt.subplots()

    days = day_indices(states)
    balance = energy_balance_series_kcal(states)

    colors = ["tab:green" if b >= 0 else "tab:red" for b in balance]
    ax.bar(days, balance, color=colors, alpha=0.6, label="Daily balance")
    ax.axhline(0.0, color="black", linewidth=0.8)

    if smoothing_window is not None:
        smoothed = moving_average(balance, smoothing_window)
        ax.plot(
            days,
            smoothed,
            color="tab:blue",
            linewidth=2,
            label=f"{smoothing_window}-day average",
        )

    ax.set_xlabel("Day")
    ax.set_ylabel("Energy Balance (kcal/day)")
    ax.set_title("Daily Energy Balance")
    ax.legend()
    return ax
