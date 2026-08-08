"""Unit tests for metabosim.simulation.engine.Simulator."""

from datetime import date, timedelta

import pytest

from metabosim.domain.diet import MacronutrientGrams
from metabosim.domain.person import Person
from metabosim.simulation.config import DailyPlan, SimulationConfig
from metabosim.simulation.engine import Simulator


@pytest.mark.unit
class TestSimulatorRowCount:
    def test_run_produces_days_plus_one_states(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=10)
        states = Simulator(moderate_male_80kg, config, jogging_plan).run()
        assert len(states) == 11

    def test_day_indices_are_sequential_from_zero(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=5)
        states = Simulator(moderate_male_80kg, config, jogging_plan).run()
        assert [s.day_index for s in states] == [0, 1, 2, 3, 4, 5]


@pytest.mark.unit
class TestSimulatorWeightTrajectory:
    def test_day_zero_weight_equals_starting_weight(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=10)
        states = Simulator(moderate_male_80kg, config, jogging_plan).run()
        assert states[0].weight_kg == pytest.approx(80.0)

    def test_surplus_plan_produces_weight_gain_trajectory(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        # jogging_plan (2580 kcal intake) is a caloric surplus relative
        # to this person's TDEE (~2439 kcal) -- weight should rise
        # monotonically.
        config = SimulationConfig(days=30)
        states = Simulator(moderate_male_80kg, config, jogging_plan).run()
        weights = [s.weight_kg for s in states]
        assert weights == sorted(weights)
        assert weights[-1] > weights[0]

    def test_deficit_plan_produces_weight_loss_trajectory(
        self,
        moderate_male_80kg: Person,
        sedentary_maintenance_plan: DailyPlan,
    ) -> None:
        config = SimulationConfig(days=30)
        states = Simulator(moderate_male_80kg, config, sedentary_maintenance_plan).run()
        weights = [s.weight_kg for s in states]
        assert weights == sorted(weights, reverse=True)
        assert weights[-1] < weights[0]

    def test_real_bmr_recompute_shrinks_surplus_over_time(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        # Because BMR is recomputed at each day's updated (heavier)
        # weight, the day-30 energy balance should be smaller in
        # magnitude than the day-0 balance for a sustained surplus --
        # this is the real physiological feedback the simulator
        # provides in place of an approximated gamma constant.
        config = SimulationConfig(days=30)
        states = Simulator(moderate_male_80kg, config, jogging_plan).run()
        day0_balance = states[0].energy_balance_kcal
        day30_balance = states[30].energy_balance_kcal
        assert 0 < day30_balance < day0_balance


@pytest.mark.unit
class TestSimulatorDateHandling:
    def test_dates_none_when_start_date_not_set(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=3)
        states = Simulator(moderate_male_80kg, config, jogging_plan).run()
        assert all(s.date is None for s in states)

    def test_dates_sequential_when_start_date_set(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        start = date(2026, 3, 1)
        config = SimulationConfig(days=3, start_date=start)
        states = Simulator(moderate_male_80kg, config, jogging_plan).run()
        expected = [start + timedelta(days=i) for i in range(4)]
        assert [s.date for s in states] == expected


@pytest.mark.unit
class TestSimulatorSingleVsListDailyPlan:
    def test_single_plan_is_applied_every_day(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=3)
        states = Simulator(moderate_male_80kg, config, jogging_plan).run()
        # Every state's reported intake should be identical, since the
        # same plan is reused for every day.
        intakes = {round(s.energy_intake_kcal, 4) for s in states}
        assert len(intakes) == 1

    def test_list_of_plans_length_mismatch_raises(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=5)
        with pytest.raises(ValueError, match="length"):
            Simulator(moderate_male_80kg, config, [jogging_plan, jogging_plan])

    def test_list_of_varying_plans_produces_varying_intake(
        self, moderate_male_80kg: Person
    ) -> None:
        low = DailyPlan(
            macros=MacronutrientGrams(protein_g=80, carbohydrate_g=100, fat_g=30)
        )
        high = DailyPlan(
            macros=MacronutrientGrams(protein_g=200, carbohydrate_g=400, fat_g=100)
        )
        config = SimulationConfig(days=2)
        states = Simulator(moderate_male_80kg, config, [low, high]).run()
        # states[0] uses `low`, states[1] uses `high` (per the
        # documented row convention); states[2] re-reports the last
        # configured plan (`high`).
        assert states[0].energy_intake_kcal == pytest.approx(low.macros.energy_kcal)
        assert states[1].energy_intake_kcal == pytest.approx(high.macros.energy_kcal)
        assert states[2].energy_intake_kcal == pytest.approx(high.macros.energy_kcal)


@pytest.mark.unit
class TestSimulatorPersonImmutability:
    def test_original_person_object_is_never_mutated(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        original_weight = moderate_male_80kg.weight_kg
        config = SimulationConfig(days=30)
        Simulator(moderate_male_80kg, config, jogging_plan).run()
        assert moderate_male_80kg.weight_kg == original_weight
