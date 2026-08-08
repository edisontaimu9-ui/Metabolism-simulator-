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

from metabosim.domain.person import Person
from metabosim.simulation.config import DailyPlan, SimulationConfig
from metabosim.simulation.stepper import step


@pytest.mark.unit
class TestStepReferenceValues:
    def test_full_reference_calculation(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=30)
        state, rate = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
        )
        assert state.bmr_kcal == pytest.approx(1780.0)
        assert state.tdee_kcal == pytest.approx(2438.9)
        assert state.energy_intake_kcal == pytest.approx(2580.0)
        assert state.energy_balance_kcal == pytest.approx(141.1, abs=1e-2)
        assert rate == pytest.approx(141.1 / 7380.0, abs=1e-6)

    def test_state_carries_requested_day_index_and_weight(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=30)
        state, _ = step(
            current_weight_kg=82.5,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=7,
            plan=jogging_plan,
            config=config,
        )
        assert state.day_index == 7
        assert state.weight_kg == pytest.approx(82.5)

    def test_state_date_is_embedded_when_provided(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=30)
        state, _ = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
            state_date=date(2026, 3, 1),
        )
        assert state.date == date(2026, 3, 1)

    def test_state_date_is_none_when_not_provided(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        config = SimulationConfig(days=30)
        state, _ = step(
            current_weight_kg=80.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
        )
        assert state.date is None


@pytest.mark.unit
class TestStepUsesCurrentWeightNotPersonTemplateWeight:
    def test_bmr_reflects_current_weight_kg_argument(
        self, moderate_male_80kg: Person, jogging_plan: DailyPlan
    ) -> None:
        # person_template.weight_kg is 80, but current_weight_kg=100
        # should be what actually drives the BMR calculation.
        config = SimulationConfig(days=30)
        state, _ = step(
            current_weight_kg=100.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=0,
            plan=jogging_plan,
            config=config,
        )
        # Mifflin-St Jeor: 10*100 + 6.25*180 - 5*30 + 5 = 1000+1125-150+5=1980
        assert state.bmr_kcal == pytest.approx(1980.0)

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
        _, rate_a = step(
            current_weight_kg=85.0,
            baseline_weight_kg=80.0,
            person_template=moderate_male_80kg,
            day_index=5,
            plan=jogging_plan,
            config=config,
        )
        _, rate_b = step(
            current_weight_kg=85.0,
            baseline_weight_kg=85.0,
            person_template=moderate_male_80kg,
            day_index=5,
            plan=jogging_plan,
            config=config,
        )
        assert rate_a == rate_b


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
