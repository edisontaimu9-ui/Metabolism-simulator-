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

Body composition tracking (Phase 10)
---------------------------------------------------------------------
If ``person.body_fat_percent`` is set, the simulator additionally
tracks fat mass and lean mass day by day (populating
``SimulationState.fat_mass_kg`` / ``lean_mass_kg``), seeded from
``person.fat_mass_kg`` (a computed property already available since
Phase 3). If ``person.body_fat_percent`` is ``None``, this simulator
behaves exactly as it did in Phase 9 -- see
``metabosim.simulation.config`` module docstring for the full
rationale and ``metabosim.simulation.stepper`` for the mechanics.

Glycogen tracking (Phase 12)
---------------------------------------------------------------------
If ``initial_glycogen_g`` is provided to the constructor, the
simulator additionally tracks glycogen (and its associated water) day
by day (populating ``SimulationState.glycogen_g`` /
``total_body_water_kg``), independent of whether body composition is
being tracked. ``initial_reference_carbohydrate_intake_g`` seeds the
carbohydrate-oxidation estimate used to drive that tracking; if
omitted, it defaults to the first day's planned carbohydrate intake --
i.e. "assume the subject is already adapted to whatever they are
about to eat on day 0," which produces zero initial transient unless
intake subsequently changes. See
``metabosim.models.macronutrient.glycogen`` and
``metabosim.simulation.stepper`` for the mechanics.
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
        simulation's baseline weight. If ``person.body_fat_percent``
        is set, body composition (fat vs. lean mass) is tracked
        throughout the simulation -- see module docstring; if not
        set, only total weight is tracked (Phase 9 behavior).
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
    initial_glycogen_g:
        The subject's starting glycogen store, in grams, if glycogen
        tracking is desired; ``None`` (default) disables it. See
        module docstring's "Glycogen tracking" section.
    initial_reference_carbohydrate_intake_g:
        The subject's starting carbohydrate-oxidation reference
        level, in grams. Only meaningful when ``initial_glycogen_g``
        is provided; if omitted in that case, defaults to the first
        day's planned carbohydrate intake.

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
        initial_glycogen_g: float | None = None,
        initial_reference_carbohydrate_intake_g: float | None = None,
    ) -> None:
        self.person = person
        self.config = config
        self.initial_glycogen_g = initial_glycogen_g
        self.initial_reference_carbohydrate_intake_g = (
            initial_reference_carbohydrate_intake_g
        )

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

        # Body composition tracking activates iff the starting Person
        # has a known body_fat_percent -- reusing the Person.fat_mass_kg
        # computed property from Phase 3 to seed the initial value.
        current_fat_mass_kg = self.person.fat_mass_kg

        # Glycogen tracking (Phase 12) activates iff initial_glycogen_g
        # was provided. The reference carbohydrate-oxidation estimate
        # defaults to day 0's own planned carbohydrate intake if not
        # explicitly seeded -- see module docstring.
        current_glycogen_g = self.initial_glycogen_g
        current_reference_carbohydrate_intake_g = (
            self.initial_reference_carbohydrate_intake_g
        )
        if (
            current_glycogen_g is not None
            and current_reference_carbohydrate_intake_g is None
        ):
            current_reference_carbohydrate_intake_g = self.daily_plans[
                0
            ].macros.carbohydrate_g

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

            result = step(
                current_weight_kg=current_weight_kg,
                baseline_weight_kg=baseline_weight_kg,
                person_template=self.person,
                day_index=day_index,
                plan=plan,
                config=self.config,
                state_date=state_date,
                current_fat_mass_kg=current_fat_mass_kg,
                current_glycogen_g=current_glycogen_g,
                current_reference_carbohydrate_intake_g=(
                    current_reference_carbohydrate_intake_g
                ),
            )
            states.append(result.state)

            if day_index < self.config.days:
                current_weight_kg += result.mass_change_rate_kg_per_day
                current_fat_mass_kg = result.next_fat_mass_kg
                current_glycogen_g = result.next_glycogen_g
                current_reference_carbohydrate_intake_g = (
                    result.next_reference_carbohydrate_intake_g
                )

        return states
