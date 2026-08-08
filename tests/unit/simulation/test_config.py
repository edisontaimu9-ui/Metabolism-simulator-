"""Unit tests for metabosim.simulation.config."""

from datetime import date

import pytest
from pydantic import ValidationError

from metabosim.domain.diet import MacronutrientGrams
from metabosim.models.activity.met_based import ActivityEntry
from metabosim.simulation.config import (
    DEFAULT_ENERGY_BALANCE_MODEL_ID,
    DailyPlan,
    SimulationConfig,
)


@pytest.mark.unit
class TestDailyPlan:
    def test_minimal_construction(self) -> None:
        macros = MacronutrientGrams(protein_g=100, carbohydrate_g=200, fat_g=60)
        plan = DailyPlan(macros=macros)
        assert plan.macros is macros
        assert plan.activity_entries == []

    def test_with_activity_entries(self) -> None:
        macros = MacronutrientGrams(protein_g=100, carbohydrate_g=200, fat_g=60)
        entries = [ActivityEntry(met=5.0, duration_hours=1.0)]
        plan = DailyPlan(macros=macros, activity_entries=entries)
        assert plan.activity_entries == entries

    def test_extra_fields_forbidden(self) -> None:
        macros = MacronutrientGrams(protein_g=100, carbohydrate_g=200, fat_g=60)
        with pytest.raises(ValidationError):
            DailyPlan(macros=macros, unexpected_field=1)


@pytest.mark.unit
class TestSimulationConfigDefaults:
    def test_default_energy_balance_model_is_tissue_energy_density(self) -> None:
        assert DEFAULT_ENERGY_BALANCE_MODEL_ID == "tissue_energy_density"

    def test_minimal_construction_uses_defaults(self) -> None:
        config = SimulationConfig(days=10)
        assert config.bmr_model_id == "mifflin_st_jeor"
        assert config.tef_model_id == "macronutrient_specific"
        assert config.energy_balance_model_id == "tissue_energy_density"
        assert config.start_date is None

    def test_start_date_can_be_set(self) -> None:
        config = SimulationConfig(days=10, start_date=date(2026, 1, 1))
        assert config.start_date == date(2026, 1, 1)


@pytest.mark.unit
class TestSimulationConfigValidation:
    def test_days_must_be_at_least_one(self) -> None:
        with pytest.raises(ValidationError):
            SimulationConfig(days=0)
        with pytest.raises(ValidationError):
            SimulationConfig(days=-5)

    def test_extra_fields_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            SimulationConfig(days=10, unexpected_field=1)

    def test_unknown_energy_balance_model_id_raises(self) -> None:
        with pytest.raises(KeyError):
            SimulationConfig(days=10, energy_balance_model_id="not_a_real_model")

    def test_feedback_including_energy_balance_model_rejected_eagerly(self) -> None:
        # This is the core safety guarantee: constructing a config
        # with an energy balance model that already includes
        # weight-dependent feedback must fail immediately, not only
        # when the simulation is later run.
        with pytest.raises(ValueError, match="double-count"):
            SimulationConfig(
                days=10, energy_balance_model_id="dynamic_quasi_exponential"
            )

    def test_static_rule_model_is_feedback_free_and_accepted(self) -> None:
        # static_rule also has includes_weight_dependent_feedback=False,
        # so it should be accepted even though it's not the default.
        config = SimulationConfig(days=10, energy_balance_model_id="static_rule")
        assert config.energy_balance_model_id == "static_rule"

    def test_unknown_bmr_model_id_is_not_validated_eagerly(self) -> None:
        # bmr_model_id is only resolved when the simulation actually
        # runs (via calculate_tdee_from_components inside the
        # stepper) -- SimulationConfig itself does not eagerly
        # validate it. This test documents that behavior explicitly
        # rather than leaving it as an untested assumption.
        config = SimulationConfig(days=10, bmr_model_id="not_a_real_model")
        assert config.bmr_model_id == "not_a_real_model"
