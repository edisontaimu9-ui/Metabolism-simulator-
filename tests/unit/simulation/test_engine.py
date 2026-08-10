"""Unit tests for metabosim.simulation.engine.Simulator."""

from datetime import date, timedelta

import pytest

from metabosim.domain.diet import MacronutrientGrams
from metabosim.domain.enums import Sex
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


@pytest.mark.unit
class TestSimulatorBodyCompositionTracking:
    """Tests for Phase 10's body composition tracking at the
    Simulator level -- activated automatically when the starting
    Person has body_fat_percent set.
    """

    def test_no_body_fat_percent_leaves_composition_untracked(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        # moderate_male_80kg has no body_fat_percent -- Phase 9
        # fallback behavior.
        config = SimulationConfig(days=10)
        states = Simulator(moderate_male_80kg, config, jogging_plan).run()
        assert all(s.fat_mass_kg is None for s in states)
        assert all(s.lean_mass_kg is None for s in states)

    def test_body_fat_percent_activates_tracking(self, jogging_plan: DailyPlan) -> None:
        person = Person(
            sex=Sex.MALE,
            age_years=30,
            height_cm=180,
            weight_kg=80,
            body_fat_percent=20.0,
        )
        config = SimulationConfig(days=10)
        states = Simulator(person, config, jogging_plan).run()
        assert all(s.fat_mass_kg is not None for s in states)
        assert all(s.lean_mass_kg is not None for s in states)

    def test_day_zero_composition_matches_person_fat_mass_kg(
        self, jogging_plan: DailyPlan
    ) -> None:
        person = Person(
            sex=Sex.MALE,
            age_years=30,
            height_cm=180,
            weight_kg=80,
            body_fat_percent=20.0,
        )
        config = SimulationConfig(days=10)
        states = Simulator(person, config, jogging_plan).run()
        assert states[0].fat_mass_kg == pytest.approx(person.fat_mass_kg)
        assert states[0].lean_mass_kg == pytest.approx(person.lean_mass_kg)

    def test_composition_sums_to_weight_at_every_state(
        self, jogging_plan: DailyPlan
    ) -> None:
        person = Person(
            sex=Sex.MALE,
            age_years=30,
            height_cm=180,
            weight_kg=80,
            body_fat_percent=20.0,
        )
        config = SimulationConfig(days=30)
        states = Simulator(person, config, jogging_plan).run()
        for state in states:
            assert state.fat_mass_kg + state.lean_mass_kg == pytest.approx(
                state.weight_kg, abs=1e-6
            )

    def test_fat_and_lean_mass_both_increase_under_sustained_surplus(
        self, jogging_plan: DailyPlan
    ) -> None:
        person = Person(
            sex=Sex.MALE,
            age_years=30,
            height_cm=180,
            weight_kg=80,
            body_fat_percent=20.0,
        )
        config = SimulationConfig(days=30)
        states = Simulator(person, config, jogging_plan).run()
        assert states[-1].fat_mass_kg > states[0].fat_mass_kg
        assert states[-1].lean_mass_kg > states[0].lean_mass_kg

    def test_leaner_starting_person_gains_relatively_more_lean_mass(
        self, jogging_plan: DailyPlan
    ) -> None:
        # Forbes' theory's core qualitative prediction: at the same
        # total weight gain, a leaner person (lower body_fat_percent)
        # should see a higher proportion of that gain go to lean mass
        # than a fatter person would.
        lean_person = Person(
            sex=Sex.MALE,
            age_years=30,
            height_cm=180,
            weight_kg=80,
            body_fat_percent=8.0,
        )
        fat_person = Person(
            sex=Sex.MALE,
            age_years=30,
            height_cm=180,
            weight_kg=80,
            body_fat_percent=35.0,
        )
        config = SimulationConfig(days=30)

        lean_states = Simulator(lean_person, config, jogging_plan).run()
        fat_states = Simulator(fat_person, config, jogging_plan).run()

        lean_person_lean_gain = (
            lean_states[-1].lean_mass_kg - lean_states[0].lean_mass_kg
        )
        lean_person_total_gain = lean_states[-1].weight_kg - lean_states[0].weight_kg
        fat_person_lean_gain = fat_states[-1].lean_mass_kg - fat_states[0].lean_mass_kg
        fat_person_total_gain = fat_states[-1].weight_kg - fat_states[0].weight_kg

        lean_person_lean_fraction = lean_person_lean_gain / lean_person_total_gain
        fat_person_lean_fraction = fat_person_lean_gain / fat_person_total_gain

        assert lean_person_lean_fraction > fat_person_lean_fraction

    def test_unknown_body_composition_model_id_raises_eagerly(self) -> None:
        with pytest.raises(KeyError):
            SimulationConfig(days=10, body_composition_model_id="not_a_real_model")


@pytest.mark.unit
class TestSimulatorAdaptiveThermogenesis:
    """End-to-end tests for Phase 11's adaptive thermogenesis, run
    through the full Simulator rather than just the isolated stepper.
    """

    def test_no_adaptation_is_the_default_over_a_full_simulation(
        self, moderate_male_80kg: Person, sedentary_maintenance_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=60)
        states = Simulator(moderate_male_80kg, config, sedentary_maintenance_plan).run()
        assert all(s.adaptive_thermogenesis_kcal == pytest.approx(0.0) for s in states)
        assert all(
            s.energy_expenditure_kcal == pytest.approx(s.tdee_kcal) for s in states
        )

    def test_proportional_adaptation_slows_weight_loss_over_a_full_simulation(
        self, sedentary_maintenance_plan: DailyPlan
    ) -> None:
        # Same person, same deficit-inducing plan, same duration --
        # the only difference is whether adaptive thermogenesis is
        # modeled. Real physiology (and this project's Phase 11
        # citations) predicts LESS total weight loss when adaptation
        # is modeled, since suppressed expenditure partially offsets
        # the deficit as weight drops.
        person = Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=100)
        config_none = SimulationConfig(days=100)
        config_proportional = SimulationConfig(
            days=100, adaptive_thermogenesis_model_id="proportional"
        )

        states_none = Simulator(person, config_none, sedentary_maintenance_plan).run()
        states_proportional = Simulator(
            person, config_proportional, sedentary_maintenance_plan
        ).run()

        loss_without_adaptation = states_none[0].weight_kg - states_none[-1].weight_kg
        loss_with_adaptation = (
            states_proportional[0].weight_kg - states_proportional[-1].weight_kg
        )
        assert loss_with_adaptation < loss_without_adaptation

    def test_adaptive_thermogenesis_kcal_grows_in_magnitude_as_weight_drops(
        self, sedentary_maintenance_plan: DailyPlan
    ) -> None:
        person = Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=100)
        config = SimulationConfig(
            days=100, adaptive_thermogenesis_model_id="proportional"
        )
        states = Simulator(person, config, sedentary_maintenance_plan).run()
        # As weight drops further from baseline over the simulation,
        # the (negative) adaptation term should grow in magnitude.
        early_adaptation = abs(states[10].adaptive_thermogenesis_kcal)
        late_adaptation = abs(states[90].adaptive_thermogenesis_kcal)
        assert late_adaptation > early_adaptation

    def test_threshold_model_gives_flat_fraction_once_activated(
        self, sedentary_maintenance_plan: DailyPlan
    ) -> None:
        # Once the 10% threshold is crossed, the adjustment must stay
        # pinned at exactly -15% of that day's own naive TDEE,
        # regardless of how much further weight drops beyond the
        # threshold -- unlike the proportional model, whose fraction
        # keeps growing in magnitude with further weight loss.
        person = Person(sex=Sex.MALE, age_years=30, height_cm=180, weight_kg=100)
        config = SimulationConfig(days=150, adaptive_thermogenesis_model_id="threshold")
        states = Simulator(person, config, sedentary_maintenance_plan).run()

        activated_states = [s for s in states if s.adaptive_thermogenesis_kcal != 0.0]
        assert len(activated_states) > 0
        for s in activated_states:
            ratio = s.adaptive_thermogenesis_kcal / s.tdee_kcal
            assert ratio == pytest.approx(-0.15, abs=1e-6)
