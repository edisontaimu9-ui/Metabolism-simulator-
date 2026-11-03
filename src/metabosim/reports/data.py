"""
metabosim.reports.data
=========================

``ReportData``: the single, validated bundle of everything a report
needs -- the subject, the configuration, the diet/activity plan(s),
the full state history, and its headline summary.

Why a bundle exists at all
---------------------------------------------------------------------
A ``list[SimulationState]`` alone does not say *who* was simulated,
*which models* produced it, or *what they ate*. A report that omitted
those would be a set of numbers without provenance. ``Simulator``
already holds all of those inputs, so ``build_report_data`` reads them
from the simulator directly instead of asking the caller to pass the
same objects a second time (and risk passing a mismatched set).

Contains no scientific modeling and no citations apply; it only
assembles and validates already-computed data.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator

from metabosim.analysis.summary import SimulationSummary, summarize
from metabosim.domain.person import Person
from metabosim.domain.simulation_state import SimulationState
from metabosim.simulation.config import DailyPlan, SimulationConfig
from metabosim.simulation.engine import Simulator

DEFAULT_REPORT_TITLE: str = "Metabolism Simulation Report"


class ReportData(BaseModel):
    """Everything needed to render one simulation report.

    Attributes
    ----------
    title:
        Report title.
    person:
        The subject's starting profile.
    config:
        The model-selection configuration the run used.
    daily_plans:
        One ``DailyPlan`` per simulated day (length ``config.days``).
    states:
        The full state history (length ``config.days + 1``; see
        ``metabosim.simulation.engine`` for the row convention).
    summary:
        Headline statistics, computed from ``states``.
    initial_glycogen_g:
        The starting glycogen store if glycogen tracking was active,
        else ``None``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    title: str = DEFAULT_REPORT_TITLE
    person: Person
    config: SimulationConfig
    daily_plans: list[DailyPlan]
    states: list[SimulationState]
    summary: SimulationSummary
    initial_glycogen_g: float | None = None

    @model_validator(mode="after")
    def _check_lengths_are_consistent(self) -> ReportData:
        """Fail fast if the plans or states do not match ``config.days``
        (e.g. a state history from a different run than the config)."""
        days = self.config.days
        if len(self.states) != days + 1:
            raise ValueError(
                f"states has {len(self.states)} entries but config.days="
                f"{days} implies {days + 1} (see metabosim.simulation.engine "
                "row convention)."
            )
        if len(self.daily_plans) != days:
            raise ValueError(
                f"daily_plans has {len(self.daily_plans)} entries but "
                f"config.days={days}."
            )
        return self

    @property
    def plan_is_uniform(self) -> bool:
        """``True`` if every simulated day used an identical plan."""
        first = self.daily_plans[0]
        return all(plan == first for plan in self.daily_plans)


def build_report_data(
    simulator: Simulator,
    states: list[SimulationState],
    title: str | None = None,
) -> ReportData:
    """Assemble ``ReportData`` from a ``Simulator`` and its output.

    Parameters
    ----------
    simulator:
        The simulator that produced ``states``. Its person, config,
        daily plans, and initial glycogen are read directly.
    states:
        The result of ``simulator.run()``.
    title:
        Optional report title. Defaults to
        ``"Metabolism Simulation Report"``, with the subject's name
        appended if ``Person.name`` is set.

    Raises
    ------
    ValueError
        If ``states`` is empty, or does not match the simulator's
        configured number of days.
    """
    if title is None:
        name = simulator.person.name
        title = f"{DEFAULT_REPORT_TITLE}: {name}" if name else DEFAULT_REPORT_TITLE
    return ReportData(
        title=title,
        person=simulator.person,
        config=simulator.config,
        daily_plans=simulator.daily_plans,
        states=states,
        summary=summarize(states),
        initial_glycogen_g=simulator.initial_glycogen_g,
    )
