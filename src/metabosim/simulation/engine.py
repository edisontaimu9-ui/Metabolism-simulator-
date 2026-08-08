"""
metabosim.simulation.engine
==============================

``Simulator``: runs a day-by-day body weight simulation by repeatedly
calling ``metabosim.simulation.stepper.step``, producing a full
history of ``SimulationState`` objects -- the single artifact that
``metabosim.analysis``, ``metabosim.visualization``, and
``metabosim.reports`` will consume downstream (Phases 15-16), per
``docs/architecture.md``'s data-flow design.

Row convention
----------------
A simulation configured for ``config.days`` days produces
``config.days + 1`` states, indexed 0 through ``config.days``
inclusive:

- State ``i``'s ``weight_kg`` is the subject's weight at the *start*
  of simulated day ``i`` (state 0's weight is the subject's original
  starting weight, unchanged).
- State ``i``'s ``energy_intake_kcal`` / ``energy_expenditure_kcal`` /
  ``bmr_kcal`` / ``tdee_kcal`` describe what happens *during* day
  ``i``, computed using state ``i``'s weight.
- State ``i + 1``'s weight is state ``i``'s weight plus the mass
  change implied by state ``i``'s own energy balance.

The final state (index ``config.days``) is therefore a genuinely
useful "where things stand now" snapshot -- its energy figures show
what the subject's BMR/TDEE would be at their new weight if the same
plan continued one more day -- rather than a wasted or empty row.
"""

from __future__ import annotations

from datetime import timedelta

from metabosim.domain.person import Person
from metabosim.domain.simulation_state import SimulationState
from metabosim.simulation.config import DailyPlan, SimulationConfig
from metabosim.simulation.stepper import step


class Simulator:
    """Day-by-day body weight simulation engine.

    Parameters
    ----------
    person:
        The subject's starting profile. ``person.weight_kg`` is the
        simulation's baseline weight; every other field
        (sex, age, height, body_fat_percent) is held constant
        throughout the simulation -- body composition dynamics are not
        modeled until Phase 10.
    config:
        Model-selection configuration; see
        ``metabosim.simulation.config.SimulationConfig``.
    daily_plan:
        Either a single ``DailyPlan`` applied identically to every
        simulated day (the common case: "what happens if I sustain
        this diet and activity level for N days"), or a list of
        ``DailyPlan`` objects, one per simulated day, of length
        exactly ``config.days``, for scenarios where intake or
        activity varies day to day.

    Raises
    ------
    ValueError
        If ``daily_plan`` is a list whose length does not equal
        ``config.days``.
    """

    def __init__(
        self,
        person: Person,
        config: SimulationConfig,
        daily_plan: DailyPlan | list[DailyPlan],
    ) -> None:
        self.person = person
        self.config = config

        if isinstance(daily_plan, list):
            if len(daily_plan) != config.days:
                raise ValueError(
                    "When daily_plan is a list, its length "
                    f"({len(daily_plan)}) must equal config.days "
                    f"({config.days})."
                )
            self.daily_plans: list[DailyPlan] = list(daily_plan)
        else:
            self.daily_plans = [daily_plan] * config.days

    def run(self) -> list[SimulationState]:
        """Run the simulation and return the full state history.

        Returns
        -------
        list[SimulationState]
            ``config.days + 1`` states; see module docstring for the
            row convention.
        """
        baseline_weight_kg = self.person.weight_kg
        current_weight_kg = baseline_weight_kg
        states: list[SimulationState] = []

        for day_index in range(self.config.days + 1):
            # The final state (day_index == config.days) has no
            # "next" day to plan for within this simulation, but we
            # still report that day's energetics for continuity --
            # reuse the last configured plan for that purpose. See
            # module docstring's "row convention".
            plan = (
                self.daily_plans[day_index]
                if day_index < self.config.days
                else self.daily_plans[-1]
            )

            state_date = (
                self.config.start_date + timedelta(days=day_index)
                if self.config.start_date is not None
                else None
            )

            state, rate_kg_per_day = step(
                current_weight_kg=current_weight_kg,
                baseline_weight_kg=baseline_weight_kg,
                person_template=self.person,
                day_index=day_index,
                plan=plan,
                config=self.config,
                state_date=state_date,
            )
            states.append(state)

            if day_index < self.config.days:
                current_weight_kg += rate_kg_per_day

        return states
