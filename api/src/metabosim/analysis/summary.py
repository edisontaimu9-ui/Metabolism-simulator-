"""
metabosim.analysis.summary
==============================

Computes a small set of headline summary statistics from a completed
simulation's state history -- the kind of numbers a chart title, a
report header (Phase 16), or a quick console printout would want,
without needing to re-derive them from the raw series each time.

Like ``metabosim.analysis.series``, this contains no scientific
modeling -- only arithmetic over already-computed simulation output.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from metabosim.domain.simulation_state import SimulationState


class SimulationSummary(BaseModel):
    """Headline statistics for a completed simulation run.

    Attributes
    ----------
    days_simulated:
        Number of simulated days (``len(states) - 1``; see
        ``metabosim.simulation.engine`` for the row convention).
    starting_weight_kg, ending_weight_kg:
        Weight at the first and last state.
    total_weight_change_kg:
        ``ending_weight_kg - starting_weight_kg``. Positive for a net
        gain, negative for a net loss.
    average_daily_rate_kg:
        ``total_weight_change_kg / days_simulated``. ``0.0`` if
        ``days_simulated`` is ``0``.
    average_daily_energy_balance_kcal:
        Mean of ``energy_balance_kcal`` across all simulated days
        (excludes the final report-only state -- see
        ``metabosim.simulation.engine`` module docstring's row
        convention).
    tracked_body_composition:
        Whether ``fat_mass_kg``/``lean_mass_kg`` were populated (i.e.
        Phase 10 tracking was active for this run).
    tracked_glycogen:
        Whether ``glycogen_g`` was populated (i.e. Phase 12 tracking
        was active for this run).
    """

    model_config = ConfigDict(frozen=True)

    days_simulated: int
    starting_weight_kg: float
    ending_weight_kg: float
    total_weight_change_kg: float
    average_daily_rate_kg: float
    average_daily_energy_balance_kcal: float
    tracked_body_composition: bool
    tracked_glycogen: bool


def summarize(states: list[SimulationState]) -> SimulationSummary:
    """Compute headline summary statistics for a completed simulation.

    Parameters
    ----------
    states:
        The full state history from ``Simulator.run()``. Must contain
        at least one state.

    Returns
    -------
    SimulationSummary

    Raises
    ------
    ValueError
        If ``states`` is empty.
    """
    if not states:
        raise ValueError("states must contain at least one SimulationState.")

    days_simulated = len(states) - 1
    starting_weight_kg = states[0].weight_kg
    ending_weight_kg = states[-1].weight_kg
    total_weight_change_kg = ending_weight_kg - starting_weight_kg
    average_daily_rate_kg = (
        total_weight_change_kg / days_simulated if days_simulated > 0 else 0.0
    )

    # Exclude the final report-only state from the energy-balance
    # average, per the row convention documented on SimulationSummary.
    balance_states = states[:-1] if days_simulated > 0 else states
    average_daily_energy_balance_kcal = sum(
        state.energy_balance_kcal for state in balance_states
    ) / len(balance_states)

    return SimulationSummary(
        days_simulated=days_simulated,
        starting_weight_kg=starting_weight_kg,
        ending_weight_kg=ending_weight_kg,
        total_weight_change_kg=total_weight_change_kg,
        average_daily_rate_kg=average_daily_rate_kg,
        average_daily_energy_balance_kcal=average_daily_energy_balance_kcal,
        tracked_body_composition=states[0].fat_mass_kg is not None,
        tracked_glycogen=states[0].glycogen_g is not None,
    )
