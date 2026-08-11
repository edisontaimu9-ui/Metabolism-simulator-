"""Unit tests for metabosim.simulation.stepper.step.

Reference values hand-computed and cross-checked against earlier
phases: BMR 1780.0 (Mifflin-St Jeor, 80kg/180cm/30y male), Activity
400.0 kcal (MET-based, (6-1)*80*1), TEF 258.9 kcal (macronutrient
specific, 150g protein/300g carb/80g fat/30g fiber), intake 2580.0
kcal, TDEE 2438.9 kcal, balance +141.1 kcal, rate = 141.1/7380 (default
tissue energy density) ~= 0.019119 kg/day.
"""

from datetime import date

import pytest

from metabosim.domain.enums import Sex
from metabosim.domain.person import Person
from metabosim.simulation.config import DailyPlan, SimulationConfig
from metabosim.simulation.stepper import step


@pytest.mark.unit
class TestStepReferenceValues:
    def test_full_reference_calculation(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=30)
        result = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
        )
        assert result.state.bmr_kcal == pytest.approx(1780.0)
        assert result.state.tdee_kcal == pytest.approx(2438.9)
        assert result.state.energy_intake_kcal == pytest.approx(2580.0)
        assert result.state.energy_balance_kcal == pytest.approx(141.1, abs=1e-2)
        assert result.mass_change_rate_kg_per_day == pytest.approx(
            141.1 / 7380.0, abs=1e-6
        )

    def test_state_carries_requested_day_index_and_weight(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=30)
        result = step(
            current_weight_kg=82.5,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=7,
            plan=jogging_plan,
            config=config,
        )
        assert result.state.day_index == 7
        assert result.state.weight_kg == pytest.approx(82.5)

    def test_state_date_is_embedded_when_provided(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=30)
        result = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
            state_date=date(2026, 3, 1),
        )
        assert result.state.date == date(2026, 3, 1)

    def test_state_date_is_none_when_not_provided(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=30)
        result = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
        )
        assert result.state.date is None


@pytest.mark.unit
class TestStepUsesCurrentWeightNotPersonTemplateWeight:
    def test_bmr_reflects_current_weight_kg_argument(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        # person_template.weight_kg is 80, but current_weight_kg=100
        # should be what actually drives the BMR calculation.
        config = SimulationConfig(days=30)
        result = step(
            current_weight_kg=100.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
        )
        # Mifflin-St Jeor: 10*100 + 6.25*180 - 5*30 + 5 = 1000+1125-150+5=1980
        assert result.state.bmr_kcal == pytest.approx(1980.0)

    def test_person_template_is_not_mutated(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        original_weight = moderate_male_80kg.weight_kg
        config = SimulationConfig(days=30)
        step(
            current_weight_kg=999.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
        )
        assert moderate_male_80kg.weight_kg == original_weight


@pytest.mark.unit
class TestStepExcessWeightHandling:
    def test_default_model_ignores_excess_weight(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        # tissue_energy_density has no feedback term -- rate should be
        # identical regardless of baseline_weight_kg / accumulated
        # excess weight.
        config = SimulationConfig(days=30)
        result_a = step(
            current_weight_kg=85.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=5,
            plan=jogging_plan,
            config=config,
        )
        result_b = step(
            current_weight_kg=85.0,
            baseline_weight_kg=85.0,
            person_template=moderate_male_80kg,
            day_index=5,
            plan=jogging_plan,
            config=config,
        )
        assert (
            result_a.mass_change_rate_kg_per_day == result_b.mass_change_rate_kg_per_day
        )


@pytest.mark.unit
class TestStepSafetyCheck:
    def test_feedback_including_model_raises_via_manual_bypass(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        # SimulationConfig itself blocks constructing a config with a
        # feedback-including energy_balance_model_id (tested in
        # test_config.py), so to test step()'s own defense-in-depth
        # check in isolation, we must bypass that validation
        # deliberately via model_construct().
        bad_config = SimulationConfig.model_construct(
            days=30,
            bmr_model_id="mifflin_st_jeor",
            tef_model_id="macronutrient_specific",
            energy_balance_model_id="dynamic_quasi_exponential",
            body_composition_model_id="forbes",
            start_date=None,
        )
        with pytest.raises(ValueError, match="double-count"):
            step(
                current_weight_kg=80.0,
                baseline_weight_kg=80.0,
                person_template=moderate_male_80kg,
                day_index=0,
                plan=jogging_plan,
                config=bad_config,
            )


@pytest.mark.unit
class TestStepBodyCompositionTracking:
    """Tests for Phase 10's body composition tracking, activated by
    passing current_fat_mass_kg (not None).
    """

    def test_not_tracking_when_fat_mass_is_none(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=30)
        result = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
            current_fat_mass_kg=None,
        )
        assert result.state.fat_mass_kg is None
        assert result.state.lean_mass_kg is None
        assert result.next_fat_mass_kg is None
        assert result.next_lean_mass_kg is None

    def test_tracking_populates_state_fields(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=30)
        result = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
            current_fat_mass_kg=16.0,
        )
        assert result.state.fat_mass_kg == pytest.approx(16.0)
        assert result.state.lean_mass_kg == pytest.approx(64.0)

    def test_next_fat_and_lean_mass_sum_to_next_weight(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=30)
        result = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
            current_fat_mass_kg=16.0,
        )
        assert result.next_fat_mass_kg is not None
        assert result.next_lean_mass_kg is not None
        next_weight = 80.0 + result.mass_change_rate_kg_per_day
        assert result.next_fat_mass_kg + result.next_lean_mass_kg == pytest.approx(
            next_weight, abs=1e-9
        )

    def test_bmr_uses_updated_body_fat_percent_not_static_initial_value(
        self, jogging_plan: DailyPlan
    ) -> None:
        # Katch-McArdle BMR depends on lean mass, which depends on
        # body_fat_percent. A person_template with a deliberately
        # stale/wrong body_fat_percent should NOT affect the result
        # when tracking is active -- current_fat_mass_kg (together
        # with current_weight_kg) must be what drives the day's BMR,
        # not whatever body_fat_percent happens to be set on
        # person_template.
        stale_person = Person(
            sex=Sex.MALE,
            age_years=30,
            height_cm=180,
            weight_kg=80,
            body_fat_percent=50.0,  # deliberately stale/wrong
        )
        fresh_person = Person(
            sex=Sex.MALE,
            age_years=30,
            height_cm=180,
            weight_kg=80,
            body_fat_percent=20.0,  # the "true" current value
        )
        config = SimulationConfig(days=30, bmr_model_id="katch_mcardle")

        # current_fat_mass_kg = 16.0 corresponds to 20% body fat at
        # 80 kg -- i.e. fresh_person's actual composition, not
        # stale_person's stated 50%.
        result_from_stale_template = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=stale_person,
            day_index=0,
            plan=jogging_plan,
            config=config,
            current_fat_mass_kg=16.0,
        )
        result_from_fresh_template = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=fresh_person,
            day_index=0,
            plan=jogging_plan,
            config=config,
            current_fat_mass_kg=16.0,
        )
        assert result_from_stale_template.state.bmr_kcal == pytest.approx(
            result_from_fresh_template.state.bmr_kcal
        )

    def test_low_fat_mass_produces_higher_ffm_fraction_partition(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=30)
        low_fat_result = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
            current_fat_mass_kg=2.0,
        )
        high_fat_result = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
            current_fat_mass_kg=60.0,
        )
        assert low_fat_result.next_lean_mass_kg is not None
        assert high_fat_result.next_lean_mass_kg is not None
        low_fat_delta_lean = low_fat_result.next_lean_mass_kg - (80.0 - 2.0)
        high_fat_delta_lean = high_fat_result.next_lean_mass_kg - (80.0 - 60.0)
        # At low current fat mass, a larger share of the day's mass
        # change should be lean; at high fat mass, a smaller share.
        assert low_fat_delta_lean > high_fat_delta_lean

    def test_only_overrides_ffm_fraction_for_tissue_energy_density(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        # static_rule has no ffm_fraction concept at all -- tracking
        # composition must not error out or silently do nothing odd
        # when combined with it; the rate should simply match
        # StaticEnergyBalanceModel's own fixed-density calculation.
        config = SimulationConfig(days=30, energy_balance_model_id="static_rule")
        result = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
            current_fat_mass_kg=16.0,
        )
        # 141.1 / 7716.18 (Wishnofsky density) -- unaffected by ffm_fraction
        assert result.mass_change_rate_kg_per_day == pytest.approx(
            141.1 / 7716.179176470715, abs=1e-6
        )
        # Composition is still tracked/reported and partitioned, even
        # though the *rate* itself didn't use a Forbes-derived density.
        assert result.next_fat_mass_kg is not None
        assert result.next_lean_mass_kg is not None


@pytest.mark.unit
class TestStepAdaptiveThermogenesis:
    """Tests for Phase 11's adaptive thermogenesis wiring."""

    def test_default_model_gives_zero_adjustment(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=30)
        result = step(
            current_weight_kg=72.0,  # 10% below an implied 80kg baseline
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
        )
        assert result.state.adaptive_thermogenesis_kcal == pytest.approx(0.0)
        assert result.state.energy_expenditure_kcal == pytest.approx(
            result.state.tdee_kcal
        )

    def test_proportional_model_reduces_effective_expenditure_at_reduced_weight(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(
            days=30, adaptive_thermogenesis_model_id="proportional"
        )
        result = step(
            current_weight_kg=72.0,  # 10% below baseline
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
        )
        # -0.15 * naive TDEE
        assert result.state.adaptive_thermogenesis_kcal == pytest.approx(
            -0.15 * result.state.tdee_kcal, rel=1e-6
        )
        assert result.state.energy_expenditure_kcal == pytest.approx(
            result.state.tdee_kcal + result.state.adaptive_thermogenesis_kcal
        )
        assert result.state.energy_expenditure_kcal < result.state.tdee_kcal

    def test_proportional_model_increases_effective_expenditure_at_elevated_weight(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(
            days=30, adaptive_thermogenesis_model_id="proportional"
        )
        result = step(
            current_weight_kg=88.0,  # 10% above baseline
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
        )
        assert result.state.adaptive_thermogenesis_kcal > 0.0
        assert result.state.energy_expenditure_kcal > result.state.tdee_kcal

    def test_adaptation_affects_mass_change_rate(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        # At reduced weight, adaptive suppression lowers effective
        # expenditure, which (for the same intake) INCREASES the net
        # energy balance -- i.e. slows further loss / boosts gain,
        # relative to the no-adaptation baseline rate.
        config_none = SimulationConfig(days=30)
        config_proportional = SimulationConfig(
            days=30, adaptive_thermogenesis_model_id="proportional"
        )
        result_none = step(
            current_weight_kg=72.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config_none,
        )
        result_proportional = step(
            current_weight_kg=72.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config_proportional,
        )
        assert (
            result_proportional.mass_change_rate_kg_per_day
            > result_none.mass_change_rate_kg_per_day
        )

    def test_tdee_kcal_stays_naive_while_expenditure_reflects_adaptation(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        # This is the exact relationship SimulationState's docstring
        # has anticipated since Phase 3: tdee_kcal is the "clean"
        # prediction; energy_expenditure_kcal includes adaptation.
        config = SimulationConfig(days=30, adaptive_thermogenesis_model_id="threshold")
        result = step(
            current_weight_kg=72.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
        )
        assert result.state.tdee_kcal != result.state.energy_expenditure_kcal
        assert result.state.energy_expenditure_kcal == pytest.approx(
            result.state.tdee_kcal + result.state.adaptive_thermogenesis_kcal
        )


@pytest.mark.unit
class TestStepGlycogenTracking:
    """Tests for Phase 12's glycogen tracking, activated by passing
    current_glycogen_g (not None) alongside
    current_reference_carbohydrate_intake_g.
    """

    def test_not_tracking_when_glycogen_is_none(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=30)
        result = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
        )
        assert result.state.glycogen_g is None
        assert result.state.total_body_water_kg is None
        assert result.next_glycogen_g is None
        assert result.next_reference_carbohydrate_intake_g is None

    def test_providing_only_one_of_the_pair_raises(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=30)
        with pytest.raises(ValueError, match="must both be provided"):
            step(
                current_weight_kg=80.0,
                baseline_weight_kg=80.0,
                person_template=moderate_male_80kg,
                day_index=0,
                plan=jogging_plan,
                config=config,
                current_glycogen_g=300.0,
                current_reference_carbohydrate_intake_g=None,
            )
        with pytest.raises(ValueError, match="must both be provided"):
            step(
                current_weight_kg=80.0,
                baseline_weight_kg=80.0,
                person_template=moderate_male_80kg,
                day_index=0,
                plan=jogging_plan,
                config=config,
                current_glycogen_g=None,
                current_reference_carbohydrate_intake_g=300.0,
            )

    def test_tracking_populates_state_fields(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=30)
        result = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
            current_glycogen_g=300.0,
            current_reference_carbohydrate_intake_g=300.0,
        )
        assert result.state.glycogen_g == pytest.approx(300.0)
        # 300 * (1+2.7) / 1000 = 1.11
        assert result.state.total_body_water_kg == pytest.approx(1.11)

    def test_matched_intake_and_reference_gives_stable_glycogen(
        self, moderate_male_80kg: Person
    ) -> None:
        from metabosim.domain.diet import MacronutrientGrams

        plan = DailyPlan(
            macros=MacronutrientGrams(
                protein_g=150, carbohydrate_g=300, fat_g=80, fiber_g=30
            ),
            activity_entries=[],
        )
        config = SimulationConfig(days=30)
        result = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=plan,
            config=config,
            current_glycogen_g=250.0,
            current_reference_carbohydrate_intake_g=300.0,
        )
        assert result.next_glycogen_g == pytest.approx(250.0)

    def test_carbohydrate_deficit_reduces_next_glycogen_and_rate(
        self, moderate_male_80kg: Person
    ) -> None:
        from metabosim.domain.diet import MacronutrientGrams

        low_carb_plan = DailyPlan(
            macros=MacronutrientGrams(protein_g=150, carbohydrate_g=20, fat_g=150),
            activity_entries=[],
        )
        config = SimulationConfig(days=30)
        result = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=low_carb_plan,
            config=config,
            current_glycogen_g=300.0,
            current_reference_carbohydrate_intake_g=300.0,
        )
        assert result.next_glycogen_g is not None
        assert result.next_glycogen_g < 300.0
        # The glycogen transient should make the day's total mass
        # change rate MORE negative than the energy-balance-only rate
        # would have been (glycogen depletion adds weight loss).
        assert result.mass_change_rate_kg_per_day < 0.0

    def test_glycogen_transient_is_attributed_to_lean_not_fat(self) -> None:
        from metabosim.domain.diet import MacronutrientGrams

        person = Person(
            sex=Sex.MALE,
            age_years=30,
            height_cm=180,
            weight_kg=80,
            body_fat_percent=20.0,
        )
        low_carb_plan = DailyPlan(
            macros=MacronutrientGrams(protein_g=150, carbohydrate_g=20, fat_g=150),
            activity_entries=[],
        )
        config = SimulationConfig(days=30)
        result = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=person,
            day_index=0,
            plan=low_carb_plan,
            config=config,
            current_fat_mass_kg=16.0,
            current_glycogen_g=300.0,
            current_reference_carbohydrate_intake_g=300.0,
        )
        assert result.next_fat_mass_kg is not None
        assert result.next_lean_mass_kg is not None
        next_weight = 80.0 + result.mass_change_rate_kg_per_day
        assert result.next_fat_mass_kg + result.next_lean_mass_kg == pytest.approx(
            next_weight, abs=1e-9
        )

    def test_glycogen_tracking_works_without_composition_tracking(
        self, moderate_male_80kg: Person
    ) -> None:
        # moderate_male_80kg has no body_fat_percent -- composition
        # tracking is off, but glycogen tracking should still work
        # independently.
        from metabosim.domain.diet import MacronutrientGrams

        low_carb_plan = DailyPlan(
            macros=MacronutrientGrams(protein_g=150, carbohydrate_g=20, fat_g=150),
            activity_entries=[],
        )
        config = SimulationConfig(days=30)
        result = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=low_carb_plan,
            config=config,
            current_glycogen_g=300.0,
            current_reference_carbohydrate_intake_g=300.0,
        )
        assert result.next_fat_mass_kg is None
        assert result.next_lean_mass_kg is None
        assert result.next_glycogen_g is not None
        assert result.next_glycogen_g < 300.0
